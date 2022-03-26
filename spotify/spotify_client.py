import time
import csv
from pathlib import Path
import spotipy
from flask import redirect, session
import os
from dotenv import load_dotenv
from spotipy import SpotifyOAuth

# read env variables from .env file
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# spotify urls
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# client-side parameters
CLIENT_SIDE_URL = 'http://localhost'
PORT = 5000
REDIRECT_URI = "{}:{}/callback/".format(CLIENT_SIDE_URL, PORT)
SCOPE = os.getenv('SCOPE')
STATE = ''
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

# spotify authentication credentials
def create_spotify_oauth():
    """
    spotify api credentials
    """
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE)

# spotify login and authorization
def login():
    """
    login spotify
    """
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return auth_url

# get access token
def get_token():
    """
    check token expires in, and refresh
    """
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
    """
    verify user session
    """
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    return sp


def logout():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(".cache")
        session.clear()
        for key in list(session.keys()):
            session.pop(key)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def get_user_details():
    """
    get spotify user details
    """
    sp = verify_session()
    user_details = sp.current_user()
    user_name = user_details['display_name']
    user_images = user_details['images'][0]['url']
    user_details = [user_name, user_images]
    return user_details


def get_all_playlists():
    """
    get all user playlists
    """
    sp = verify_session()
    playlists = sp.current_user_playlists()
    dict_playlists = {}
    print(playlists)
    for i, playlist in enumerate(playlists['items']):
        i = str(i)
        dict_playlists[i] = [playlist['name'], playlist['id'], playlist['images'][0]['url']]
    """print('====================')
    print('AVAILABLE PLAYLISTS')
    print('====================')
    for key in dict_playlists:
        print("{}. {}".format(key, dict_playlists[key]))"""
    return dict_playlists


def write_playlist_tracks(playlist_id, playlist_name: str):
    """
    write  playlist's tracks to a csv file
    """
    sp = verify_session()
    playlist_tracks = sp.playlist_items(playlist_id)
    path = Path('playlist_tracks_csv/')
    if not os.path.exists(path):
        path.mkdir(parents=True)
    else:
        print(path)
        # write playlist into csv file
        fpath = (path / playlist_name).with_suffix('.csv')
        with fpath.open(mode='w+', encoding='utf-8') as file_out:
            writer = csv.DictWriter(file_out, fieldnames=["name", "artists", "spotify_url"])
            writer.writeheader()
            while True:
                # filter playlist_tracks items
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


def get_playlist_tracks(playlist_id):
    """
    get a playlist's tracks
    """
    sp = verify_session()
    playlist_items = []
    playlist_tracks = sp.playlist_items(playlist_id)
    print(playlist_tracks)
    while True:
        for item in playlist_tracks['items']:
            if 'track' in item:
                track = item['track']
            else:
                track = item
            try:
                track_name = track['name']
                track_artist = track['artists'][0]['name']
                track = '{} by {}'.format(track_name, track_artist)
                playlist_items.append(track)

            except KeyError:
                print(u'Skipping track {0} by {1} (local only?)'.format(
                    track['name'], track['artists'][0]['name']))
        else:
            break
    return playlist_items
