import os
import json
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-modify-public playlist-modify-private"
)

# Manually authenticate and get token
token_info = sp_oauth.get_access_token()
access_token = token_info["access_token"]
refresh_token = token_info["refresh_token"]

# Save token to a file
with open("spotify_token.json", "w") as token_file:
    json.dump(token_info, token_file)

print("✅ Token saved! Upload 'spotify_token.json' to your server.")
