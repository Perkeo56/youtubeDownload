import signal
import webbrowser
import threading
import time
import tkinter as tk
from tkinter import ttk
import os
import pytube.exceptions
import requests
import sys
from threading import Thread
from pytube import Playlist
from tkinter.messagebox import showinfo
from client import get_file
from logging_own import log

# Global Variables
init = True


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def version_check():
    global os_infos
    # Version check
    time.sleep(2)

    version = requests.get("http://api.flocloud.at/youtubeDownload/version")
    if not version.content == b"""{"version":"1.0\\n"}""":
        showinfo(title="Neue Version verfügbar!", message="Eine neue Version steht zum Download zur Verfügung.")
        if os_infos['type'] == "posix":
            url = 'https://github.com/Perkeo56/youtubeDownload/raw/master/dist/youtubeDownloaderBin'
        else:
            url = "https://github.com/Perkeo56/youtubeDownload/raw/master/dist/youtubeDownloader.exe"
        webbrowser.open_new_tab(url)
        os.kill(os.getpid(), signal.SIGTERM)

def os_specific():
    global pb_text, pb, download_format, download_button, url_entry, os_infos
    # Musik Paths Posix/Windows
    os_infos = {"type": os.name}
    os_infos["path_seperator"] = "/" if os_infos["type"] == "posix" else "\\"
    os_infos['home_directory'] = os.path.expanduser("~")
    if os_infos['type'] != "posix":
        try:
            #from win32com.shell import shell, shellcon
            from winreg import ConnectRegistry, HKEY_CURRENT_USER, OpenKey, EnumKey, QueryValueEx
            access_registry = ConnectRegistry(None, HKEY_CURRENT_USER)
            access_key = OpenKey(access_registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
            os_infos['music_directory_windows'] = QueryValueEx(access_key, "My Music")[0]
            if not os.path.exists(f"{os_infos['music_directory_windows']}{os_infos['path_seperator']}YoutubeDownload"):
                os.mkdir(f"{os_infos['music_directory_windows']}{os_infos['path_seperator']}YoutubeDownload")
            os_infos['path'] = f"{os_infos['music_directory_windows']}{os_infos['path_seperator']}YoutubeDownload"

        except Exception as e:
            log(e, "[ERROR] Windows Registry reading: ")

    else:
        if os.path.exists(f"{os_infos['home_directory']}{os_infos['path_seperator']}Musik"):
            os_infos["path"] = f"{os_infos['home_directory']}{os_infos['path_seperator']}Musik{os_infos['path_seperator']}YoutubeDownload"
        else:
            os_infos["path"] = f"{os_infos['home_directory']}{os_infos['path_seperator']}Music{os_infos['path_seperator']}YoutubeDownload"



def download_init(url):
    global pb_text, pb, download_format, download_button, url_entry, os_infos
    path_einzeln = f"{os_infos['path']}{os_infos['path_seperator']}{download_format.get()}{os_infos['path_seperator']}Einzeln{os_infos['path_seperator']}"
    #os.makedirs(os_infos["path"], exist_ok=True) #durch nächsten unnötig
    os.makedirs(path_einzeln, exist_ok=True)
    log(os_infos['path'], "[INFO]")
    if "playlist" in url.lower():
        playlist = Playlist(url)
        print('Number of videos in playlist: %s' % len(playlist.video_urls))
        pb_text['text'] = update_progress_label(0, len(playlist.video_urls))
        pb['value'] = 0
        i = 1
        for s in playlist.video_urls:
            log(f"Download {i} gestartet.", "[INFO]")
            try:
                get_file(os_infos, s, download_format.get(), True, playlist.title, str(i))
                    #log("Fehler beim Herunterladen.", "[ERROR]")
                    #print("Fehler beim Herunterladen.")
            except pytube.exceptions.RegexMatchError as r:
                error_field['text'] = update_error_message("Eingabe konnte nicht gelesen werden.")
                log(r, "[ERROR]")
                download_button['state'] = tk.NORMAL
                url_entry.delete(0, 1000)
                return

            except Exception as e:
                error_field['text'] = update_error_message(e)
                log(f"Fehler beim Herunterladen {i}: {e}.", "[ERROR]")
                #print(f"Error while downloading {i}: {e}")
                download_button['state'] = tk.NORMAL
                url_entry.delete(0, 1000)
                return
            log(f"Download {i} ist abgeschlossen.", "[INFO]")
            #print(f'Download {i} ist abgeschlossen.')
            pb_text['text'] = update_progress_label(i, len(playlist.video_urls))
            pb['value'] += 100 / len(playlist.video_urls)
            i += 1
    else:
        pb_text['text'] = update_progress_label(0, 1)
        try:
            get_file(os_infos, url, download_format.get())
                #log("Fehler beim Herunterladen.", "[ERROR]")
                #print("Fehler beim Herunterladen.")
        except pytube.exceptions.RegexMatchError as r:
            error_field['text'] = update_error_message("Eingabe konnte nicht gelesen werden.")
            log(r, "[ERROR]")
            download_button['state'] = tk.NORMAL
            url_entry.delete(0, 1000)
            return
        except Exception as e:
            error_field['text'] = update_error_message(e)
            log(f"Fehler beim Herunterladen {e}.", "[ERROR]")
            download_button['state'] = tk.NORMAL
            url_entry.delete(0, 1000)
            print(e)
            return
        pb_text['text'] = update_progress_label(1, 1)
        pb['value'] += 100
    showinfo(message='Download abgeschlossen!')
    download_button['state'] = tk.NORMAL
    url_entry.delete(0, 1000)


def download_button_func():
    global url_entry, download_format, download_button, error_field, init
    if init == True:
        return
    if url_entry.get() == "":
        log("Empty field.", "[ERROR]")
        error_field['text'] = update_error_message("Leeres Eingabefeld")
        #print("Empty")
        return
    url = url_entry.get()
    error_field['text'] = update_error_message(-1)
    thread = Thread(target=download_init, args=(url,))
    thread.start()
    download_button['state'] = tk.DISABLED


def update_progress_label(number, anzahl):
    return f"Fortschritt: {number} von {anzahl}"


def update_error_message(exception):
    if exception == -1:

        return ""
    else:
        return f"Fehler: {exception}"


def root_window():
    global url_entry, pb_text, pb, download_format, download_button, error_field, init, os_infos
    log("Fenster initialisation.", "[INFO]")
    os_specific()
    root = tk.Tk()
    root.geometry("800x500")
    root.resizable(0, 0)

    # Hintergrund
    background_image = tk.PhotoImage(file=resource_path(f"{os_infos['home_directory']}{os_infos['path_seperator']}PycharmProjects{os_infos['path_seperator']}youtubeDownloadOnline{os_infos['path_seperator']}baum_800x600.png"))
    label_background = tk.Label(root, image=background_image)
    label_background.place(x=0, y=0)

    # Progressbar
    pb = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=280)
    pb.place(x=260, y=150)  # width=280
    pb_text = ttk.Label(root, text=update_progress_label(0, 0))
    pb_text.place(x=337.5, y=180)  # width=125

    # Radio Button Audio Video
    download_format = tk.StringVar()
    radio_format = tk.Radiobutton(root, text="MP3", variable=download_format, value="mp3")
    radio_format.place(x=340, y=50)  # width=55

    radio_format_2 = tk.Radiobutton(root, text="MP4", variable=download_format, value="mp4")
    radio_format_2.place(x=405, y=50)  # width=55

    download_format.set("mp3")

    # URL Input Text
    url_entry_text = tk.Label(root, text="URL :")
    url_entry_text.place(x=165, y=100)  # width = 35

    # URL Input
    url_entry = tk.Entry(root)
    # url_entry.insert(0, "URL eingeben")
    url_entry.place(x=225, y=100, width=350)  # width = 350

    # Download Button
    download_button = tk.Button(root, text="Download", command=download_button_func)
    download_button.bind("<Button-1>", download_button_func())
    download_button.place(x=600, y=95)

    error_field = tk.Label(root, text=update_error_message(-1), fg="#ff0000")
    error_field.place(x=10, y=300)

    root.title("Youtube Downloader")
    #root.iconbitmap(resource_path(f"{os_infos['home_directory']}{os_infos['path_seperator']}PycharmProjects{os_infos['path_seperator']}youtubeDownloadOnline{os_infos['path_seperator']}download-button.png"))
    root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=resource_path(f"{os_infos['home_directory']}{os_infos['path_seperator']}PycharmProjects{os_infos['path_seperator']}youtubeDownloadOnline{os_infos['path_seperator']}download-button.png")))
    #root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=resource_path("download-button.png")))
    #root.iconphoto(tk.PhotoImage("baum_800x600.png"))
    log("Fenster initialisation abgeschlossen.", "[INFO]")
    init = False
    version_thread = threading.Thread(target=version_check)
    version_thread.start()

    root.mainloop()
