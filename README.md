🎵 Spotify Playlist Manager

A Python-based Spotify Playlist Manager that allows users to modify their playlists (public & private) using Spotify's API. Built using Spotipy, OAuth 2.0, and Flask, this project is deployed on Render for seamless web access.

🚀 Features

✅ Add songs to a playlist

✅ Create & modify public/private playlists

✅ OAuth 2.0 authentication for secure access

✅ Token refresh mechanism for uninterrupted access


🛠 Tech Stack

Python 3.x 🐍

Spotipy (Spotify API wrapper) 🎶

OAuth 2.0 Authentication 🔑

Render (Deployment) 🚀


📌 Setup & Installation

1️⃣ Clone the Repository

``` git clone https://github.com/yourusername/spotify-playlist-manager.git```

```cd spotify-playlist-manager ```

2️⃣ Install Dependencies

``` pip install -r requirements.txt```

3️⃣ Set Up Environment Variables

Create a .env file and add your Spotify API credentials:

``` SPOTIFY_CLIENT_ID=your_client_id ```

``` SPOTIFY_CLIENT_SECRET=your_client_secret```

``` SPOTIFY_REDIRECT_URI=http://localhost:5000/callback```

Spotify Refresh Token for new token

```SPOTIFY_REFRESH_TOKEN=your Spotify_Refresh_Token```

```TELEGRAM_BOT_TOKEN=your_telegram_bot_token```

Get your Client ID & Secret from the {Spotify Developer Dashboard}.


4️⃣ Run the Project Locally

```python3 playlist_manager.py```














