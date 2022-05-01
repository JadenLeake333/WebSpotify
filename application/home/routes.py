import os
from . import demo as guest_account
from .. import navbar, helper_functions, parseJSON, auth, spotifyAPI
from dotenv import load_dotenv
from flask import request, redirect, url_for, render_template, session, Blueprint, make_response

spotify = auth.authorize()
nav, search = navbar.create_navbar()

# Blueprint Configuration
routes_bp = Blueprint(
    'routes_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@routes_bp.route('/')
def login():
    return render_template("login.html", url=spotify.get_url())

@routes_bp.route('/logout')
def logout():
  session.pop('username', None)
  session.pop('code', None)
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
    song_data = spotify.make_call("me/top/tracks", session['code'])
    username = spotify.make_call("me", session['code'])['display_name']
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
    next_page = spotify.get_next(next_playlist[0], session['code'])

    for item in next_page['items']:
      user_playlists['items'].append(item)

    next_playlist = parseJSON.parse_json.extract_values(next_page, 'next')

  return render_template(
    'viewplaylists.html',
    data                = user_playlists,
    navbar              = nav,
    searchbar           = search
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
