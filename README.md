# 🎵 Myfy - Pro Music Downloader (Termux Edition)

A powerful, CLI-based pure music downloader built specifically for Android (Termux). Myfy bypasses normal YouTube search algorithms by utilizing the **YouTube Music API**, ensuring you get 100% pure official audio without any lyrical video dialogues or intro/outro interruptions.

## ✨ Key Features

* **🎧 Pure Official Audio:** Directly hits the YouTube Music database (`ytmusicapi`) to fetch exact studio-quality audio.
* **🏷️ Auto Meta-Tagging:** Automatically embeds Cover Art, Song Title, Artist, and Album Name into the MP3 file using `ffmpeg`.
* **📜 Synced Lyrics:** Auto-fetches and saves `.lrc` (synced lyrics) files from LRCLIB for compatible music players.
* **📋 Smart Search UI:** Interactive command-line interface with pagination. Search directly using Apple Music (iTunes API) data.
* **🔗 Link / Playlist Downloader:** Paste any YouTube or Soundcloud URL (single track or entire playlist) to download them in your preferred bitrate.
* **🔄 Auto Media Scan:** Instantly pushes downloaded songs to your Android Music Player using `termux-media-scan`.
* **🎚️ Custom Bitrate:** Choose your preferred audio quality (128kbps to 320kbps).

---

## 🛠️ Installation & Setup (Termux)

Follow these steps carefully to set up Myfy on your Android device using Termux.

### 1. Grant Storage Permission
First, allow Termux to access your internal storage so it can save the songs.
```bash
termux-setup-storage


### 2. Install Required System Packages
Update your system and install Python and FFmpeg (used for audio conversion and metadata tagging).
