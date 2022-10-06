import requests
import shutil
import os
from logging_own import log
import pytube



def get_file(os_infos, vid_url, download_format, is_playlist=False, name_of_playlist="Unbekannt", track_number="0"):
    #author und filename
    yt = pytube.YouTube(vid_url)
    try:
        author, topic = yt.author.split("-")
    except ValueError:
        author = yt.author

    stream = yt.streams.get_highest_resolution()
    file = f"{author}- {stream.title}"
    filename = f"{file}.{download_format}"
    #/ und \\ ersetzen durch -
    for n in range(0, 9):
        if "/" in filename:
            vorne, hinten = filename.split("/", 1)
            filename = vorne + "-" + hinten
        elif "\\" in filename:
            vorne, hinten = filename.split("\\", 1)
            filename = vorne + "-" + hinten
        else:
            break

    if is_playlist:
        path = f"{os_infos['path']}{os_infos['path_seperator']}{download_format}{os_infos['path_seperator']}Playlist{os_infos['path_seperator']}{name_of_playlist}"
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
    else:
        path = f"{os_infos['path']}{os_infos['path_seperator']}{download_format}{os_infos['path_seperator']}Einzeln{os_infos['path_seperator']}"

    if os.path.exists(path+os_infos["path_seperator"]+track_number+" "+filename) or os.path.exists(path+os_infos["path_seperator"]+filename):
        return True

    url = "http://api.flocloud.at/youtubeDownload"
    parameters = {"url": vid_url, "download_format": download_format, "name_of_playlist": name_of_playlist,
                  "track_number": track_number}
    response = requests.get(url, params=parameters, stream=True)
    print(response.status_code)
    print(response.url)


    if is_playlist:
        with open(path+os_infos["path_seperator"]+track_number+" "+filename, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
    else:
        with open(path+os_infos["path_seperator"]+filename, 'wb') as f:
            shutil.copyfileobj(response.raw, f)