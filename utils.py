import os
import time
import shutil


def delete_downloaded_files(directory, time_threshold):
    """Delete files and folders from a directory that are older than a given time threshold"""
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            if time.time() - os.path.getctime(file_path) > time_threshold:
                print(f"Deleting file: {file_path}")
                os.remove(file_path)
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if time.time() - os.path.getctime(folder_path) > time_threshold:
                print(f"Deleting folder: {folder_path}")
                shutil.rmtree(folder_path)
    return True


def check_song_in_downloads(song_title, playlist_directory):
    """Check if a song is already available in one of the playlist folders"""
    for root, _, files in os.walk(playlist_directory):
        for file in files:
            if song_title in file:
                return os.path.join(root, file)
    return None


def move_song_to_playlist(file_path, current_playlist_folder):
    """Move a song file to the current playlist folder"""
    song_title = os.path.basename(file_path)
    destination_path = os.path.join(current_playlist_folder, song_title)
    shutil.move(file_path, destination_path)
    print(f"{song_title} was moved to {destination_path}.")
    return True
