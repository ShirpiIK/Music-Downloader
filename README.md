# 🎵 Myfy - Pro Music Downloader (Termux Edition)

Myfy is a powerful, command-line based pure music downloader built specifically for Android devices using Termux. Unlike standard YouTube downloaders, Myfy utilizes the **YouTube Music API** to bypass lyrical videos, dialogue intros, and fan covers, ensuring you get 100% official, studio-quality audio every time.

## ✨ Key Features

* **🎧 Pure Official Audio:** Directly hits the YouTube Music database (`ytmusicapi`) to fetch exact original tracks.
* **🏷️ Auto Meta-Tagging:** Automatically embeds high-quality Cover Art, Song Title, Artist, and Album Name into the MP3 file using `ffmpeg`.
* **📜 Synced Lyrics:** Auto-fetches and saves `.lrc` files from LRCLIB, enabling synced lyrics on compatible Android music players.
* **📋 Smart Search UI:** Interactive, paginated command-line interface. Search accurately using the Apple Music (iTunes) database.
* **🔗 Link / Playlist Support:** Paste any YouTube or Soundcloud URL (single track or full playlist) to download them in your preferred audio quality.
* **🔄 Auto Media Scan:** Instantly pushes downloaded songs to your Android Music Player library without requiring a device reboot.
* **🎚️ Custom Bitrate:** Choose your preferred audio quality (128kbps, 160kbps, 192kbps, 256kbps, or 320kbps).

---

## 🛠️ Installation & Setup (For Termux)

Follow these steps carefully to set up Myfy on your Android device.

### 1. Grant Storage Permission
Allow Termux to access your internal storage so it can save the downloaded songs:

```bash
termux-setup-storage
```

### 2. Install Required System Packages
Update your system and install Python along with FFmpeg (used for audio conversion and metadata tagging):

```bash
pkg update && pkg upgrade -y
pkg install python ffmpeg -y
```

### 3. Install Python Modules
Install the required third-party libraries that power the search and download engines:

```bash
pip install yt-dlp requests ytmusicapi
```

### 4. Clone & Run
Clone this repository and start the application:

```bash
git clone https://github.com/ShirpiIK/Music-Downloader
cd Music-Downloader
python music_bot.py
```

---

## 🚀 How to Use & Query Examples

Run the script using `python music_bot.py`. You will be greeted with a Main Menu offering 4 options:

### Option 1: Search by Movie/Album
* **How it works:** Uses the iTunes API to fetch the official album data.
* **Query Example:** Type `Love Insurance Kompany` or `Leo`.
* **Action:** It lists all songs from that specific movie. You can download a single song (e.g., type `2`), multiple songs (e.g., `1,3,4`), or the entire album (type `A`).

### Option 2: Search by Song
* **How it works:** Directly searches for a specific track.
* **Query Example:** Type `Adaavadi` or `Hukum`.
* **Action:** It displays the top search results. Select the number, choose your bitrate, and the pure audio will be downloaded via the YouTube Music database.

### Option 3: Download via Link
* **How it works:** Direct download using `yt-dlp`.
* **Query Example:** Paste a `https://youtube.com/playlist?...` link.
* **Action:** Automatically analyzes the URL, fetches all metadata, downloads the entire playlist, and syncs it to your device.

---

## 📂 Storage & Media Integration

* **Folder Location:** All downloaded MP3 and LRC files are saved directly to your phone's internal storage in this directory:
  `Internal Storage/Download/Myfy`
  *(The script automatically creates this folder if it doesn't exist).*

* **Music Player Integration:** Android OS sometimes ignores new files downloaded via the terminal. Myfy solves this using a built-in Termux command
  ```base
  termux-media-scan
  ```
   Once a song is downloaded, this command forcefully pings the Android Media Scanner, ensuring your new tracks appear instantly in apps like Samsung Music, Musicolet, or Poweramp.
