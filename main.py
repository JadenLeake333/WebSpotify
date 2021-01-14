from flask import Flask, request, redirect, url_for, render_template
from spotifyAPI import spotify_api
import requests
from parseJSON import parse_json

app = Flask(__name__)

client_id = '26c35b7190da459584f5534423c51888'
client_secret = 'a812b20459834130ae10039ac7a9264b'
redirect_uri = 'http://localhost:5000/callback'

spotify = spotify_api(client_id,client_secret,'user-top-read,playlist-modify-public,playlist-read-private,playlist-modify-private,playlist-read-collaborative',redirect_uri)
authorize = spotify.get_url()

@app.route('/')
def starter():
    #url_for('static', filename='style.css')
    return render_template("login.html", url=authorize)

@app.route('/callback')
def main():
    #find_code = request.url.find("?code=")
    exchange_code = request.args.get('code') # Parse the code from callback url
    try:
        if spotify.get_access_token(exchange_code)['error'] == 'invalid_grant':
            return redirect(url_for('starter'))
    except:
        pass
    artist_data = spotify.get_user_artists()
    artist_names = parse_json.extract_values(artist_data,'name')

    artist_table = "<table><tr><th>Artist</th></tr>"
    for idx,names in enumerate(artist_names):
        artist_table += "<tr><td>%s</td></tr>"%(names)
    artist_table += "</table>"

    song_data = spotify.get_user_tracks()
    song_names,song_links,song_uris = [],[],[]

    for obj in song_data['items']:
        song_names.append(obj['name'])
        song_links.append(obj['external_urls']['spotify'])
        song_uris.append(obj['uri'])

    song_table = "<table><tr><th>Song</th></tr>"
    for idx,names in enumerate(song_names):
        song_table += "<tr><td><a href='%s' target='_blank'>%s</a></td></tr>"%(song_links[idx],names)
    song_table += "</table>"
    
    return '''
    <html>
        <head>
            <title>Spotify Data</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                rel="stylesheet" 
                integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                crossorigin="anonymous">
        </head>
        <body>
        <div>
            <a href='/viewplaylists'>Click here to see your playlists</a>
        </div>
        <div>
            <h1>Enter a track name or <a href='https://community.spotify.com/t5/Spotify-Answers/What-s-a-Spotify-URI/ta-p/919201'>spotify playlist uri</a> here!</h1>
            <div class="input-group mb-3">
                <input type="text" id='search' class="form-control" aria-describedby="button-addon2">
                <button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button>
            </div>        
        </div>
        <div>
            %s
        </div>
        <div>
            %s
        </div>
            <script type='text/javascript' src='static/search.js'></script>
        </body>
    </html>
''' %(artist_table,song_table)

@app.route('/topartists')

def top_artists():
    artist_data = spotify.get_user_artists()
    
    try:
        if artist_data['error']['status'] == 401:
            return redirect(url_for('starter'))
    except:
        pass
    artist_names = parse_json.extract_values(artist_data,'name')
    artist_popluraity = parse_json.extract_values(artist_data,'popularity')
    artist_followers = parse_json.extract_values(artist_data,'total')

    table = "<table><tr><th>Artist</th><th>Popularity</th><th>Followers</th></tr>"
    for idx,names in enumerate(artist_names):
        table += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(names,artist_popluraity[idx],artist_followers[idx])
    table += "</table>"
    return '''
    <html>
    <head>
        <title>Spotify Data</title>
        <link rel="stylesheet" href='/static/style.css'>
    </head>
    <body>
    <div>
        <a href='/topartists'>Click here to see your top artists</a>
        <a href='/topsongs'>Click here to see your top songs</a>
        <a href='/search'>Click here to search</a>
        <a href='/viewplaylists'>Click here to see your playlists</a>
    </div>
    <div>
        <h1>Here are your top artists</h1>
        %s
    </div>
    </body>
    </html>
    ''' %table

@app.route('/topsongs')

def top_songs():
    song_data = spotify.get_user_tracks()
    try:
        if song_data['error']['status'] == 401:
            return redirect(url_for('starter'))
    except:
        pass
    song_names,song_links,song_uris = [],[],[]

    for obj in song_data['items']:
        song_names.append(obj['name'])
        song_links.append(obj['external_urls']['spotify'])
        song_uris.append(obj['uri'])
    songs_csv = ','.join(song_uris)
    table = "<table><tr><th>Artist</th></tr>"
    for idx,names in enumerate(song_names):
        table += "<tr><td><a href='%s' target='_blank'>%s</a></td></tr>"%(song_links[idx],names)
    table += "</table>"
    return '''
    <html>
    <head>
        <title>Spotify Data</title>
        <link rel="stylesheet" href='/static/style.css'>
    </head>
    <body>
    <div>
        <a href='/topartists'>Click here to see your top artists</a>
        <a href='/topsongs'>Click here to see your top songs</a>
        <a href='/search'>Click here to search</a>
        <a href='/viewplaylists'>Click here to see your playlists</a>
    </div>
    <div>
        <h1>Here are your top songs</h1>
        %s
    </div>
    <a href="/makeplaylist?s=%s" target='_blank'>Click here to make a playlist</a>
    </body>
    </html>
    ''' %(table,songs_csv)


@app.route('/makeplaylist')
def make_playlist():
    user = spotify.get_user()
    user_id = user['id']
    top_playlist = spotify.make_playlist(user_id,"Top Songs","Here are your most listened to songs!")
    songs = request.args.get('s')
    spotify.fill_playlist(top_playlist['id'],songs)
    return "Your playlist has been made! <a href='/playlistdata?playlist=%s'>Click here to view it!</a>" %top_playlist['uri']

@app.route('/search')
def make_search():
    search = request.args.get("s")
    get_tracks = spotify.search_track(search)
    song_names,song_img,song_artist,song_preview,song_id = [],[],[],[],[]

    for songs in get_tracks['tracks']['items']:
        song_names.append(songs['name'])
        song_img.append(songs['album']['images'][0]['url'])
        song_artist.append(songs['artists'][0]['name'])
        song_preview.append(songs['preview_url'])
        song_id.append(songs['id'])

    table = "<table><tr><th></th><th>Artist</th><th>Song Name</th><th>Preview</th></tr>"
    for idx,names in enumerate(song_names):
        table += "<tr><td><a href='/features?feat=%s&img=%s&artist=%s&name=%s'><img src='%s' width='250' height='250'></a></td><td>%s</td><td>%s</td><td><audio controls src='%s'></td></tr>"%(song_id[idx],song_img[idx],song_artist[idx],names,song_img[idx],song_artist[idx],names,song_preview[idx])
    table += "</table>"
    return '''
    <html>
        <head>
            <title>Spotify Data</title>
            <link rel="stylesheet" href='/static/style.css'>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                  rel="stylesheet" 
                  integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                  crossorigin="anonymous">
        </head>
        <body>
        <div>
            <div>
                <a href='/topartists'>Click here to see your top artists</a>
                <a href='/topsongs'>Click here to see your top songs</a>
                <a href='/search'>Click here to search</a>
                <a href='/viewplaylists'>Click here to see your playlists</a>
            </div>
            <h1>Enter a track name or <a href='https://community.spotify.com/t5/Spotify-Answers/What-s-a-Spotify-URI/ta-p/919201'>spotify playlist uri</a> here!</h1>
            <div class="input-group mb-3">
                <input type="text" id='search' class="form-control" aria-describedby="button-addon2">
                <button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button>
            </div>        
        </div>
        <div>
            %s
        </div>
            <script type='text/javascript' src='static/search.js'></script>
        </body>
    </html>
    '''%table

@app.route('/features')
def audio_features(feat=None,img=None,artist=None,name=None):
    song_id = request.args.get("feat")
    img = request.args.get("img")
    artist = request.args.get("artist")
    name = request.args.get('name')

    song_features = spotify.get_analysis(song_id)

    dance = float(song_features['danceability'])*100
    energy = float(song_features['energy'])*100
    instrumentalness = float(song_features['instrumentalness'])*100
    print(dance,song_features['danceability'],energy,song_features['energy'],instrumentalness,song_features['instrumentalness'])
    return render_template('songanalysis.html',img=img,artist=artist,name=name,dance=dance,energy=energy,instrumentalness=instrumentalness)

@app.route('/playlistdata')
def playlists():
    playlist = request.args.get("playlist")
    playlist_id = playlist[17::]
    playlist_data = spotify.get_playlist(playlist_id)
    try:
        if playlist_data['error']['status'] == 401:
            return redirect(url_for('starter'))
    except:
        pass
    playlist_name = playlist_data['name']

    song_names,song_img,song_artist,song_id = [],[],[],[] # Get images, names, artists and song ids of playlist
    for songs in playlist_data['tracks']['items']:
        song_names.append(songs['track']['name'])
        song_img.append(songs['track']['album']['images'][0]['url'])
        song_artist.append(songs['track']['artists'][0]['name'])
        song_id.append(songs['track']['id'])

    song_analysis = spotify.get_analysis(song_id)
    dance, energy, instrumentalness = [],[],[] # Get audio analysis of songs
    for analysis in song_analysis['audio_features']:
        dance.append(analysis['danceability'])
        energy.append(analysis['energy'])
        instrumentalness.append(analysis['instrumentalness'])
    
    dance_avg = (sum(dance) / len(dance)) *100
    energy_avg = (sum(energy) / len(energy)) *100
    instrumentalness_avg = (sum(instrumentalness) / len(instrumentalness)) *100

    table = "<div class='row'>"
    for idx,names in enumerate(song_names):
        table += "<div class='col child'><tr><figure><td><a href='/features?feat=%s&img=%s&artist=%s&name=%s'><img src='%s' width='250' height='250'></a></td><figcaption><td>%s</td><br><td>%s</td></figcaption></figure></tr></div>"%(song_id[idx],song_img[idx],song_artist[idx],names,song_img[idx],song_artist[idx],names)
    table += "</div>"
    return '''
    <html>
        <head>
            <title>Spotify Data</title>
            <link rel="stylesheet" href='/static/style.css'>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
		    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js" integrity="sha384-ygbV9kiqUc6oa4msXn9868pTtWMgiQaeYH7/t7LECLbyPA2x65Kgf80OJFdroafW" crossorigin="anonymous"></script>
        </head>
        <body>
        <div>
            <div>
                <a href='/topartists'>Click here to see your top artists</a>
                <a href='/topsongs'>Click here to see your top songs</a>
                <a href='/search'>Click here to search</a>
                <a href='/viewplaylists'>Click here to see your playlists</a>
            </div>
            <h1>Enter a track name or <a href='https://community.spotify.com/t5/Spotify-Answers/What-s-a-Spotify-URI/ta-p/919201'>spotify playlist uri</a> here!</h1>
            <div class="input-group mb-3">
                <input type="text" id='search' class="form-control" aria-describedby="button-addon2">
                <button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button>
            </div>        
        </div>
        <h1>%s</h1>
        <div class='container overflow-auto cont' style='width: 100%%; height: 32%%;'>   
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
            <script type='text/javascript' src='static/search.js'></script>
        </body>
    </html>
    '''%(playlist_name,table,dance_avg,dance_avg,energy_avg,energy_avg,instrumentalness_avg,instrumentalness_avg)

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

    return redirect(url_for('audio_features',feat=track_id,img=img,artist=artist,name=name))

@app.route('/viewplaylists')
def view_playlists():
    user_playlists = spotify.get_user_playlists()
    img,names,ids = [],[],[]
    for playlists in user_playlists['items']:
        try:
            img.append(playlists['images'][0]['url'])
        except:
            img.append('https://www.pngkey.com/png/detail/113-1138845_question-mark-inside-square-question-mark-icon-white.png')
        names.append(playlists['name'])
        ids.append(playlists['uri'])

    table = "<div class='row'>"
    for idx in range(len(names)):
        table += "<div class='col' style='margin: 10px;'><figure><a href='/playlistdata?playlist=%s'><img src='%s' height='300px' width='300px'></a><figcaption>%s</figcaption></figure></div>"%(ids[idx],img[idx],names[idx])
    table += '</div>'
    return '''
    <html>
        <head>
            <title>Spotify Data</title>
            <link rel="stylesheet" href='/static/style.css'>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
		    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js" integrity="sha384-ygbV9kiqUc6oa4msXn9868pTtWMgiQaeYH7/t7LECLbyPA2x65Kgf80OJFdroafW" crossorigin="anonymous"></script>
        </head>
        <body>
        <div>
            <div>
                <a href='/topartists'>Click here to see your top artists</a>
                <a href='/topsongs'>Click here to see your top songs</a>
                <a href='/search'>Click here to search</a>
                <a href='/viewplaylists'>Click here to see your playlists</a>
            </div>
            <h1>Enter a track name or <a href='https://community.spotify.com/t5/Spotify-Answers/What-s-a-Spotify-URI/ta-p/919201'>spotify playlist uri</a> here!</h1>
            <div class="input-group mb-3">
                <input type="text" id='search' class="form-control" aria-describedby="button-addon2">
                <button class="btn btn-outline-secondary" type="button" id="button-addon2" onclick="makeSearch()">Search</button>
            </div>        
        </div>
            %s
            <script type='text/javascript' src='static/search.js'></script>
        </body>
    </html>
    '''%(table)

if __name__ == "__main__":
    app.run()