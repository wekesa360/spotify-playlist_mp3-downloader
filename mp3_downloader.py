import csv
from pathlib import Path
import shutil
import os
import yt_dlp
from youtube_search import YoutubeSearch
from pytube import YouTube


def display_playlist_tracks(playlist):
    """
    display playlist tracks from saved csv file
    """
    path = Path('playlist_tracks_csv/')
    file_name = '{}'.format(playlist)
    # read from existing csv file
    fpath = (path / file_name).with_suffix('.csv')
    with fpath.open(mode='w') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        tracks = []
        line_count = 1
        for row in csv_reader:
            track = "{} - {}: spotify_url: {}".format(row['name'], row['artists'], row['spotify_url'])
            tracks.append(track)
            line_count += 1
        return tracks


def find_and_download_songs(reference_file: str):
    """
    Download tracks from YouTube, referencing the playlist's tracks csv file
    """
    TOTAL_ATTEMPTS = 10
    saved_playlist_zip_file = ''.join(e for e in reference_file if e.isalnum())
    filepath = os.path.join('Downloads/', saved_playlist_zip_file)
    if not os.path.exists('Downloads/{}/'.format(saved_playlist_zip_file)):
        os.makedirs('Downloads/{}'.format(saved_playlist_zip_file))
    path = "playlist_tracks_csv/"
    path = Path(path)
    fpath = (path / reference_file).with_suffix('.csv')
    with fpath.open(mode="r", encoding='utf-8') as file:
        
        line_count = 0
        for row in file:
            if line_count == 0:
                line_count += 1
            else:
                temp = row.split(',')
                name, artist = temp[0], temp[1]
                text_to_search = artist + " - " + name
                best_url = None
                attempts_left = TOTAL_ATTEMPTS
                line_count += 1
                while attempts_left > 0:
                    try:
                        results_list = YoutubeSearch(text_to_search, max_results=1).to_dict()
                        best_url = "https://www.youtube.com{}".format(results_list[0]['url_suffix'])
                        break
                    except IndexError:
                        attempts_left -= 1
                        print("No valid URLs found for {}, trying again ({} attempts left).".format(
                            text_to_search, attempts_left))
                if best_url is None:
                    print("No valid URLs found for {}, skipping track.".format(text_to_search))
                    continue
                # run you-get to fetch and download the link's audio
                print("Initiating download for {}.".format(text_to_search))
                video = YouTube(best_url)    # yt_dlp.YoutubeDL().extract_info(url=best_url, download=False)
                filename = f"{video.title}.mp3"
                stream = video.streams.filter(only_audio=True).first()
                stream.download(output_path=filepath, filename=filename)
                print(f"Download for {text_to_search} complete")
    print(filepath)
    # write downloaded playlist folder and zip it
    shutil.make_archive(filepath, 'zip', filepath)
