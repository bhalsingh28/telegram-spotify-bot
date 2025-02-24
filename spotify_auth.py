import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-modify-public playlist-modify-private"
)

def get_access_token():
    token_info = sp_oauth.get_access_token(as_dict=True)
    return token_info.get("access_token")


