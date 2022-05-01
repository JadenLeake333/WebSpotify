import os
from . import spotifyAPI
from flask import session
from dotenv import load_dotenv

load_dotenv() #Get env variables

def authorize():
    client_id = os.getenv("CLIENT")
    client_secret = os.getenv("SECRET")
    callback_url = os.getenv("CALLBACK")
    redirect_uri = callback_url
    permissions = 'user-top-read,playlist-modify-public,playlist-read-private,playlist-modify-private,playlist-read-collaborative'

    spotify = spotifyAPI.spotify_api(
        client_id, 
        client_secret,
        permissions,
        redirect_uri
    )
        
    return spotify