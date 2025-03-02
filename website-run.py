from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from pymongo import MongoClient
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB kapcsolat
client = MongoClient('mongodb://localhost:27017/')
db = client['spotify_db']
users_collection = db['users']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/get_playback_time')
def get_playback_time():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'time': 0})

    user = users_collection.find_one({'user_id': user_id})
    if user:
        return jsonify({'time': user.get('playback_time', 0)})
    return jsonify({'time': 0})

@app.route('/get_leaderboard')
def get_leaderboard():
    leaderboard = users_collection.find().sort('playback_time', -1).limit(10)
    leaderboard_data = [{'name': user['name'], 'time': user['playback_time']} for user in leaderboard]
    return jsonify(leaderboard_data)

if __name__ == '__main__':
    app.run(debug=True)