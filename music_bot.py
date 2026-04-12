import os
import requests
import readline
from ytmusicapi import YTMusic

DOWNLOAD_PATH = "/data/data/com.termux/files/home/storage/shared/Download/Myfy"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

class GoHome(Exception): pass
class GoBack(Exception): pass

def ask(prompt_text):
    ans = input(prompt_text).strip().upper()
    if ans == '0': raise GoHome()
    if ans == 'B': raise GoBack()
    return ans

def paginate_list(items, format_func, title):
    total = len(items)
    if total == 0:
        print("❌ Nothing found!")
        return None
    
    page = 0
    limit = 10
    while True:
        start = page * limit
        end = min(start + limit, total)
        print(f"\n📑 {title} (Page {page+1} / {(total-1)//limit + 1}):")
        for i in range(start, end):
            print(format_func(i, items[i]))
        
        print("-" * 35)
        opts = []
        if end < total: opts.append("'N' Next Page")
        if page > 0: opts.append("'P' Prev Page")
        
        prompt = f"👉 Number | {', '.join(opts)} | 'B' Back | '0' Home: "
        choice = input(prompt).strip().upper()
        
        if choice == '0': raise GoHome()
        if choice == 'B': raise GoBack()
        if choice == 'N' and end < total: page += 1
        elif choice == 'P' and page > 0: page -= 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < total: return idx
            else: print("❌ Invalid number!")
        else: print("❌ Invalid choice!")

def get_quality_choice():
    print("\n🎧 Choose Audio Quality:")
    print("1. 128 kbps | 2. 160 kbps | 3. 192 kbps | 4. 256 kbps | 5. 320 kbps")
    q_choice = ask("Option (1-5) (Enter: B=Back, 0=Home): ")
    q_map = {'1': '128', '2': '160', '3': '192', '4': '256', '5': '320'}
    return q_map.get(q_choice, '192')

def download_track(track, bitrate):
    title = track.get('trackName', 'Unknown').replace('"', '').replace('/', '')
    artist = track.get('artistName', 'Unknown').replace('"', '').replace('/', '')
    album = track.get('collectionName', 'Unknown').replace('"', '').replace('/', '')
    cover_url = track.get('artworkUrl100', '').replace('100x100bb', '600x600bb')
    
    # MAGIC STRING CLEANER
    c_title = title.split('(')[0].split('[')[0].split('-')[0].strip()
    c_artist = artist.split(',')[0].split('&')[0].strip()
    c_album = album.split('(')[0].split('[')[0].split('-')[0].strip()
    
    search_base = f"{c_title} {c_artist}"
    
    print(f"\n⏳ Downloading Pure Audio: {c_title}...")
    
    if cover_url:
        open("cover.jpg", "wb").write(requests.get(cover_url).content)
    
    # PRO METHOD: YouTube Music API (Directly hits the music database)
    ytmusic = YTMusic()
    try:
        print("🔍 Scanning YouTube Music database...")
        search_results = ytmusic.search(search_base, filter="songs", limit=1)
        
        if search_results and len(search_results) > 0:
            video_id = search_results[0]['videoId']
            yt_url = f"https://music.youtube.com/watch?v={video_id}"
            print(f"✅ Exact Official Audio found via API! Starting download...")
            os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --max-downloads 1 -o 'temp.mp3' '{yt_url}'")
        else:
            # BACKUP METHOD: If API fails, standard search without duration limits
            print("⚠️ API miss. Trying standard YouTube audio fetch...")
            os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --max-downloads 1 -o 'temp.mp3' 'ytsearch1:{search_base} official audio'")
    except Exception as e:
        print("⚠️ API Error. Trying standard YouTube audio fetch...")
        os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --max-downloads 1 -o 'temp.mp3' 'ytsearch1:{search_base} official audio'")

    # FINAL SAFETY
    if not os.path.exists("temp.mp3"):
        print(f"❌ Error: YouTube-la indha paattu kedaikkala. Download fail aagiduchu.")
        if os.path.exists("cover.jpg"): os.remove("cover.jpg")
        return

    final_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.mp3"
    os.system(f"ffmpeg -y -i temp.mp3 -i cover.jpg -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata title=\"{title}\" -metadata artist=\"{artist}\" -metadata album=\"{album}\" \"{final_path}\" -loglevel quiet")
    os.system(f"termux-media-scan '{final_path}'")
    
    print("🔍 Searching for lyrics...")
    lrc_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.lrc"
    try:
        lrc_data = requests.get("https://lrclib.net/api/search", params={"track_name": c_title, "artist_name": c_artist, "album_name": c_album}).json()
        found_lyrics = False
        if isinstance(lrc_data, list) and len(lrc_data) > 0:
            for item in lrc_data:
                if item.get('syncedLyrics'):
                    open(lrc_path, 'w', encoding='utf-8').write(item['syncedLyrics'])
                    found_lyrics = True
                    break
            if not found_lyrics and lrc_data[0].get('plainLyrics'):
                open(lrc_path, 'w', encoding='utf-8').write(lrc_data[0]['plainLyrics'])
                found_lyrics = True
                
            if found_lyrics:
                os.system(f"termux-media-scan '{lrc_path}'")
                print("📜 Lyrics saved successfully!")
            else:
                print("⚠️ Lyrics not found for this song in the database.")
        else:
            print("⚠️ Lyrics not found for this song in the database.")
    except Exception:
        print("❌ Lyrics API Error. Skipping lyrics.")

    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    if os.path.exists("cover.jpg"): os.remove("cover.jpg")
    print(f"✅ Success! '{title}' downloaded.")

def download_url():
    try:
        url = ask("\n🔗 Paste YouTube/Soundcloud URL (Playlist or Song) (Enter: B=Back, 0=Home): ")
        bitrate = get_quality_choice()
        
        print(f"\n⏳ Analyzing URL and starting download. If it's a playlist, this might take a while...")
        
        output_template = f"{DOWNLOAD_PATH}/%(title)s_{bitrate}k.%(ext)s"
        
        cmd = (f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k "
               f"--embed-thumbnail --add-metadata "
               f"-o '{output_template}' '{url}'")
        
        os.system(cmd)
        
        print("\n🔄 Syncing new files with Android Music Player...")
        os.system(f"termux-media-scan -r '{DOWNLOAD_PATH}'")
        
        print("✅ URL/Playlist download complete!")
        
    except GoBack: return
    except GoHome: raise GoHome()

def search_movie():
    while True:
        try:
            movie_name = ask("\n🎬 Enter Movie Name (Enter: B=Back, 0=Home): ")
            data = requests.get(f"https://itunes.apple.com/search?term={movie_name}&entity=album&limit=50&country=IN").json()
            albums = data['results']
            
            while True:
                try:
                    idx = paginate_list(albums, lambda i, a: f"{i+1}. {a['collectionName']} ({a['artistName']})", "Albums")
                    if idx is None: raise GoBack()
                    
                    album_id = albums[idx]['collectionId']
                    tracks = requests.get(f"https://itunes.apple.com/lookup?id={album_id}&entity=song&country=IN").json()['results'][1:]
                    
                    while True:
                        try:
                            print("\n🎶 Songs List:")
                            for i, t in enumerate(tracks): print(f"{i+1}. {t['trackName']}")
                            dl_choice = ask("\n📥 'A' (All) or Numbers (eg: 1,3) (Enter: B=Back, 0=Home): ").upper()
                            bitrate = get_quality_choice()
                            
                            if dl_choice == 'A':
                                for t in tracks: download_track(t, bitrate)
                            else:
                                selections = [int(x.strip())-1 for x in dl_choice.split(',')]
                                for s in selections: download_track(tracks[s], bitrate)
                            return 
                        except GoBack: pass 
                except GoBack: break 
        except GoBack: return 

def search_song():
    while True:
        try:
            song_name = ask("\n🎵 Enter Song Name (Enter: B=Back, 0=Home): ")
            data = requests.get(f"https://itunes.apple.com/search?term={song_name}&entity=song&limit=50&country=IN").json()
            songs = data['results']
            
            while True:
                try:
                    idx = paginate_list(songs, lambda i, t: f"{i+1}. {t['trackName']} - {t['artistName']}", "Songs")
                    if idx is None: raise GoBack()
                    
                    bitrate = get_quality_choice()
                    download_track(songs[idx], bitrate)
                    return 
                except GoBack: break 
        except GoBack: return

def main():
    while True:
        try:
            print("\n" + "="*45 + "\n🎵 Pro Music Downloader (Ultimate UI) 🎵\n" + "="*45)
            print("1. Search by Movie/Album")
            print("2. Search by Song")
            print("3. Download via Link (Playlist/Song)")
            print("4. Exit")
            choice = input("\nChoice (1, 2, 3 or 4): ").strip()
            
            if choice == '4':
                print("👋 Exiting App. Bye Bye!")
                break
            elif choice == '1': search_movie()
            elif choice == '2': search_song()
            elif choice == '3': download_url()
            else: print("❌ Invalid choice. Please try again.")
        except GoHome:
            print("\n🏠 Returning to Home Menu...")
        except KeyboardInterrupt:
            print("\n👋 Process interrupted. Exiting App...")
            break
        except Exception as e:
            print(f"\n❌ An error occurred. Returning to Home Menu.")
            
if __name__ == "__main__":
    main()                    
