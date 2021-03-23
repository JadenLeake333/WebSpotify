from flask import Flask, request, redirect, url_for, render_template
from spotifyAPI import spotify_api
import os
from parseJSON import parse_json
from dotenv import load_dotenv



app = Flask(__name__)
load_dotenv() #Get env variables

client_id = os.getenv("CLIENT")
client_secret = os.getenv("SECRET")
redirect_uri = 'http://localhost:5000/callback' #https://Web-Spotify.jadenleake.repl.co/callback

spotify = spotify_api(
    client_id, client_secret,
    'user-top-read,playlist-modify-public,playlist-read-private,playlist-modify-private,playlist-read-collaborative',
    redirect_uri)
authorize = spotify.get_url()


@app.route('/')
def starter():
    #url_for('static', filename='style.css')
    return render_template("login.html", url=authorize)


@app.route('/callback')
def main():
    #find_code = request.url.find("?code=")
    exchange_code = request.args.get('code')  # Parse the code from callback url
    try:
        if spotify.get_access_token(exchange_code)['error'] == 'invalid_grant':
            return redirect(url_for('starter'))
    except:
        pass

    song_data = spotify.get_user_tracks()
    try:
        if song_data['error']['status'] == 401:
            return redirect(url_for('starter'))
    except:
        pass

    return render_template('callback.html',data=song_data['items'])

@app.route('/makeplaylist')
def make_playlist():
    user = spotify.get_user()
    user_id = user['id']
    top_playlist = spotify.make_playlist(
        user_id, "Top Songs", "Here are your most listened to songs!")
    songs = request.args.get('s')
    spotify.fill_playlist(top_playlist['id'], songs)
    return "Your playlist has been made! <a href='/playlistdata?playlist=%s'>Click here to view it!</a>" % top_playlist[
        'uri']


@app.route('/search')
def make_search():
    search = request.args.get("s")
    if search == '':
        search = "none"
    get_tracks = spotify.search_track(search)
    return render_template('search.html',data=get_tracks['tracks']['items'])


@app.route('/features')
def audio_features(feat=None, img=None, artist=None, name=None):
    song_id = request.args.get("feat")
    img = request.args.get("img")
    artist = request.args.get("artist")
    name = request.args.get('name')

    song_features = spotify.get_analysis(song_id)

    dance = float(song_features['danceability']) * 100
    energy = float(song_features['energy']) * 100
    instrumentalness = float(song_features['instrumentalness']) * 100
    valence = float(song_features['valence']) * 100
    #print(dance,song_features['danceability'],energy,song_features['energy'],instrumentalness,song_features['instrumentalness'])
    return render_template('songanalysis.html',
                           img=img,
                           artist=artist,
                           name=name,
                           dance=dance,
                           energy=energy,
                           instrumentalness=instrumentalness,
                           valence=valence)


@app.route('/playlistdata')
def playlists():
    playlist = request.args.get("playlist")
    playlist_id = playlist[17::]
    playlist_data = spotify.get_playlist(playlist_id)
    next_playlist = parse_json.extract_values(playlist_data, 'next')
    num_tracks = playlist_data['tracks']['total']

    try:
        if playlist_data['error']['status'] == 401:
            return redirect(url_for('starter'))
    except:
        pass
    playlist_name = playlist_data['name']

    temp_id, song_names, song_img, song_artist, song_id = [], [], [], [], []  # Get images, names, artists and song ids of playlist
    for songs in playlist_data['tracks']['items']:
        song_names.append(songs['track']['name'])
        song_img.append(songs['track']['album']['images'][0]['url'])
        song_artist.append(songs['track']['artists'][0]['name'])
        song_id.append(songs['track']['id'])

    song_analysis = spotify.get_analysis(song_id)
    dance, energy, instrumentalness, valence = [], [], [], []  # Get audio analysis of songs
    for analysis in song_analysis['audio_features']:
        dance.append(analysis['danceability'])
        energy.append(analysis['energy'])
        instrumentalness.append(analysis['instrumentalness'])
        valence.append(analysis['valence'])

    duration_ms = 0
    while next_playlist[0] != None:  # If the playlist is larger than 100 songs this will be able to get each "page"
        next_page = spotify.get_next_playlist(next_playlist[0])
        temp_id.clear()
        for songs in next_page['items']:
            song_names.append(songs['track']['name'])
            song_img.append(songs['track']['album']['images'][0]['url'])
            song_artist.append(songs['track']['artists'][0]['name'])
            song_id.append(songs['track']['id'])
            temp_id.append(songs['track']['id'])
            duration_ms += int(songs['track']['duration_ms'])

        song_analysis = spotify.get_analysis(temp_id)
        for analysis in song_analysis['audio_features']:
            dance.append(analysis['danceability'])
            energy.append(analysis['energy'])
            instrumentalness.append(analysis['instrumentalness'])
            valence.append(analysis['valence'])

        next_playlist = parse_json.extract_values(next_page, 'next')

    dance_avg = (sum(dance) / len(dance)) * 100
    energy_avg = (sum(energy) / len(energy)) * 100
    instrumentalness_avg = (sum(instrumentalness) /
                            len(instrumentalness)) * 100
    valence_avg = (sum(valence) / len(valence)) * 100

    table = "<div class='row'>"
    for idx, names in enumerate(song_names):
        if names.find("'"):
          names = names.replace("'","")
        table += "<div class='col child'><tr><figure><td><a href='/features?feat=%s&img=%s&artist=%s&name=%s'><img src='%s' width='250' height='250'></a></td><figcaption><td>%s</td><br><td>%s</td></figcaption></figure></tr></div>" % (
            song_id[idx], song_img[idx], song_artist[idx], names,
            song_img[idx], song_artist[idx], names)
    table += "</div>"

    return '''
    <html>
        <head>
            <title>Spotify Data</title>
            <link href="static/bootstrap.min.css" rel="stylesheet">
            <link href="static/cover.css" rel="stylesheet">
        </head>
        <body class="d-flex h-100 justify-content-center text-center text-white bg-dark">
            <div>
                <header class="mb-auto">
                    <nav class="nav nav-masthead justify-content-center float-md-end">
                        <a class="nav-link fs-2" href='/search'>Search</a>
                        <a class="nav-link fs-2" href='/viewplaylists'>My playlists</a>
                    </nav>
                </header>
                <div class="input-group mb-3">
                    <input type="text" id='search' placeholder="Paste the link of a song or playlist here! Or just search a name!" class="form-control" aria-describedby="button-addon2">
                    <button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button>
                </div>        
                <h1>%s</h1>
                <h2>Tracks: %s</h2>
                <div class='container overflow-auto cont' style='width: 100%%; height: 65%%;'>   
                    %s
                </div>
                <h1>Danceability</h1>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: %.2f%%" aria-valuemin="0" aria-valuemax="1">%.2f%%</div>
                </div>
                <br>
                <h1>Energy</h1>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width:%.2f%%" aria-valuemin="0" aria-valuemax="100">%.2f%%</div>      
                </div>
                <br>
                <h1>Instrumentalness</h1>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: %.2f%%" aria-valuemin="0" aria-valuemax="100">%.2f%%</div>
                </div>
                <h1>Valence</h1>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: %.2f%%" aria-valuemin="0" aria-valuemax="100">%.2f%%</div>
                </div>
            </div>
                <script type='text/javascript' src='static/search.js'></script>
        </body>
    </html>
    ''' % (playlist_name, num_tracks, table, dance_avg, dance_avg, energy_avg,
           energy_avg, instrumentalness_avg, instrumentalness_avg, valence_avg,
           valence_avg)


@app.route('/searchtrack')
def tracks():
    track = request.args.get('track')
    track_id = track[14::]
    track_data = spotify.search_trackid(track_id)

    try:
        if track_data['error']['status'] == 401:
            return redirect(url_for('starter'))
    except:
        pass
    print(track_data)
    name = track_data['name']
    img = track_data['album']['images'][0]['url']
    artist = track_data['artists'][0]['name']
    if name.find("'"):
      name = name.replace("'","")
    return redirect(
        url_for('audio_features',
                feat=track_id,
                img=img,
                artist=artist,
                name=name))


@app.route('/viewplaylists')
def view_playlists():
    user_playlists = spotify.get_user_playlists()
    
    return render_template('viewplaylists.html',data=user_playlists['items'])

@app.route('/recommend')
def recommend_songs():
    return render_template('recommend.html')

@app.route('/recommendedsongs')
def display_recommended(dance=None, energy=None, instrumental=None, valence=None):
    dance = int(request.args.get("dance")) / 100
    energy = int(request.args.get("energy")) / 100
    instrumental = int(request.args.get("instrumental")) / 100
    valence = int(request.args.get('valence')) / 100

    song_data = spotify.get_user_tracks()
    song_artist_data = spotify.get_user_artists()
    song_artist, song_id, song_genre = [], [], []

    for songs in song_data['items']:
        song_artist.append(songs['artists'][0]['id'])
        song_id.append(songs['id'])

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

    recommended = spotify.get_user_recommendations(song_artist,song_id,genres,dance=dance,energy=energy,instrumental=instrumental,valence=valence)
    print(recommended)
    return 'hey'




if __name__ == "__main__":
    app.run() #host='0.0.0.0'
