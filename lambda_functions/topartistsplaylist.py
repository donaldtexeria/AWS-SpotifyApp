import json
import requests
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
        print("**STARTING**")
        body = json.loads(event['body'])
        access_token = body.get("access_token")
        user_id = body.get("user_id")
        playlist_name = body.get("playlist_name")

        top_artists_url = "https://api.spotify.com/v1/me/top/artists?limit=50"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(top_artists_url, headers=headers)
        if response.status_code == 200:
            artists_data = response.json()
            artist_ids = [artist['id'] for artist in artists_data['items']]
            print("Top artists:", artist_ids)
        else:
            print("Failed to get top artists")
            print(response.status_code, response.text)
            return {
                "statusCode": response.status_code,
                "body": json.dumps("ERROR")
            }
        playlist_id = create_spotify_playlist(user_id, playlist_name, access_token)
        track_ids = []  # Collect track IDs from top artists' tracks
        for artist_id in artist_ids:
            tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
            tracks_response = requests.get(tracks_url, headers=headers)
            if tracks_response.status_code == 200:
                tracks = tracks_response.json()['tracks']
                top_track = tracks[0]  # Get the top track (first in the list)
                track_ids.append(top_track['uri'])
        result = add_tracks_to_playlist(playlist_id, track_ids, access_token)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except Exception as e:
        print("**ERROR**")
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }