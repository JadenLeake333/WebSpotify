import base64
import requests
from helper_functions import *
from parseJSON import parse_json
from urllib.parse import urlencode

class spotify_api():
    def __init__(self,client,secret,scope,redirect_uri):
        self.client = client
        self.secret = secret
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.headers = None
        self.endpoint = "https://api.spotify.com/v1/"

    def get_url(self):
        provider_url = "https://accounts.spotify.com/authorize"
        params = urlencode({
            'client_id': '%s'%self.client,
            'scope': '%s'%self.scope,
            'redirect_uri': '%s'%self.redirect_uri,
            'response_type': 'code'
        })
        urlx = provider_url + '?' + params
        return urlx

    def get_access_token(self,code):
        # Use code to retrieve access code from Spotify API
        codes = self.client+":"+self.secret
        encode = codes.encode('ascii')
        head = base64.b64encode(encode) # Client and secret codes need to be base64 encoded and passed to API

        headers = {
            'Authorization': 'Basic %s'%head.decode('ascii'),
        }   

        data = {
            'grant_type': 'authorization_code',
            'code': '%s'%code,
            'redirect_uri': '%s'%self.redirect_uri
        }
        
        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        return response.json()['access_token'] #Return access code

    def client_credentials(self):
        codes = self.client+":"+self.secret
        encode = codes.encode('ascii')
        head = base64.b64encode(encode) # Client and secret codes need to be base64 encoded and passed to API

        headers = {
            'Authorization': 'Basic %s'%head.decode('ascii'),
        } 

        data = {
            'grant_type': 'client_credentials'
        }

        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        print(response.json())
        return response.json()['access_token']

    def make_call(self,target,token,queries = None):
        self.headers = {
            'Authorization': 'Bearer %s'%token,
        }
        query_string = "?"
        if queries:
            for q in queries.items():
                query_string += f"{q[0]}={q[1]}"
        response = requests.get(f'{self.endpoint}{target}{query_string if query_string != "?" else ""}', headers=self.headers)
        return response.json()

    def track_list(self,data,content_type,token):
        song_items = {
            "song_names" : [],
            "song_img" : [],
            "song_artist" : [], 
            "song_id" : [],
            "total_duration" : 0
        }

        if content_type == "playlists":
            next_playlist = parse_json.extract_values(data, 'next')
            for tracks in data['tracks']['items']:
                if tracks.get('track').get('id'):
                    song_items["song_names"].append(tracks['track']['name'])
                    song_items["song_img"].append(tracks['track']['album']['images'][0]['url'])
                    song_items["song_artist"].append(tracks['track']['artists'][0]['name'])
                    song_items["song_id"].append(tracks['track']['id'])
                    song_items["total_duration"] += (tracks['track']['duration_ms'])
                else:
                    song_items["song_names"].append(tracks['track']['name'])
                    song_items["song_img"].append("../static/assets/unknown.png")
                    song_items["song_artist"].append("Unknown")
                    song_items["song_id"].append("")

           
            while next_playlist[0]:
                next_page = self.get_next(next_playlist[0],token)
                for tracks in next_page['items']:
                    if tracks.get('track').get('id'):
                        song_items["song_names"].append(tracks['track']['name'])
                        song_items["song_img"].append(tracks['track']['album']['images'][0]['url'])
                        song_items["song_artist"].append(tracks['track']['artists'][0]['name'])
                        song_items["song_id"].append(tracks['track']['id'])
                        song_items["total_duration"] += (tracks['track']['duration_ms'])
                    else:
                        song_items["song_names"].append(tracks['track']['name'])
                        song_items["song_img"].append("../static/assets/unknown.png")
                        song_items["song_artist"].append("Unknown")
                        song_items["song_id"].append("")
                
                next_playlist = parse_json.extract_values(next_page, 'next')

        if content_type == "albums":
            for tracks in data['tracks']['items']:
                song_items["song_names"].append(tracks['name'])
                song_items["song_img"].append(data['images'][0]['url'])
                song_items["song_artist"].append(tracks['artists'][0]['name'])
                song_items["song_id"].append(tracks['id'])
                song_items["total_duration"] += tracks['duration_ms']
        return song_items
    
    def song_analysis(self,track_ids,token):
        song_stats = {
            "danceability" : [],
            "instrumentalness" : [],
            "energy" : [],
            "valence" : []
        }
        ids = split_list(track_ids,100) # From helper_functions
        for id in ids:
            analysis = self.make_call("audio-features", token, {"ids" : ",".join(id)})
            dance, instrumental, valence, energy = self.parse_song_analysis(analysis)
            song_stats['danceability'] += dance
            song_stats['instrumentalness'] += instrumental
            song_stats['valence'] += valence
            song_stats['energy'] += energy
        return song_stats

    def parse_song_analysis(self, data : dict) -> dict:
        danceability = [analysis['danceability'] for analysis in data['audio_features']]
        instrumentalness = [analysis['instrumentalness'] for analysis in data['audio_features']]
        valence = [analysis['valence'] for analysis in data['audio_features']]
        energy = [analysis['energy'] for analysis in data['audio_features']]
        return danceability, instrumentalness, valence, energy

    def get_user_artists(self,token):
        # Obtain user's (who confirmed website) top artists
        response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=self.headers)
        return response.json()

    def get_user_tracks(self,token):
        # Precondition: A unique string access code, passed by Spotify endpoint
        # Obtain user's (who confirmed website) top tracks
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=self.headers)
        return response.json()
    
    def get_genre_seeds(self,token):
        # Precondition: A unique string access code, passed by Spotify endpoint
        # Obtain user's (who confirmed website) top tracks
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers=self.headers)
        return response.json()

    def get_user_recommendations(self,artist,tracks,genres,token,**kwargs):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/recommendations?seed_artists=%s&seed_tracks=%s&seed_genres=%s&target_danceability=%s&target_energy=%s&target_instrumentalness=%s&target_valence=%s'%(artist,tracks,genres,kwargs['dance'],kwargs['energy'],kwargs['instrumental'],kwargs['valence']),headers=self.headers) 
        return response.json()

    def get_analysis(self,id,token):
        # Precondition: A unique string access code, passed by Spotify endpoint and a unqiue string belonging to each spotify track
        # Obtain Spotify's track analysis (Danceability mainly)
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        if type(id) != list:
            response = requests.get('https://api.spotify.com/v1/audio-features/%s'%id,headers=self.headers)
            return response.json()
        else:
           ids = ','.join(id)
           response = requests.get('https://api.spotify.com/v1/audio-features/?ids=%s'%ids,headers=self.headers)
           return response.json()

    def get_artist(self,artist,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/search?q=%s&type=artist'%artist,headers=self.headers)
        return response.json()

    def search_artist(self,artist,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/search?q=%s&type=artist'%artist,headers=self.headers)
        return response.json()

    def get_playlist(self,playlist_id,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/playlists/%s'%playlist_id, headers=self.headers)
        return response.json()

    def get_album(self,album_id,token):
        self.headers = {
            'Authorization': 'Bearer %s'%token,
        }
        response = requests.get('https://api.spotify.com/v1/albums/%s'%album_id, headers=self.headers)
        return response.json()

    def get_recommendations(self,genres,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/recommendations?seed_genres=%s'%genres,headers=self.headers)
        return response.json()

    def search_track(self,track,token):
        # Precondition: A unique string access code, passed by Spotify endpoint
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/search?q=%s&type=track'%track,headers=self.headers)
        return response.json()

    def search_trackid(self,trackid,token):
        # Precondition: A unique string access code, passed by Spotify endpoint
        #Can take multiple tracks, csv
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/tracks/%s'%trackid,headers=self.headers)
        return response.json()

    def get_next(self,next_page,token): # Requires calling the "get_playlist()" function first to retrieve "next"
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get(next_page,headers=self.headers)
        return response.json()

    def make_playlist(self,id,name,desc,token):
        #User id, Playlist name and description
        self.headers = {
        'Authorization': 'Bearer %s'%token,
        "Content-Type":"application/json"
            }

        playlist_data = '{"name":"%s","description":"%s"}' %(name,desc)
        
        response = requests.post('https://api.spotify.com/v1/users/%s/playlists'%(id),headers=self.headers,data=playlist_data)
        return response.json()

    def get_user(self,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/me',headers=self.headers)
        return response.json()

    def fill_playlist(self,id,uris,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        if type(uris) == list:
          uris = ",".join(uris)
        response = requests.post("https://api.spotify.com/v1/playlists/%s/tracks?uris=%s"%(id,uris),headers=self.headers)
        return response.json()

    def get_user_playlists(self,limit,token):
        self.headers = {
        'Authorization': f'Bearer {token}',
            }
        response = requests.get(f'https://api.spotify.com/v1/me/playlists?limit={limit}',headers=self.headers)
        return response.json()
    