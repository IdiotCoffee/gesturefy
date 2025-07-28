🎧 Gesturefy – Control Spotify with Hand Gestures
Sick of digging through 15 open tabs just to change your music while you're in the zone? Gesturefy is a simple Python project that lets you control Spotify playback using just your hands via your webcam. Swipe to skip. Pinch to pause. Thumbs-up to resume. Two hands? Adjust the volume.

A lightweight but surprisingly powerful weekend build that taught me a lot about gesture tracking and real-time control flows.


🧍‍♂️ Author
Made by Ishaan Mavinkurve. Check out the demo video on LinkedIn.

🔧 Features

👉 Swipe left/right to switch tracks
✊ Pinch to pause playback
👍 Thumbs-up to resume music
👐 Use two hands to control volume by changing the distance between them
🧠 Smart lock: disables swipe gestures when two hands are detected to prevent accidental skips


🧠 How It Works
Gesturefy uses MediaPipe to track hands, then maps specific motions to Spotify playback actions via the Spotipy API:

Swipe detection: relative position between wrist and index tip
Pinch detection: checks if index and thumb are close
Thumbs-up: checks finger positions to identify thumbs-up
Volume control: calculates Euclidean distance between index tips of both hands

The result? Intuitive, hands-free control over your music — no keyboard shortcuts or GUIs.

🚀 Setup Instructions
1. Clone the repo
git clone https://github.com/IdiotCoffee/gesturefy.git
cd gesturefy

2. Add your Spotify API credentials
Create a file called creds.py in the project folder with your Spotify developer credentials:
client_id = "{YOUR_SPOTIFY_CLIENT_ID}"
client_secret = "{YOUR_SPOTIFY_CLIENT_SECRET}"
redirect_uri = "http://127.0.0.1:3000"

You can get these by registering an app at the Spotify Developer Dashboard.
3. Install dependencies
pip install opencv-python mediapipe numpy spotipy

4. Run the app
python main.py

On first run, Spotify will ask for permission in a browser popup — click OK, and you’re in.

📁 Project Structure
gesturefy/
│
├── main.py            # Main file with webcam + gesture logic
├── creds.py           # Spotify credentials (add this yourself)
├── mute.py            # Detect pinch gesture
├── play.py            # Detect thumbs-up
├── tracks.py          # Detect swipe left/right
├── volume.py          # Volume control using two hands
└── README.md          # You're reading it


🛠️ Built With

MediaPipe for real-time hand tracking
Spotipy to control Spotify playback
OpenCV for webcam and visual overlay
NumPy for gesture math


💡 Why This Was Interesting
A seemingly simple feature — swipe detection — was surprisingly tricky. Hands move fast, webcam input can jitter, and false positives were everywhere. Adding logic to lock gestures when both hands are up made the whole experience way smoother.

⚠️ Notes

Works best under good lighting conditions
Currently supports webcam input only (no mobile support yet)
Only supports one Spotify account at a time


🎵 Music
For demo purposes, consider using royalty-free tracks. Here’s a good playlist:StreamBeats by Harris Heller

📝 License
MIT — do whatever you want, just don’t sell it as your own.

🙋‍♂️ Questions?
Open an issue or message me on GitHub if you're curious how it works under the hood.