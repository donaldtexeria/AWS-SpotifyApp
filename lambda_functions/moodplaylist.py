import json
import requests
from configparser import ConfigParser

SPOTIFY_API_URL = "https://api.spotify.com/v1"

def create_spotify_playlist(user_id, playlist_name, access_token):
    url = f"{SPOTIFY_API_URL}/users/{user_id}/playlists"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': playlist_name,
        'public': False  # You can set this to True if you want a public playlist
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        playlist_id = response.json()['id']
        return playlist_id
    else:
        raise Exception(f"Failed to create playlist: {response.text}")

def search_spotify_tracks(query, access_token):
    url = f"{SPOTIFY_API_URL}/search"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': query,
        'type': 'track',
        'limit': 10  # Limit the number of results
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        tracks = response.json()['tracks']['items']
        track_uris = [track['uri'] for track in tracks]
        return track_uris
    else:
        raise Exception(f"Failed to search tracks: {response.text}")

def add_tracks_to_playlist(playlist_id, track_uris, access_token):
    url = f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    data = {
        'uris': track_uris
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        return playlist_id
    else:
        raise Exception(f"Failed to add tracks: {response.text}")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        access_token = body.get('access_token')
        playlist_name = body.get('playlist_name')
        sentiment = body.get('sentiment')
        mood = ""
        if sentiment == "NEGATIVE":
            mood = "sad"
        elif sentiment == "MIXED":
            mood = "versatile"
        elif sentiment == "NEUTRAL":
            mood = "ambient"
        elif sentiment == "POSITIVE":
            mood = "happy"
        tracks = search_spotify_tracks(mood, access_token)
        playlist_id = create_spotify_playlist(user_id, playlist_name, access_token)
        result = add_tracks_to_playlist(playlist_id, tracks, access_token)
        return {
            'statusCode': 200,
            'body': json.dumps(playlist_id)
        }

    except Exception as e:
        print("**ERROR**")
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
