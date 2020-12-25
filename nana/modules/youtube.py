import logging
import os
import re
import shutil
import subprocess
import sys
import traceback
import time

import pafy
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pathlib import Path

from youtube_dl import YoutubeDL
from youtube_dl.utils import (
    ContentTooShortError,
    DownloadError,
    ExtractorError,
    GeoRestrictedError,
    MaxDownloadsReached,
    PostProcessingError,
    UnavailableVideoError,
    XAttrMetadataError,
)

from nana import app, setbot, Command, AdminSettings, edrep
from nana.utils.parser import escape_markdown
from nana.modules.downloads import download_url, progressdl

__MODULE__ = "YouTube"
__HELP__ = """
download, convert music from youtube!

──「 **Download video** 」──
-> `ytdl (url)`
Download youtube video (mp4)

──「 **Convert to music** 」──
-> `ytmusic (url)`
Download youtube music, and then send to tg as music.
"""


@app.on_message(filters.user(AdminSettings) & filters.command("ytdl", Command))
async def youtube_download(client, message):
    args = message.text.split(None, 1)
    if len(args) == 1:
        await edrep(message, text="missing [url] parameter!!")
        return
    url = args[1]
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await edrep(message, text=f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await edrep(message, text="`The download content was too short.`")
        return
    except GeoRestrictedError:
        await edrep(
            message,
            text="`Video is not available from your geographic location due to geographic restrictions imposed by a website.`",
        )
        return
    except MaxDownloadsReached:
        await edrep(message, text="`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await edrep(message, text="`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await edrep(message, text="`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await edrep(message, text=f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await edrep(message, text="`There was an error during info extraction.`")
        return
    except Exception as e:
        await edrep(message, text=f"{str(type(e)): {str(e)}}")
        return
    thumbnail = Path(f"{ytdl_data['id']}.jpg")
    c_time = time.time()
    try:
        await message.reply_video(
            f"{ytdl_data['id']}.mp4",
            supports_streaming=True,
            duration=ytdl_data["duration"],
            caption=ytdl_data["title"],
            thumb=thumbnail,
            progress=lambda d, t: client.loop.create_task(
                progressdl(d, t, message, c_time, "Downloading...")
            ),
        ),
    except FileNotFoundError:
        await message.reply_video(
            f"{ytdl_data['id']}.mp4",
            supports_streaming=True,
            duration=ytdl_data["duration"],
            caption=ytdl_data["title"],
            progress=lambda d, t: client.loop.create_task(
                progressdl(d, t, message, c_time, "Downloading...")
            ),
        ),
    os.remove(f"{ytdl_data['id']}.mp4")
    if thumbnail:
        os.remove(thumbnail)
    await message.delete()


@app.on_message(filters.user(AdminSettings) & filters.command("ytmusic", Command))
async def youtube_music(client, message):
    args = message.text.split(None, 1)
    if len(args) == 1:
        await edrep(message, text="missing [url] parameter!")
        return
    url = args[1]
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "outtmpl": "%(id)s.mp3",
        "quiet": True,
        "logtostderr": False,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await edrep(message, text=f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await edrep(message, text="`The download content was too short.`")
        return
    except GeoRestrictedError:
        await edrep(
            message,
            text="`Video is not available from your geographic location due to geographic restrictions imposed by a website.`",
        )
        return
    except MaxDownloadsReached:
        await edrep(message, text="`Max-downloads limit has been reached.`")
        return
    except PostProcessingError:
        await edrep(message, text="`There was an error during post processing.`")
        return
    except UnavailableVideoError:
        await edrep(message, text="`Media is not available in the requested format.`")
        return
    except XAttrMetadataError as XAME:
        await edrep(message, text=f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await edrep(message, text="`There was an error during info extraction.`")
        return
    except Exception as e:
        await edrep(message, text=f"{str(type(e)): {str(e)}}")
        return
    thumbnail = Path(f"{ytdl_data['id']}.jpg")
    c_time = time.time()
    try:
        await message.reply_audio(
            f"{ytdl_data['id']}.mp3",
            duration=ytdl_data["duration"],
            caption=ytdl_data["title"],
            thumb=thumbnail,
            progress=lambda d, t: client.loop.create_task(
                progressdl(d, t, message, c_time, "Downloading...")
            ),
        ),
    except FileNotFoundError:
        await message.reply_audio(
            f"{ytdl_data['id']}.mp3",
            duration=ytdl_data["duration"],
            caption=ytdl_data["title"],
            progress=lambda d, t: client.loop.create_task(
                progressdl(d, t, message, c_time, "Downloading...")
            ),
        ),
    os.remove(f"{ytdl_data['id']}.mp3")
    if thumbnail:
        os.remove(thumbnail)
    await message.delete()
