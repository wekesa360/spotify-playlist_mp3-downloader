import csv
from pathlib import Path
import shutil
import os
import yt_dlp
from youtube_search import YoutubeSearch
from utils import check_song_in_downloads, move_song_to_playlist
from pytube import YouTube


class PlaylistDownloader:
    def __init__(self, playlist_name):
        self.playlist_name = playlist_name
        self.playlist_tracks_path = Path("playlist_tracks_csv/")
        self.downloads_path = Path("Downloads/")

    def display_playlist_tracks(self):
        """Display playlist tracks from saved csv file"""
        file_name = f"{self.playlist_name}.csv"
        fpath = self.playlist_tracks_path / file_name

        with fpath.open(mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            tracks = [
                f"{row['name']} - {row['artists']}: spotify_url: {row['spotify_url']}"
                for row in csv_reader
            ]

        return tracks

    def find_and_download_songs(self):
        """Download tracks from YouTube, referencing the playlist's tracks csv file"""
        TOTAL_ATTEMPTS = 10
        saved_playlist_zip_file = "".join(e for e in self.playlist_name if e.isalnum())
        filepath = self.downloads_path / saved_playlist_zip_file

        if not filepath.exists():
            filepath.mkdir(parents=True)

        fpath = self.playlist_tracks_path / f"{self.playlist_name}.csv"

        with fpath.open(mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                name, artist = row[0], row[1]
                text_to_search = f"{artist} - {name}"
                best_url = None
                attempts_left = TOTAL_ATTEMPTS

                while attempts_left > 0:
                    try:
                        results_list = YoutubeSearch(
                            text_to_search, max_results=1
                        ).to_dict()
                        best_url = (
                            f"https://www.youtube.com{results_list[0]['url_suffix']}"
                        )
                        break
                    except IndexError:
                        attempts_left -= 1
                        print(
                            f"No valid URLs found for {text_to_search}, trying again ({attempts_left} attempts left)."
                        )

                if best_url is None:
                    print(f"No valid URLs found for {text_to_search}, skipping track.")
                    continue

                print(f"Initiating download for {text_to_search}.")
                video = YouTube(best_url)
                filename = f"{video.title}.mp3"
                downloaded_file_path = check_song_in_downloads(
                    filename, self.downloads_path
                )

                if downloaded_file_path:
                    move_song_to_playlist(downloaded_file_path, filepath)
                    continue

                stream = video.streams.filter(only_audio=True).first()
                stream.download(output_path=filepath, filename=filename)
                print(f"Download for {text_to_search} complete")

        # Write downloaded playlist folder and zip it
        shutil.make_archive(filepath, "zip", filepath)
