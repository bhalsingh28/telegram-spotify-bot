import requests
import os
from dotenv import load_dotenv
from spotify_auth import get_access_token
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ACCESS_TOKEN = get_access_token()

def refresh_access_token():
    global ACCESS_TOKEN
    ACCESS_TOKEN = get_access_token()

def check_access_token(response):
    if response.status_code == 401:
        refresh_access_token()
        return False
    return True

def get_playlists():
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if not check_access_token(response):
        return get_playlists()
    
    if response.status_code == 200:
        playlists = response.json()["items"]
        return {idx + 1: (p["name"], p["id"]) for idx, p in enumerate(playlists)}
    else:
        return None
    
def create_playlist(name):
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    json_data = {"name": name, "public": False}
    
    response = requests.post(url, headers=headers, json=json_data)
    return response.status_code == 201
    
async def create_new_playlist(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /create <playlist name>")
        return
    
    playlist_name = " ".join(context.args)
    if create_playlist(playlist_name):
        await update.message.reply_text(f"✅ Playlist '{playlist_name}' created successfully!")
    else:
        await update.message.reply_text("❌ Error creating playlist.")

def search_tracks(song_query):
    url = f"https://api.spotify.com/v1/search?q={song_query}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if not check_access_token(response):
        return search_tracks(song_query)
    
    if response.status_code == 200 and response.json()["tracks"]["items"]:
        return response.json()["tracks"]["items"][0]["id"]
    else:
        return None

def add_tracks_to_playlist(playlist_id, track_ids):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    json_data = {"uris": [f"spotify:track:{track_id}" for track_id in track_ids]}
    
    response = requests.post(url, headers=headers, json=json_data)
    if not check_access_token(response):
        return add_tracks_to_playlist(playlist_id, track_ids)
    
    return response.status_code == 201

# async def start(update: Update, context: CallbackContext):
#     await update.message.reply_text("🎵 Welcome to Spotify Bot!\nUse /add <song> to add a song.\n /playlists to see your playlists.\n /create <name> to create new playlist.")

async def start(update: Update, context: CallbackContext):
    message = (
        "🎵 *Welcome to Spotify Bot!* 🎵\n\n"
        "Use the commands below:\n"
        "➡️ `/add <song>` - Add a song to a playlist\n"
        "➡️ `/playlists` - View your playlists\n"
        "➡️ `/create <name>` - Create a new playlist\n\n"
        "Enjoy your music! 🎶"
    )
    
    await update.message.reply_text(message, parse_mode="Markdown")



async def list_playlists(update: Update, context: CallbackContext):
    playlists = get_playlists()
    
    if playlists:
        msg = "📂 Your Playlists:\n"
        for idx, (name, _) in playlists.items():
            msg += f"{idx}. {name}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ Error fetching playlists.")

async def add_song(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /add <song name>")
        return
    
    song_queries = " ".join(context.args).split(";")
    found_tracks = {}
    
    for song_query in song_queries:
        track_id = search_tracks(song_query.strip())
        if track_id:
            found_tracks[song_query.strip()] = track_id
    
    if not found_tracks:
        await update.message.reply_text("❌ No songs found.")
        return
    
    msg = "🎵 Songs found:\n"
    for song in found_tracks.keys():
        msg += f"- {song}\n"
    msg += "\n✅ Reply with 'yes' to add them or 'no' to cancel."
    
    await update.message.reply_text(msg)
    context.user_data["track_ids"] = list(found_tracks.values())

async def confirm_add(update: Update, context: CallbackContext):
    if "track_ids" not in context.user_data:
        return
    
    response = update.message.text.lower()
    if response == "yes":
        playlists = get_playlists()
        if not playlists:
            await update.message.reply_text("❌ Error fetching playlists.")
            return
        
        msg = "📂 Choose a playlist by index:\n"
        for idx, (name, _) in playlists.items():
            msg += f"{idx}. {name}\n"
        await update.message.reply_text(msg)
        
        context.user_data["playlists"] = playlists
    else:
        await update.message.reply_text("❌ Song addition cancelled.")
        context.user_data.pop("track_ids", None)

async def select_playlist(update: Update, context: CallbackContext):
    if "track_ids" not in context.user_data:
        return
    
    try:
        playlist_index = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")
        return
    
    playlists = context.user_data["playlists"]
    playlist_id = playlists.get(playlist_index, (None, None))[1]
    
    if not playlist_id:
        await update.message.reply_text("❌ Invalid playlist selection.")
        return
    
    track_ids = context.user_data.pop("track_ids")
    
    if add_tracks_to_playlist(playlist_id, track_ids):
        await update.message.reply_text("✅ Songs added successfully!")
    else:
        await update.message.reply_text("❌ Error adding songs.")

async def handle_text(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if text in ["yes", "no"]:
        await confirm_add(update, context)
    else:
        await select_playlist(update, context)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("playlists", list_playlists))
    application.add_handler(CommandHandler("add", add_song))
    application.add_handler(CommandHandler("create", create_new_playlist))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()

if __name__ == "__main__":
    main()
