from time import ctime

logging = False


def log(message, type="[INFO]"):
    if logging == True:
        log_file = open("youtubeDownload.log", "a")
        log_file.write(str(ctime()) + f" {type} {message}\n")
        log_file.close()
        #print(f"{type} {message}")
        return
    else:
        return
