import time
import csv
import spotipy
from flask import redirect, session
from decouple import config
from dotenv import load_dotenv
from spotipy import SpotifyOAuth

load_dotenv('.env')

CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# client-side Parameters
CLIENT_SIDE_URL = 'http://localhost'
PORT = 5000
REDIRECT_URI = "{}:{}/callback/".format(CLIENT_SIDE_URL, PORT)
SCOPE = 'playlist-modify-public playlist-modify-private user-library-read user-read-private'
STATE = ''
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE)

def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return auth_url

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})
    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid
    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60
    # Refreshing token if it has expired
    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
    token_valid = True
    return token_info, token_valid

def verify_session():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    return sp

def get_user_details():
    sp = verify_session()
    user_details = sp.current_user()
    user_name = user_details['display_name']
    user_images = user_details['images'][0]['url']
    user_details = [user_name, user_images]
    print('====================')
    print('USER DETAILS')
    print('====================')
    print('username: {}\nimage_url: {}'.format(user_name, user_images))
    return user_details

def get_all_playlists():
    sp = verify_session()
    playlists = sp.current_user_playlists()
    dict_playlists = {}
    for i, playlist in enumerate(playlists['items']):
        i = str(i)
        dict_playlists[i] = [playlist['name'], playlist['id']]
    print('====================')
    print('AVAILABLE PLAYLISTS')
    print('====================')
    for key in dict_playlists:
        print("{}. {}".format(key, dict_playlists[key][0]))
    return dict_playlists

def get_playlist_tracks(playlist_dict):
    sp = verify_session()
    playlist_id = playlist_dict[1]
    playlist_name = playlist_dict[0]
    playlist_tracks = sp.playlist_items(playlist_id)
    with open(playlist_name, 'w+', encoding='utf-8') as file_out:
        writer = csv.DictWriter(file_out, fieldnames=["name", "artists", "spotify_url"])
        writer.writeheader()
        while True:
            for item in playlist_tracks['items']:
                if 'track' in item:
                    track = item['track']
                else:
                    track = item
                try:
                    track_url = track['external_urls']['spotify']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    csv_line = track_name + "," + track_artist + "," + track_url + "\n"
                    try:
                        file_out.write(csv_line)
                    except UnicodeEncodeError:  # Most likely caused by non-English song names
                        print("Track named {} failed due to an encoding error. This is \
                            most likely due to this song having a non-English name.".format(track_name))
                except KeyError:
                    print(u'Skipping track {0} by {1} (local only?)'.format(
                        track['name'], track['artists'][0]['name']))
            else:
                break
    print("playlist name: {} - playlist id: {}\nwritten successfully".format(playlist_name, playlist_id))
    return playlist_name









