from flask import Flask, request, redirect, session, render_template, send_file
import spotify.spotify_client as sp_auth
from mp3_downloader import find_and_download_songs
import os
import datetime
from dotenv import load_dotenv

load_dotenv('.env')
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
PORT = 5000


@app.route('/')
def homepage():
    return render_template('index.html')


# spotify login
@app.route('/spotify_login')
def spotify_login():
    """
    Login to spotify, through the browser
    """
    sp_login = sp_auth.login()
    return redirect(sp_login)


# redirect url for spotify api
@app.route('/callback/')
def spotify_authorize():
    """
    application callback endpoint
    """
    sp_oauth = sp_auth.create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    sp_auth.get_token()
    return redirect('/available_playlists')


# logout from spotify
@app.route('/logout')
def logout():
    sp_auth.logout()
    session.clear()
    return redirect('/')


# render playlist
@app.route('/available_playlists', methods=['GET', 'POST'])
def view_playlist():
    # user details
    user_details = sp_auth.get_user_details()
    user_name = user_details[0]
    user_images = user_details[1]
    # get names of playlists
    playlists = sp_auth.get_all_playlists()
    playlists_names = {}
    playlist_dict = {}
    for key in playlists.items():
        playlists_names[key[1][0]] = "{}".format(key[1][2])
        playlist_dict[key[1][0]] = "{}".format(key[1][1])
    print(playlists_names)
    for key in playlist_dict.items():
        if request.method == 'POST':
            if request.form.get('view_tracks_button') == key[0]:
                playlist_id = key[1]
                # view track
                tracks = sp_auth.get_playlist_tracks(playlist_id)
                return render_template('tracks.html', tracks=tracks)
            if request.form.get('download_button') == key[0]:
                playlist_id = key[1]
                playlist_name = key[0]
                playlist_cover_img = playlists_names[playlist_name]
                sp_auth.write_playlist_tracks(playlist_id, playlist_name)
                # download playlist
                find_and_download_songs(playlist_name)
                formatted_playlist_name = ''.join(e for e in playlist_name if e.isalnum())
                download_zip = "{}.zip".format(str(formatted_playlist_name))
                print(download_zip)
                return render_template('download.html', file_name=playlist_name, download_zip=download_zip,
                                       playlist_cover_img=playlist_cover_img)
            else:
                redirect('/available_playlists')
    with app.app_context():
        rendered = render_template('playlists.html', playlists=playlists_names,
                                   user_name=user_name, user_images=user_images)

    return rendered

# download playlist as zipped folder
@app.route('/download/<file_name>')
def download(file_name):
    filepath = os.path.join('Downloads/', file_name)
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
