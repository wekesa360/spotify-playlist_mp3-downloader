import csv
import yt_dlp
from youtube_search import YoutubeSearch

def display_playlist_tracks(playlist):
    name_of_playlist = playlist
    file_name = '{}'.format(name_of_playlist)
    with open(file_name, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        tracks = []
        line_count = 1
        for row in csv_reader:
            track = "{} - {}: spotify_url: {}".format(row['name'], row['artists'], row['spotify_url'])
            tracks.append(track)
            line_count += 1
        i = 0
        while i != len(tracks)-1:
            print("{}. {}".format(i,tracks[i]))
            i += 1
        print(f'Processed {line_count} lines.')
        return tracks

def find_and_download_songs(reference_file: str):
    TOTAL_ATTEMPTS = 10
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            temp = line.split(",")
            name, artist = temp[0], temp[1]
            text_to_search = artist + " - " + name
            best_url = None
            attempts_left = TOTAL_ATTEMPTS
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(text_to_search, max_results=1).to_dict()
                    print(results_list)
                    best_url = "https://www.youtube.com/{}".format(results_list[0]['url_suffix'])
                    print(best_url)
                    break
                except IndexError:
                    attempts_left -= 1
                    print("No valid URLs found for {}, trying again ({} attempts left).".format(
                        text_to_search, attempts_left))
            if best_url is None:
                print("No valid URLs found for {}, skipping track.".format(text_to_search))
                continue
            # Run you-get to fetch and download the link's audio
            print("Initiating download for {}.".format(text_to_search))
            video_info = yt_dlp.YoutubeDL().extract_info(
                url=best_url, download=False)
            filename = f"{video_info['title']}.mp3"
            options = {
                'cachedir':False,
                'format': 'bestaudio/best',
                'keepvideo': False,
                'outtmpl': filename,
            }
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([best_url])

