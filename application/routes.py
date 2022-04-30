import os
from . import demo as guest_account
from . import navbar, helper_functions, parseJSON, spotifyAPI
from dotenv import load_dotenv
# from helper_functions import * # check_error, pitch_class_conversion, ms_time_conversion
# from youtube_api import YoutubeDataApi
from flask import request, redirect, url_for, render_template, session, Blueprint, make_response

load_dotenv() #Get env variables

client_id = os.getenv("CLIENT")
client_secret = os.getenv("SECRET")
callback_url = os.getenv("CALLBACK")
# youtubeAPI = YoutubeDataApi(os.getenv("UTUBEAPIKEY"))
redirect_uri = callback_url
permissions = 'user-top-read,playlist-modify-public,playlist-read-private,playlist-modify-private,playlist-read-collaborative'

spotify = spotifyAPI.spotify_api(
    client_id, 
    client_secret,
    permissions,
    redirect_uri
  )
    
authorize = spotify.get_url()
nav, search = navbar.create_navbar()


# Blueprint Configuration
routes_bp = Blueprint(
    'routes_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@routes_bp.route('/')
def login():
    return render_template("login.html", url=authorize)

@routes_bp.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(
      url_for('routes_bp.login')
    )

@routes_bp.errorhandler(404)
def not_found_error(error):
    return make_response(
        render_template('error.html', navbar=navbar, searchbar=search, error=404), 
        404
      )

@routes_bp.errorhandler(500)
def internal_error(error):
    return make_response(
        render_template('error.html', navbar=navbar, searchbar=search, error=500),
        500
      )

# Home page to display users top listened to songs according to spotify
@routes_bp.route('/home')
def home():
  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  if session['type'] == "demo":
    song_data = guest_account.top
    username = "Guest"
  else:
    song_data = spotify.make_call("me/top/tracks",session['code'])
    username = spotify.make_call("me",session['code'])['display_name']
  return render_template(
    'callback.html',
    data           = song_data, # Using Jinja template engine
    name           = username,
    navbar         = nav,
    searchbar      = search
  )

# Allow user to demo application using hard-coded data
@routes_bp.route('/demo')
def demo():
  demo_user = spotify.client_credentials()
  session['code'] = demo_user
  session['type'] = 'demo'
  return redirect(url_for('routes_bp.home'))

# Initalize access token
@routes_bp.route('/callback')
def main():
  exchange_code = request.args.get('code')  # Parse the code from callback url
  session['code'] = spotify.get_access_token(exchange_code)
  session['type'] = "user"

  return redirect(url_for('routes_bp.home'))

# @routes_bp.route('/makeplaylist')
# def make_playlist():
#   if 'code' not in session.keys():
#     return redirect(url_for('routes_bp.login'))

#   user = spotify.get_user(session['code'])
#   user_id = user['id']

#   top_playlist = spotify.make_playlist(
#       user_id, 
#       "Top Songs", 
#       "Here are your most listened to songs!", 
#       session['code']
#     )

#   songs = request.args.get('s')

#   spotify.fill_playlist(
#     top_playlist['id'], 
#     songs, 
#     session['code']
#   )

#   return "Your playlist has been made! <a href='/playlistdata?playlist=%s'>Click here to view it!</a>" % top_playlist['uri']

# Query API to return search results from given input
@routes_bp.route('/search')
def make_search():
  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  query = request.args.get("s")

  if query == '':
      query = "none"

  get_tracks = spotify.make_call(f'search',session['code'], {"q" : query, "type" : "track", "limit" : 50})
  if helper_functions.check_error(get_tracks):
    return render_template("error.html", error=404, navbar=nav, searchbar=search)

  return render_template( 
    'search.html',
    data        = get_tracks['tracks']['items'],
    navbar      = nav,
    searchbar   = search
  )

# Given a track id, display analytics about the song including values like "danceability" and "valence"
@routes_bp.route('/features/<track_id>')
# @flask_profiler.profile()
def audio_features(track_id):

  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  track_info = spotify.make_call(f"tracks/{track_id}",session['code'])
  song_features = spotify.song_analysis([track_id],session['code'])
  
  if helper_functions.check_error(song_features) or helper_functions.check_error(track_info):
    return render_template("error.html", error=404, navbar=nav, searchbar=search)

  recommended = spotify.make_call("recommendations", session['code'], {"seed_tracks":track_info['id'],"limit": 5})
  translate_key = helper_functions.pitch_class_conversion(song_features['key'][0])
  return render_template(
      'songanalysis.html',
      album_id         = track_info['album']['id'],
      img              = track_info['album']['images'][0]['url'],
      artist           = track_info['album']['artists'][0]['name'],
      name             = track_info['name'],
      preview_url      = track_info['preview_url'],
      dance            = round(float(song_features['danceability'][0]) * 100),
      energy           = round(float(song_features['energy'][0]) * 100),
      instrumentalness = round(float(song_features['instrumentalness'][0]) * 100),
      valence          = round(float(song_features['valence'][0]) * 100),
      tempo            = round(song_features['tempo'][0]),
      time_signature   = song_features['time_signature'][0],
      key              = translate_key,
      recommended      = recommended,
      navbar           = nav,
      searchbar        = search
    )

# Display users playlists 
@routes_bp.route('/playlists')
def view_playlists():
  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  if session['type'] == "demo":
    user_playlists = guest_account.playlists

    return render_template(
    'viewplaylists.html',
    data                = user_playlists,
    navbar              = nav,
    searchbar           = search
  )

  user_playlists = spotify.make_call("me/playlists", session['code'],  {"limit" : 50})
  next_playlist = parseJSON.parse_json.extract_values(user_playlists, 'next')
  
  while next_playlist[0]:
    next_page = spotify.get_next(next_playlist[0],session['code'])

    for item in next_page['items']:
      user_playlists['items'].append(item)

    next_playlist = parseJSON.parse_json.extract_values(next_page, 'next')

  return render_template(
    'viewplaylists.html',
    data                = user_playlists,
    navbar              = nav,
    searchbar           = search
  )

# Display songs from playlists or albums
@routes_bp.route('/content/<content_type>/<content_id>')
def playlists(content_type,content_id):
  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  content_data = spotify.make_call(f"{content_type}/{content_id}",session['code'])

  if helper_functions.check_error(content_data):
    return render_template("error.html", error=404, navbar=nav,searchbar=search)

  tracks = spotify.track_list(content_data, content_type, session['code'])

  if not tracks['song_names']:
    return render_template(
      'playlistdata.html', 
      name              = "No songs to display! Try adding songs to the playlist!",
      Length            = 0,
      duration          = 0,
      display_analysis  = "none",
      table             = "",
      dance             = 0,
      energy            = 0,
      instrumental      = 0,
      valence           = 0,
      navbar            = nav,
      searchbar         = search
    )

  num_tracks = len(tracks['song_names'])

  playlist_name = content_data['name']

  analysis = spotify.song_analysis(tracks['song_id'], session['code'])
  duration = helper_functions.ms_time_conversion(tracks['total_duration'])

  # Songs that do no originate from Spotify do not have analytics. Must be checked for.
  if len(analysis['danceability']) > 0:
    dance_avg = round((sum(analysis['danceability']) / len(analysis['danceability'])) * 100)
    energy_avg = round((sum(analysis['energy']) / len(analysis['energy'])) * 100)
    instrumentalness_avg = round((sum(analysis['instrumentalness']) / len(analysis['instrumentalness'])) * 100)
    valence_avg = round((sum(analysis['valence']) / len(analysis['valence'])) * 100)
  else:
    dance_avg, energy_avg, instrumentalness_avg, valence_avg = 0,0,0,0

  # Create the card for displaying Song Images and Titles
  table = "<div class='row'>"
  for idx, names in enumerate(tracks['song_names']):
      if tracks['song_id'][idx] == "":
        table += f"<div class='enlarge col'><figure><img src='../../static/assets/unknown.png' width='250' height='250'><figcaption><h3>{tracks['song_artist'][idx]}<br>{names}</h3></figcaption></figure></div>"
      else:
        table += f"<div class='enlarge col'><figure><a href='/features/{tracks['song_id'][idx]}'><img src='{tracks['song_img'][idx]}' width='250' height='250'></a><figcaption><h3>{tracks['song_artist'][idx]}<br>{names}</h3></figcaption></figure></div>"
  table += "</div>"
  
  return render_template(
    'playlistdata.html', 
    name           = playlist_name,
    duration       = duration,
    length         = num_tracks,
    table          = table,
    dance          = dance_avg,
    energy         = energy_avg,
    instrumental   = instrumentalness_avg,
    valence        = valence_avg,
    navbar         = nav,
    searchbar      = search
  )

# Allows users to search track by its spotify uri
@routes_bp.route('/searchtrack')
def tracks():
  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  track = request.args.get('track')
  track_id = track.split(":")[2]
  track_data = spotify.make_call(f"tracks/{track_id}",session['code'])

  if helper_functions.check_error(content_data):
    return render_template("error.html", error=404, navbar=nav, searchbar=search)

  return redirect(
    url_for(
      'routes_bp.audio_features',
      feat    = track_id,
      name    = track_data['name'],
      artist  = track_data['artists'][0]['name'],
      img     = track_data['album']['images'][0]['url'],
    )
  )

# @routes_bp.route('/recommend')
# def recommend_songs():
#   if 'code' not in session.keys():
#     return redirect(url_for('routes_bp.login'))

#   return render_template(
#     'recommend.html',
#     navbar          = nav,
#     searchbar       = search
#   )

# @routes_bp.route('/converttospotify', methods=['GET','POST'])
# def convert_playlist():

#   if 'code' not in session.keys():
#       return redirect(url_for('routes_bp.login'))

#   if request.method == "POST":
#     playlistLink = request.form['playlist']
#     playlistID = playlistLink.replace("https://youtube.com/playlist?list=", "")

#     result = youtubeAPI.get_videos_from_playlist_id(playlistID)
#     tracks, add_to_playlist= [], []
    
#     for ids in result:
#       video_by_id = youtubeAPI.get_video_metadata(ids['video_id'])
#       if 'video_title' in video_by_id:
#         title = video_by_id['video_title']

#         title = title[0:title.find("(")]
#         tracks.append(spotify.search_track(title,session['code']))

#     user = spotify.get_user(session['code'])
#     user_id = user['id']

#     youtube_playlist = spotify.make_playlist(
#         user_id, 
#         "YouTube to Spotify", 
#         "YouTube to Spotify", 
#         session['code'])

#     for track in tracks:
#       try:
#         add_to_playlist.append(track['tracks']['items'][0]['uri'])
#       except:
#         continue

#     new_playlist = spotify.fill_playlist(
#       youtube_playlist['id'], 
#       add_to_playlist, 
#       session['code'])

#     return render_template(
#       'youtubespotify.html',
#       navbar=nav,
# searchbar=search)
#   else:
#     return render_template(
#       'youtubespotify.html',
#       navbar=nav,
# searchbar=search)

# @routes_bp.route('/recommendedsongs')
# def display_recommended(dance=None, energy=None, instrumental=None, valence=None):
#   if 'code' not in session.keys():
#     return redirect(url_for('routes_bp.login'))

#   dance = int(request.args.get("dance")) / 100
#   energy = int(request.args.get("energy")) / 100
#   instrumental = int(request.args.get("instrumental")) / 100
#   valence = int(request.args.get('valence')) / 100

#   song_data = spotify.get_user_tracks(session['code'])
#   song_artist_data = spotify.get_user_artists(session['code'])
#   song_artist, song_id, song_genre = [], [], []

#   song_artist = [song['artists'][0]['id'] for song in song_data['items']]
#   song_id = [song['id'] for song in song_data['items']]
#   # for songs in song_data['items']:
#   #     song_artist.append(songs['artists'][0]['id'])
#   #     song_id.append(songs['id'])

#   for songs in song_artist_data['items']: 
#       song_genre.append(songs['genres'][0])
#       '''  
#       try: # This needs a fix once fully working
#       song_artist = song_artist[0:4]
#       song_id = song_id[0:4]
#       song_genre = song_genre[0:4]
#   except:'''

#   song_artist = song_artist[0]
#   song_id = song_id[0]
#   song_genre = song_genre[0]

#   '''
#   artists=",".join(song_artist)
#   tracks=','.join(song_id)
#   genres=','.join(song_genre)
#   '''
#   genres = song_genre.replace(" ","%20")

#   recommended = spotify.get_user_recommendations(
#     song_artist,
#     song_id,
#     genres,
#     session['code'],
#     dance=dance,
#     energy=energy,
#     instrumental=instrumental,
#     valence=valence,
#     navbar=nav,
#     searchbar=search
#   )

#   return render_template('recommendedplaylist.html', data=recommended['tracks'])

# @routes_bp.route('/recommendplaylist')
# def make_recommended_playlist():
#   if 'code' not in session.keys():
#     return redirect(url_for('routes_bp.login'))

#   tracks = request.args.get('tracks')

#   user = spotify.get_user(session['code'])
#   user_id = user['id']

#   recommended_playlist = spotify.make_playlist(
#     user_id, 
#     "Recommended Songs", 
#     "Here are your recommended songs!",
#     session['code']
#   )

#   spotify.fill_playlist(
#     recommended_playlist['id'], 
#     tracks,session['code']
#   )

#   return "Playlist has been made, check your spotify! You can close this tab."

if __name__ == "__main__":
    routes_bp.run(host='0.0.0.0') #host='0.0.0.0'
