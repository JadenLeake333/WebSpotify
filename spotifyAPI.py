import base64
import requests
from urllib.parse import urlencode

class spotify_api():
    def __init__(self,client,secret,scope,redirect_uri):
        self.client = client
        self.secret = secret
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.token = None
        self.headers = None

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

    def get_playlist(self,playlistid,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/playlists/%s'%playlistid, headers=self.headers)
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

    def get_next_playlist(self,next_page,token): # Requires calling the "get_playlist()" function first to retrieve "next"
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

    def get_user_playlists(self,token):
        self.headers = {
        'Authorization': 'Bearer %s'%token,
            }
        response = requests.get('https://api.spotify.com/v1/me/playlists',headers=self.headers)
        return response.json()
    