import os
import navbar

from dotenv import load_dotenv
from parseJSON import parse_json
from spotifyAPI import spotify_api
from helper_functions import *
# from youtube_api import YoutubeDataApi
from flask import Flask, request, redirect, url_for, render_template, session

app = Flask(__name__)
load_dotenv() #Get env variables

client_id = os.getenv("CLIENT")
client_secret = os.getenv("SECRET")
app.secret_key = os.getenv("SESSIONSECRET")
# youtubeAPI = YoutubeDataApi(os.getenv("UTUBEAPIKEY"))
redirect_uri = 'http://localhost:5000/callback' #https://WebSpotify.jadenleake.repl.co/callback
permissions = 'user-top-read,playlist-modify-public,playlist-read-private,playlist-modify-private,playlist-read-collaborative'

spotify = spotify_api(
    client_id, 
    client_secret,
    permissions,
    redirect_uri
  )
    
authorize = spotify.get_url()
nav = navbar.create_navbar()

@app.route('/')
def login():
    return render_template("login.html", url=authorize)

@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect(url_for('login'))

@app.route('/home')
def home():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  song_data = spotify.get_user_tracks(session['code'])
  username = spotify.get_user(session['code'])['display_name']

  return render_template(
    'callback.html',
    data=song_data['items'], # Using Jinja template engine
    name=username,
    navbar=nav
  )

@app.route('/callback')
def main():
  exchange_code = request.args.get('code')  # Parse the code from callback url
  session['code'] = spotify.get_access_token(exchange_code)

  return redirect(url_for('home'))

@app.route('/makeplaylist')
def make_playlist():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  user = spotify.get_user(session['code'])
  user_id = user['id']

  top_playlist = spotify.make_playlist(
      user_id, 
      "Top Songs", 
      "Here are your most listened to songs!", 
      session['code']
    )

  songs = request.args.get('s')

  spotify.fill_playlist(
    top_playlist['id'], 
    songs, 
    session['code']
  )

  return "Your playlist has been made! <a href='/playlistdata?playlist=%s'>Click here to view it!</a>" % top_playlist['uri']

@app.route('/search')
def make_search():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  search = request.args.get("s")

  if search == '':
      search = "none"

  get_tracks = spotify.search_track(search,session['code'])

  return render_template(
    'search.html',
    data=get_tracks['tracks']['items'],
    navbar=nav
  )

@app.route('/features/<track_id>')
def audio_features(track_id):

  if 'code' not in session.keys():
    return redirect(url_for('login'))

  track_info = spotify.search_trackid(track_id,session['code'])
  song_features = spotify.get_analysis(track_id,session['code'])
  
  if check_error(song_features) or check_error(track_info):
    return render_template("error.html", navbar=nav)

  else:
    return render_template(
      'songanalysis.html',
      album_id         = track_info['album']['id'],
      img              = track_info['album']['images'][0]['url'],
      artist           = track_info['album']['artists'][0]['name'],
      name             = track_info['name'],
      dance            = round(float(song_features['danceability']) * 100),
      energy           = round(float(song_features['energy']) * 100),
      instrumentalness = round(float(song_features['instrumentalness']) * 100),
      valence          = round(float(song_features['valence']) * 100),
      navbar           = nav
    )

@app.route('/playlists')
def view_playlists():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  user_playlists = spotify.make_call("me/playlists", session['code'],  {"limit" : 50})
  next_playlist = parse_json.extract_values(user_playlists, 'next')

  while next_playlist[0]:
    next_page = spotify.get_next(next_playlist[0],session['code'])

    for item in next_page['items']:
      user_playlists['items'].append(item)

    next_playlist = parse_json.extract_values(next_page, 'next')

  return render_template(
    'viewplaylists.html',
    data=user_playlists['items'],
    navbar=nav
  )

@app.route('/content/<content_type>/<content_id>')
def playlists(content_type,content_id):
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  content_data = spotify.make_call(f"{content_type}/{content_id}",session['code'])

  if check_error(content_data):
    return render_template("error.html", navbar=nav)

  tracks = spotify.track_list(content_data, content_type, session['code'])

  if len(tracks['song_names']) == 0:
    return render_template('playlistdata.html', 
      name = "No songs to display! Try adding songs to the playlist!",
      playlistLength = 0,
      display_analysis = "none",
      table = "",
      dance = 0,
      energy = 0,
      instrumental = 0,
      valence = 0,
      navbar = nav,
    )

  # next_playlist = parse_json.extract_values(content_data, 'next')
  num_tracks = len(tracks['song_names'])

  playlist_name = content_data['name']

  temp_id, dance, energy, instrumentalness, valence = [], [], [], [], []
  analysis = spotify.song_analysis(tracks['song_id'], session['code'])
  # song_analysis = spotify.make_call("audio-features",session['code'],{"ids" : ",".join(tracks['song_id'])})

  # if len(song_analysis.get('audio_features')) > 0:
  #   dance, instrumentalness, valence, energy = spotify.parse_song_analysis(song_analysis)

  # while next_playlist[0]:  # If the playlist is larger than 100 songs this will be able to get each "page"
  #     next_page = spotify.get_next_playlist(next_playlist[0],session['code'])
  #     temp_id.clear()

  #     for songs in next_page['items']:
  #       if songs.get('track').get('name'):
  #         song_names.append(songs['track']['name'])
  #         song_img.append(songs['track']['album']['images'][0]['url'])
  #         song_artist.append(songs['track']['artists'][0]['name'])
  #         song_id.append(songs['track']['id'])
  #         temp_id.append(songs['track']['id'])
  #         duration_ms += int(songs['track']['duration_ms'])
  #       else:
  #         song_names.append(songs['track']['name'])
  #         song_img.append("static/assets/unknown.png")
  #         song_artist.append("Unknown")
  #         song_id.append("")
  #         temp_id.append("")

  #     song_analysis = spotify.get_analysis(temp_id,session['code'])
  
  #     if song_analysis.get('audio_features')[0]:
  #       for analysis in song_analysis['audio_features']:
  #           dance.append(analysis['danceability'])
  #           energy.append(analysis['energy'])
  #           instrumentalness.append(analysis['instrumentalness'])
  #           valence.append(analysis['valence'])

  #     next_playlist = parse_json.extract_values(next_page, 'next')

  if len(analysis['danceability']) > 0:
    dance_avg = round((sum(analysis['danceability']) / len(analysis['danceability'])) * 100)
    energy_avg = round((sum(analysis['energy']) / len(analysis['energy'])) * 100)
    instrumentalness_avg = round((sum(analysis['instrumentalness']) / len(analysis['instrumentalness'])) * 100)
    valence_avg = round((sum(analysis['valence']) / len(analysis['valence'])) * 100)
  else:
    dance_avg, energy_avg, instrumentalness_avg, valence_avg = 0,0,0,0

  table = "<div class='row'>"
  for idx, names in enumerate(tracks['song_names']):
      # if names.find("'"):
      #   names = names.replace("'","")
      if tracks['song_id'][idx] == "":
        table += f"<div class='enlarge col'><figure><img src='../../static/assets/unknown.png' width='250' height='250'><figcaption><h3>{tracks['song_artist'][idx]}<br>{names}</h3></figcaption></figure></div>"
      else:
        table += f"<div class='enlarge col'><figure><a href='/features/{tracks['song_id'][idx]}'><img src='{tracks['song_img'][idx]}' width='250' height='250'></a><figcaption><h3>{tracks['song_artist'][idx]}<br>{names}</h3></figcaption></figure></div>"
  table += "</div>"

  return render_template('playlistdata.html', 
    name = playlist_name,
    playlistLength = num_tracks,
    table = table,
    dance = dance_avg,
    energy = energy_avg,
    instrumental = instrumentalness_avg,
    valence = valence_avg,
    navbar = nav,
  )

@app.route('/searchtrack')
def tracks():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  track = request.args.get('track')
  print(track)
  track_id = track.split(":")[2]
  track_data = spotify.make_call(f"tracks/{track_id}",session['code'])

  if check_error(content_data):
    return render_template("error.html", navbar=nav)

  # Regex this
  if name.find("'"):
    name = name.replace("'","")

  return redirect(
    url_for(
      'audio_features',
      feat    = track_id,
      name    = track_data['name'],
      artist  = track_data['artists'][0]['name'],
      img     = track_data['album']['images'][0]['url'],
    )
  )

@app.route('/recommend')
def recommend_songs():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  return render_template(
    'recommend.html',
    navbar=nav
  )

# @app.route('/converttospotify', methods=['GET','POST'])
# def convert_playlist():

#   if 'code' not in session.keys():
#       return redirect(url_for('login'))

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
#       navbar=nav)
#   else:
#     return render_template(
#       'youtubespotify.html',
#       navbar=nav)

@app.route('/recommendedsongs')
def display_recommended(dance=None, energy=None, instrumental=None, valence=None):
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  dance = int(request.args.get("dance")) / 100
  energy = int(request.args.get("energy")) / 100
  instrumental = int(request.args.get("instrumental")) / 100
  valence = int(request.args.get('valence')) / 100

  song_data = spotify.get_user_tracks(session['code'])
  song_artist_data = spotify.get_user_artists(session['code'])
  song_artist, song_id, song_genre = [], [], []

  song_artist = [song['artists'][0]['id'] for song in song_data['items']]
  song_id = [song['id'] for song in song_data['items']]
  # for songs in song_data['items']:
  #     song_artist.append(songs['artists'][0]['id'])
  #     song_id.append(songs['id'])

  for songs in song_artist_data['items']: 
      song_genre.append(songs['genres'][0])
      '''  
      try: # This needs a fix once fully working
      song_artist = song_artist[0:4]
      song_id = song_id[0:4]
      song_genre = song_genre[0:4]
  except:'''

  song_artist = song_artist[0]
  song_id = song_id[0]
  song_genre = song_genre[0]

  '''
  artists=",".join(song_artist)
  tracks=','.join(song_id)
  genres=','.join(song_genre)
  '''
  genres = song_genre.replace(" ","%20")

  recommended = spotify.get_user_recommendations(
    song_artist,
    song_id,
    genres,
    session['code'],
    dance=dance,
    energy=energy,
    instrumental=instrumental,
    valence=valence,
    navbar=nav
  )

  return render_template('recommendedplaylist.html', data=recommended['tracks'])

@app.route('/recommendplaylist')
def make_recommended_playlist():
  if 'code' not in session.keys():
    return redirect(url_for('login'))

  tracks = request.args.get('tracks')

  user = spotify.get_user(session['code'])
  user_id = user['id']

  recommended_playlist = spotify.make_playlist(
    user_id, 
    "Recommended Songs", 
    "Here are your recommended songs!",
    session['code']
  )

  spotify.fill_playlist(
    recommended_playlist['id'], 
    tracks,session['code']
  )

  return "Playlist has been made, check your spotify! You can close this tab."

if __name__ == "__main__":
    app.run(host='0.0.0.0') #host='0.0.0.0'
