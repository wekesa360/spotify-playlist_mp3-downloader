from flask import Flask, request, redirect, session, render_template
import spotify.spotify_client as sp_auth
from decouple import config
from dotenv import load_dotenv
from mp3_downloader import display_playlist_tracks, find_and_download_songs

load_dotenv('.env')
app = Flask(__name__)

app.secret_key = config('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
PORT = 5000

@app.route('/')
def spotify_login():
    sp_login = sp_auth.login()
    return redirect(sp_login)

@app.route('/callback/')
def spotify_authorize():
    sp_oauth = sp_auth.create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    sp_auth.get_token()
    return redirect('/available_playlists')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/available_playlists')
def sp_user_playlists():
    user_details = sp_auth.get_user_details()
    user_name = user_details[0]
    user_images = user_details[1]
    playlists = sp_auth.get_all_playlists()
    playlists_names = []
    for key in playlists.items():
        playlists_names.append(key[1][0])
    print('=================')
    print('SELECT PLAYLIST')
    print('=================')
    choice = input("Enter playlist index: ")
    try:
        playlist_dict = playlists[choice]
        playlist = sp_auth.get_playlist_tracks(playlist_dict)
    except ValueError:
        print('Enter an index of the available playlists')
    print('=================')
    print('PLAYLIST ITEMS')
    print('=================')
    display_playlist_tracks(playlist)
    print('=================')
    print('DOWNLOAD PLAYLIST')
    print('=================')
    choice = input("yes or no: ")
    if choice == 'yes':
        find_and_download_songs(playlist)
    elif choice == 'no':
        print('Great')
    else:
        print('Strictly yes or no!')
    return render_template('index.html', playlists=playlists_names,
                            user_name=user_name, user_images=user_images)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
