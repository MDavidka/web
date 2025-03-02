from flask import Flask, request, redirect, session, jsonify, render_template
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "3baa3b2f48c14eb0b1ec3fb7b6c5b0db")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "your_client_secret_here")
REDIRECT_URI = "https://ltpd.xyz/test.html"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1/me/player/currently-playing"

# Spotify Scopes
SCOPE = "user-read-playback-state user-read-currently-playing"

# Store refresh tokens
TOKEN_EXPIRY = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    auth_url = f"{SPOTIFY_AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(auth_url)

@app.route("/callback")
def callback():
    global TOKEN_EXPIRY

    code = request.args.get("code")
    if not code:
        return "Authorization failed.", 400

    # Exchange authorization code for access token
    response = requests.post(SPOTIFY_TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if response.status_code != 200:
        return f"Failed to get token: {response.json()}", 400

    token_data = response.json()
    session["access_token"] = token_data["access_token"]
    session["refresh_token"] = token_data["refresh_token"]
    TOKEN_EXPIRY = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

    return redirect("/test")

def refresh_token():
    global TOKEN_EXPIRY

    if TOKEN_EXPIRY and datetime.utcnow() < TOKEN_EXPIRY:
        return session.get("access_token")

    response = requests.post(SPOTIFY_TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": session.get("refresh_token"),
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })

    if response.status_code != 200:
        return None

    token_data = response.json()
    session["access_token"] = token_data["access_token"]
    TOKEN_EXPIRY = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

    return session["access_token"]

@app.route("/currently-playing")
def currently_playing():
    access_token = refresh_token()
    if not access_token:
        return jsonify({"error": "Unauthorized"}), 401

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SPOTIFY_API_URL, headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())

    return jsonify({"message": "No song currently playing"}), 204

@app.route("/test")
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run(debug=True)