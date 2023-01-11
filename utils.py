import os
import time
import shutil

directory = './Downloads'
time_threshold = 60 * 60 * 24 * 7  # 7 days

def delete_downloaded_files(directory, time_threshold):
    """
    Delete files from a directory that are older than a given time threshold
    """
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames + dirnames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getctime(file_path)
                if time.time() - file_time > time_threshold:
                    print(f"Deleting file: {file_path}")
                    os.remove(file_path)
            elif os.path.isdir(file_path):
                folder_time = os.path.getctime(file_path)
                if time.time() - folder_time > time_threshold:
                    print(f"Deleting folder: {file_path}")
                    os.rmdir(file_path)
    return True

def check_song_in_downloads(song_title, playlist_directory):
    for dirpath, dirnames, filenames, in os.walk(playlist_directory):
        for filename in filenames:
            if song_title in filename:
                # if song is already available in one of the playlist folders
                file_path = os.path.join(dirpath, filename)
                return file_path
                
def move_song_to_playlist(file_path, current_playlist_folder):
    # get th song title from the file path
    song_title = os.path.basename(file_path)
    # construct the destination file path
    destination_path = os.path.join(current_playlist_folder, song_title)
    #move the file
    shutil.move(file_path, destination_path)
    print(f"{song_title} was moved to {destination_path}.")

    return True

