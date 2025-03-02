from pymongo import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# MongoDB kapcsolat
client = MongoClient('mongodb://localhost:27017/')
db = client['spotify_db']
users_collection = db['users']

# Spotify API beállítások
SPOTIPY_CLIENT_ID = 'your_client_id'
SPOTIPY_CLIENT_SECRET = 'your_client_secret'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

def update_playback_time():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-read-recently-played"
    )
    while True:
        users = users_collection.find()
        for user in users:
            token_info = user.get('token_info')
            if token_info:
                sp = spotipy.Spotify(auth=token_info['access_token'])
                recent_tracks = sp.current_user_recently_played(limit=50)
                playback_time = sum(track['track']['duration_ms'] for track in recent_tracks['items']) // 60000
                users_collection.update_one(
                    {'user_id': user['user_id']},
                    {'$set': {'playback_time': playback_time}}
                )
        time.sleep(60)  # Minden percben frissít

if __name__ == '__main__':
    update_playback_time()