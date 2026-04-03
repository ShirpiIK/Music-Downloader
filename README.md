# Music-Downloader-

# 🎵 Pro Music Downloader (Termux Edition)

A powerful, command-line based Python script for Android (Termux) that downloads 100% pure studio audio without movie dialogues or intros. 

## ✨ Key Features
* **Double-Layer Filtration:** Uses iTunes API for metadata and duration, matching it with YouTube 'Topic' channels to ensure pure audio extraction.
* **Auto-Lyrics:** Automatically fetches and saves synced `.lrc` files from lrclib.net.
* **Smart Syncing:** Uses `termux-media-scan` to automatically push downloaded songs directly to the native Android Music Player.
* **Custom Bitrate:** Choose audio quality from 128kbps up to 320kbps.
* **Batch Download:** Download entire movie albums at once.

## 🛠️ Prerequisites
You need an Android phone with **Termux** and the **Termux:API** app installed.

1. Update packages and install dependencies:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python ffmpeg termux-api -y

2. Clone this repository and install Python requirements:
   pip install -r requirements.txt

How to Run:
   Simply start the script using Python:

   python music_bot.py
