from flask import Flask, request, redirect, session, render_template, send_file
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from spotify.spotify_client import SpotifyClient
from mp3_downloader import PlaylistDownloader
import os
import time
from flask_socketio import SocketIO, emit
import schedule
from utils import delete_downloaded_files
from dotenv import load_dotenv

# load_dotenv(".env")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_COOKIE_NAME"] = "spotify-login-session"
db = SQLAlchemy(app)
app.config["SESSION_SQLALCHEMY"] = db
Session(app)

PORT = 5000

sp_client = SpotifyClient()
socketio = SocketIO(app)

@app.route("/")
def homepage():
    return render_template("index.html")

@socketio.on(message='connect', namespace='/download/stream')
def test_connect():
    emit('my response', {'data': 'Connected'})

@app.route("/spotify/login")
def spotify_login():
    """Login to Spotify through the browser"""
    sp_login = sp_client.login()
    return redirect(sp_login)


@app.route("/callback/")
def spotify_authorize():
    """Application callback endpoint"""
    sp_oauth = sp_client.create_spotify_oauth()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    sp_client.get_token()
    return redirect("/available/playlists")


@app.route("/logout")
def logout():
    sp_client.logout()
    session.clear()
    return redirect("/")


@app.route("/available/playlists", methods=["GET", "POST"])
def view_playlist():
    user_details = sp_client.get_user_details()
    user_name = user_details[0]
    user_images = user_details[1]

    playlists = sp_client.get_all_playlists()
    playlists_names = {key[1][0]: key[1][2] for key in playlists.items()}
    playlist_dict = {key[1][0]: key[1][1] for key in playlists.items()}

    if request.method == "POST":
        for key in playlist_dict.items():
            if request.form.get("view_tracks_button") == key[0]:
                playlist_id = key[1]
                tracks = sp_client.get_playlist_tracks(playlist_id)
                return render_template(
                    "tracks.html",
                    tracks=tracks,
                    user_name=user_name,
                    user_images=user_images,
                )

            if request.form.get("download_button") == key[0]:
                playlist_id = key[1]
                playlist_name = key[0]
                playlist_cover_img = playlists_names[playlist_name]
                sp_client.write_playlist_tracks(playlist_id, playlist_name)

                playlist_downloader = PlaylistDownloader(playlist_name, socketio)
                playlist_downloader.find_and_download_songs()

                formatted_playlist_name = "".join(
                    e for e in playlist_name if e.isalnum()
                )
                download_zip = f"{formatted_playlist_name}.zip"
                return render_template(
                    "download_playlist.html",
                    file_name=playlist_name,
                    download_zip=download_zip,
                    playlist_cover_img=playlist_cover_img,
                )

    with app.app_context():
        rendered = render_template(
            "playlists.html",
            playlists=playlists_names,
            user_name=user_name,
            user_images=user_images,
        )
    return rendered


@app.route("/download/<file_name>")
def download(file_name):
    filepath = os.path.join("Downloads/", file_name)
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    schedule.every().day.at("00:00").do(delete_downloaded_files)
    socketio.run(app, debug=True, port=PORT)
