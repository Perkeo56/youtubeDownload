import requests
import shutil
import music_tag
from logging_own import log
import os


def set_tags(yt, file, author, name_of_playlist, path, is_playlist=False, track_number=0):

    if "Album" in name_of_playlist:
        album, name_of_playlist = name_of_playlist.split("- ")
    if is_playlist:
        song = music_tag.load_file(f"{path}/{track_number} {file}")
        song.append_tag('album', name_of_playlist)
        song['tracknumber'] = track_number
    else:
        song = music_tag.load_file(f"{path}/{file}")
    song.append_tag('title', yt.title)
    song.append_tag('artist', author)
    while not download_image(yt.thumbnail_url, path):
        continue
    with open(path + "/artwork.jpg", 'rb') as img_in:
       song['artwork'] = img_in.read()
    os.remove(path + "/artwork.jpg")
    song.save()


def download_image(url, path):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(f"{path}/artwork.jpg", 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        f.close()
    else:
        log("Bild konnte nicht heruntergeladen werden.", "[ERROR]")
        return False
    return True
