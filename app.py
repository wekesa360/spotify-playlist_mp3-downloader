from flask import Flask, request, redirect, session, render_template
import spotify.spotify_client as sp_auth
import os
from dotenv import load_dotenv
from mp3_downloader import sp_user_playlists

load_dotenv('.env')
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
PORT = 5000

# spotify login
@app.route('/')
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
    return redirect('/success')

# logout from spotify
@app.route('/logout')
def logout():
    """
    logout from spotify
    """
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

# url endpoint for a successful login to spotify
@app.route('/success')
def success():
    user_details = sp_auth.get_user_details()
    user_name = user_details[0]
    user_images = user_details[1]
    sp_user_playlists()
    return render_template('index.html', user_images=user_images, user_name=user_name)


# render playlist
"""
@app.route('/available_playlists')
def view_playlist():
    # get names of playlists
    playlists = sp_auth.get_all_playlists()
    playlists_names = []
    for key in playlists.items():
        playlists_names.append(key[1][0])
    with app.app_context():
        rendered = render_template('index.html', playlists=playlists_names,
                           user_name=user_name, user_images=user_images)

    return rendered"""

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
