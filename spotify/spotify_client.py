import time
import csv
from pathlib import Path
import spotipy
from flask import redirect, session
import os
from dotenv import load_dotenv
from spotipy import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{API_VERSION}"
CLIENT_SIDE_URL = "https://spotify-playlist-mp3-downloader.onrender.com"
PORT = 5000
REDIRECT_URI = f"{CLIENT_SIDE_URL}/callback/"
SCOPE = os.getenv("SCOPE")
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


class SpotifyClient:
    def __init__(self):
        self.sp_oauth = self.create_spotify_oauth()

    @staticmethod
    def create_spotify_oauth():
        return SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
        )

    def login(self):
        auth_url = self.sp_oauth.get_authorize_url()
        return auth_url

    def get_token(self):
        token_valid = False
        token_info = session.get("token_info", {})

        if not session.get("token_info", False):
            token_valid = False
            return token_info, token_valid

        now = int(time.time())
        is_token_expired = session.get("token_info").get("expires_at") - now < 60

        if is_token_expired:
            token_info = self.sp_oauth.refresh_access_token(
                session.get("token_info").get("refresh_token")
            )

        token_valid = True
        return token_info, token_valid

    def verify_session(self):
        session["token_info"], authorized = self.get_token()
        session.modified = True
        if not authorized:
            return redirect("/")
        sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))
        return sp

    @staticmethod
    def logout():
        try:
            os.remove(".cache")
            session.clear()
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}")

    def get_user_details(self):
        sp = self.verify_session()
        user_details = sp.current_user()
        user_name = user_details["display_name"]
        user_images = user_details["images"][0]["url"]
        return user_name, user_images

    def get_all_playlists(self):
        sp = self.verify_session()
        playlists = sp.current_user_playlists()
        dict_playlists = {
            str(i): [playlist["name"], playlist["id"], playlist["images"][0]["url"]]
            for i, playlist in enumerate(playlists["items"])
        }
        return dict_playlists

    def write_playlist_tracks(self, playlist_id, playlist_name):
        sp = self.verify_session()
        playlist_tracks = sp.playlist_items(playlist_id)
        path = Path("playlist_tracks_csv/")
        path.mkdir(parents=True, exist_ok=True)

        fpath = path / f"{playlist_name}.csv"
        with fpath.open(mode="w+", encoding="utf-8") as file_out:
            writer = csv.DictWriter(
                file_out, fieldnames=["name", "artists", "spotify_url"]
            )
            writer.writeheader()

            while True:
                for item in playlist_tracks["items"]:
                    track = item["track"] if "track" in item else item
                    try:
                        track_url = track["external_urls"]["spotify"]
                        track_name = track["name"]
                        track_artist = track["artists"][0]["name"]
                        csv_line = f"{track_name},{track_artist},{track_url}\n"
                        file_out.write(csv_line)
                    except (KeyError, UnicodeEncodeError):
                        pass
                else:
                    break

        return playlist_name

    def get_playlist_tracks(self, playlist_id):
        sp = self.verify_session()
        playlist_items = []
        playlist_tracks = sp.playlist_items(playlist_id)

        while True:
            for item in playlist_tracks["items"]:
                track = item["track"] if "track" in item else item
                try:
                    track_name = track["name"]
                    track_artist = track["artists"][0]["name"]
                    track = f"{track_name} by {track_artist}"
                    playlist_items.append(track)
                except KeyError:
                    pass
            else:
                break

        return playlist_items
