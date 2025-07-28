import subprocess
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import creds
import os
import platform
import subprocess
import shutil
from pathlib import Path

def get_spotify_path():
    system = platform.system()

    if system == "Windows":
        possible_paths = [
            os.path.join(os.getenv("APPDATA"), "Spotify", "Spotify.exe"),
            os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "WindowsApps", "Spotify.exe"),
        ]
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        return shutil.which("Spotify.exe")  # fallback if in PATH

    elif system == "Darwin":  # macOS
        # Default location when installed from dmg
        app_path = "/Applications/Spotify.app/Contents/MacOS/Spotify"
        if os.path.isfile(app_path):
            return app_path
        return shutil.which("spotify")  # if it's in PATH

    elif system == "Linux":
        # Usually just installed system-wide or via snap/flatpak
        return shutil.which("spotify")

    else:
        raise RuntimeError(f"Unsupported OS: {system}")

def launch_spotify():
    spotify_path = get_spotify_path()
    if spotify_path:
        subprocess.Popen([spotify_path])
        print(f"Launching Spotify from: {spotify_path}")
    else:
        print("Spotify not found on this system.")

# Call the function
launch_spotify()


# Launch Spotify app (change the path if necessary)
# Wait for the application to launch
time.sleep(5)

# Load credentials
client_id = creds.client_id
client_secret = creds.client_secret
redirect_uri = creds.redirect_uri

# Add necessary scopes
scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

# Authenticate and get the token
sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)
token_info = sp_oauth.get_cached_token()

if not token_info:
    token_info = sp_oauth.get_access_token()

access_token = token_info['access_token'] if isinstance(token_info, dict) else token_info

# Create Spotify object with the access token
sp = spotipy.Spotify(auth=access_token)

# Check for available devices in a loop until one is found
device_id = None
while not device_id:
    devices = sp.devices()
    if devices['devices']:
        device_id = devices['devices'][0]['id']
    else:
        print("No devices found, waiting for 5 seconds...")
        time.sleep(5)

# Search for a track
# Replace with your playlist URI
playlist_uri = "spotify:playlist:2iUsaQumT7A4Cy93onxrLe"

# Get tracks from the playlist (optional if you need to display or process the tracks)
playlist_tracks = sp.playlist_tracks(playlist_uri)

# Start playback on the specified device
sp.start_playback(device_id=device_id, context_uri=playlist_uri)

