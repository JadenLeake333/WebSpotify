import os
from .. import navbar, helper_functions, parseJSON, auth, spotifyAPI
from dotenv import load_dotenv
from flask import request, redirect, url_for, render_template, session, Blueprint, make_response

spotify = spotifyAPI.spotify_api()
nav, search = navbar.create_navbar()

# Blueprint Configuration
analytics_bp = Blueprint(
    'analytics_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@analytics_bp.errorhandler(404)
def not_found_error(error):
    return make_response(
        render_template('error.html', navbar=navbar, searchbar=search, error=404), 
        404
    )

@analytics_bp.errorhandler(500)
def internal_error(error):
    return make_response(
        render_template('error.html', navbar=navbar, searchbar=search, error=500),
        500
    )

# Given a track id, display analytics about the song including values like "danceability" and "valence"
@analytics_bp.route('/features/<track_id>')
def audio_features(track_id):
    if 'code' not in session.keys():
        return redirect(url_for('routes_bp.login'))

    try:
        track_info = spotify.make_call(f"tracks/{track_id}", session['code'])
        song_features = spotify.song_analysis([track_id], session['code'])
    except:
        return make_response(
            render_template("error.html", error=404, navbar=nav, searchbar=search),
            404)

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

# Display songs from playlists or albums
@analytics_bp.route('/content/<content_type>/<content_id>')
def playlists(content_type,content_id):
  if 'code' not in session.keys():
    return redirect(url_for('routes_bp.login'))

  content_data = spotify.make_call(f"{content_type}/{content_id}",session['code'])

  if helper_functions.check_error(content_data):
    return make_response(
            render_template("error.html", error=404, navbar=nav, searchbar=search),
            404)

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
