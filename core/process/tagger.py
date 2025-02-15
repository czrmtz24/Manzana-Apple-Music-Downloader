import os
import requests

from mutagen.mp4 import MP4, MP4Cover
from utils import logger

def tag(media, data, cover, output, nolrc=False, noTags=False):
    if not noTags:
        tags = MP4(media)
        tags.delete()

        __tags = {
            "\xa9alb": data.get("album"),
            "\xa9nam": data.get("song"),
            "aART": data.get("albumartist"),
            "\xa9ART": data.get("songartist"),
            "\xa9wrt": data.get("composer"),
            "\xa9gen": data.get("genre"),
            "rtng": data.get("rating"),
            "\xa9day": data.get("releasedate"),
            "cprt": data.get("copyright"),
            "stik": data.get("type"),
            "\xa9lyr": data.get("lyrics"),
            "trkn": (data.get("trackno"), data.get("trackcount")),
            "disk": (data.get("discno"), data.get("discno")),
            "----:com.apple.itunes:Label": data.get("recordlabel"),
            "----:com.apple.itunes:ISRC": data.get("isrc"),
            "----:com.apple.itunes:UPC": data.get("upc"),
            "----:com.apple.itunes:Lyricist": data.get("songwriter"),
        }

        if "credits" in data:
            for k, v in data["credits"].items():
                __tags[f'----:com.apple.itunes:{k}'] = v

        if data["type"] == 6:
            del __tags["trkn"]
            del __tags["disk"]

        for key, value in __tags.items():
            if value:
                if isinstance(value, list):
                    value = ['\r\n'.join(value)]
                    
                    if key.startswith("----:com.apple.itunes:"):
                        value = [val.encode() for val in value]

                    try:
                        tags[key] = value
                    except UnicodeEncodeError:
                        continue
                else:
                    if key.startswith("----:com.apple.itunes:"):
                        value = value.encode()
                    
                    if key in [
                        "aART",
                        "\xa9ART",
                        "\xa9wrt",
                        "\xa9lyr",
                        "----:com.apple.itunes:Lyricist"
                    ]:
                        value = value.replace(
                            ', ',
                            '\r\n'
                        ).replace(
                            ' & ',
                            '\r\n'
                        )

                    try:
                        tags[key] = [value]
                    except UnicodeEncodeError:
                        continue

        logger.info("Embedding artwork...")
        if not cover:
            cover = requests.get(data["coverUrl"], stream=True).content
        tags["covr"] = [MP4Cover(cover, MP4Cover.FORMAT_JPEG)]
        tags.save()
            
    if data["type"] == 1:
        if not nolrc:
            if "timeSyncedLyrics" in data:
                logger.info("Saving time-synced lyrics...")

                with open(os.path.join(output, f'{data["file"]}.lrc'), 'w+', encoding="utf8") as l:
                    l.write(
                        '\n'.join(
                            data["timeSyncedLyrics"]
                        )
                    )
            else:
                logger.warning("Unable to find time-synced lyrics!")
