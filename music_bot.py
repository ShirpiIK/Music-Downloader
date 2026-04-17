import os
import requests
import random
import readline
from ytmusicapi import YTMusic

DOWNLOAD_PATH = "/data/data/com.termux/files/home/storage/shared/Download/Myfy"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

class GoHome(Exception): pass
class GoBack(Exception): pass

# ---------------------------------------------------------
# 🔥 ANTI-CRASH SHIELD: Safe API Request Function 🔥
# ---------------------------------------------------------
def fetch_json(url, params=None):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1'
    ]
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    try:
        res = requests.get(url, params=params, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
        else:
            return None
    except Exception:
        return None

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
    
    c_title = title.split('(')[0].split('[')[0].split('-')[0].strip()
    c_artist = artist.split(',')[0].split('&')[0].strip()
    
    # 🎯 TARGET LANGUAGE DETECTION
    known_langs = ['tamil', 'telugu', 'hindi', 'malayalam', 'kannada', 'marathi', 'bengali', 'english']
    target_lang = ""
    for lang in known_langs:
        if lang in album.lower() or lang in title.lower():
            target_lang = lang
            break
    
    search_base = f"{c_title} {c_artist}"
    if target_lang:
        search_base = f"{c_title} {target_lang} {c_artist}"
    
    duration_ms = track.get('trackTimeMillis', 0)
    target_sec = int(duration_ms / 1000)
    
    lang_display = target_lang.capitalize() if target_lang else 'Standard'
    print(f"\n⏳ Downloading Audio: {title} ({lang_display} | Target: {target_sec}s)...")
    
    if cover_url:
        try: open("cover.jpg", "wb").write(requests.get(cover_url).content)
        except: pass
    
    ytmusic = YTMusic()
    try:
        print(f"🔍 Scanning YouTube Music for EXACT match...")
        search_results = ytmusic.search(search_base, filter="songs", limit=15)
        
        video_id = None
        if search_results:
            for result in search_results:
                res_sec = result.get('duration_seconds')
                if not res_sec and result.get('duration'):
                    try:
                        parts = str(result['duration']).split(':')
                        if len(parts) == 2: res_sec = int(parts[0])*60 + int(parts[1])
                        elif len(parts) == 3: res_sec = int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
                    except: pass
                
                if res_sec and abs(res_sec - target_sec) <= 5:
                    res_album = result.get('album', {}).get('name', '').lower() if result.get('album') else ''
                    res_title = result.get('title', '').lower()
                    
                    if target_lang:
                        if target_lang in res_album or target_lang in res_title:
                            video_id = result['videoId']
                            print(f"✅ Strict {target_lang.capitalize()} Audio Match Found! ({res_sec}s)")
                            break
                    else:
                        video_id = result['videoId']
                        print(f"✅ Exact Audio ID Match Found! ({res_sec}s)")
                        break
        
        if video_id:
            yt_url = f"https://music.youtube.com/watch?v={video_id}"
            os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --max-downloads 1 -o 'temp.mp3' '{yt_url}'")
        else:
            print("⚠️ API strict match missed. Trying standard YouTube search...")
            os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --match-filter \"duration >= {target_sec-5} & duration <= {target_sec+5}\" --max-downloads 1 -o 'temp.mp3' 'ytsearch15:{search_base} official audio'")
    except Exception as e:
        print(f"⚠️ API Error ({e}). Trying standard YouTube search...")
        os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --match-filter \"duration >= {target_sec-5} & duration <= {target_sec+5}\" --max-downloads 1 -o 'temp.mp3' 'ytsearch15:{search_base} official audio'")

    if not os.path.exists("temp.mp3"):
        print(f"❌ Error: Song download fail aagiduchu.")
        if os.path.exists("cover.jpg"): os.remove("cover.jpg")
        return

    final_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.mp3"
    os.system(f"ffmpeg -y -i temp.mp3 -i cover.jpg -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata title=\"{title}\" -metadata artist=\"{artist}\" -metadata album=\"{album}\" \"{final_path}\" -loglevel quiet")
    os.system(f"termux-media-scan '{final_path}'")
    
    # ---------------------------------------------------------
    # 🔥 ULTIMATE STRICT LYRICS MATCHER 🔥
    # ---------------------------------------------------------
    lrc_search_title = f"{c_title} {target_lang}".strip() if target_lang else c_title
    print(f"🔍 Searching for purely synced lyrics ({lrc_search_title})...")
    
    lrc_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.lrc"
    try:
        lrc_data = fetch_json("https://lrclib.net/api/search", {"track_name": lrc_search_title, "artist_name": c_artist})
        
        if not lrc_data or len(lrc_data) == 0:
            lrc_data = fetch_json("https://lrclib.net/api/search", {"track_name": c_title, "artist_name": c_artist})

        if lrc_data and isinstance(lrc_data, list) and len(lrc_data) > 0:
            synced_only_data = [item for item in lrc_data if item.get('syncedLyrics')]
            
            if not synced_only_data:
                print("⚠️ Synced Lyrics not found (Only plain text available, skipped).")
            else:
                selected_lrc = None
                
                if target_lang:
                    # STRICT MODE: Must match language and duration
                    for item in synced_only_data:
                        item_album = item.get('albumName', '').lower() if item.get('albumName') else ''
                        item_title = item.get('trackName', '').lower() if item.get('trackName') else ''
                        item_dur = item.get('duration', 0)
                        
                        if (target_lang in item_album or target_lang in item_title) and (item_dur and abs(item_dur - target_sec) <= 5):
                            selected_lrc = item
                            break
                    
                    if not selected_lrc:
                        for item in synced_only_data:
                            item_album = item.get('albumName', '').lower() if item.get('albumName') else ''
                            item_title = item.get('trackName', '').lower() if item.get('trackName') else ''
                            if target_lang in item_album or target_lang in item_title:
                                selected_lrc = item
                                break
                else:
                    # NORMAL MODE: Just match duration
                    for item in synced_only_data:
                        item_dur = item.get('duration', 0)
                        if item_dur and abs(item_dur - target_sec) <= 5:
                            selected_lrc = item
                            break
                    
                    if not selected_lrc:
                        selected_lrc = synced_only_data[0]
                        
                if selected_lrc:
                    open(lrc_path, 'w', encoding='utf-8').write(selected_lrc['syncedLyrics'])
                    os.system(f"termux-media-scan '{lrc_path}'")
                    print(f"📜 {lang_display} Synced Lyrics saved successfully!")
                else:
                    if target_lang:
                        print(f"⚠️ {lang_display} Synced Lyrics not found in database. Skipped to prevent wrong language.")
                    else:
                        print("⚠️ Lyrics not found in database.")
        else:
            print("⚠️ Lyrics not found in database.")
    except Exception:
        print(f"❌ Lyrics Error: Skipped.")

    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    if os.path.exists("cover.jpg"): os.remove("cover.jpg")
    print(f"✅ Success! '{title}' downloaded.")

def download_url():
    try:
        url = ask("\n🔗 Paste YouTube/Soundcloud URL (Playlist or Song) (Enter: B=Back, 0=Home): ")
        bitrate = get_quality_choice()
        
        print(f"\n⏳ Analyzing URL and starting download...")
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
            
            # Limited to 20 to avoid rate limits
            data = fetch_json("https://itunes.apple.com/search", {"term": movie_name, "entity": "album", "limit": 20, "country": "IN"})
            albums = data.get('results', []) if data else []
            
            if not albums:
                print("❌ No results found or API blocked. Try again in a few minutes or use Option 2.")
                continue
                
            while True:
                try:
                    idx = paginate_list(albums, lambda i, a: f"{i+1}. {a.get('collectionName', 'Unknown')} ({a.get('artistName', 'Unknown')})", "Albums")
                    if idx is None: raise GoBack()
                    
                    album_id = albums[idx]['collectionId']
                    
                    tracks_data = fetch_json("https://itunes.apple.com/lookup", {"id": album_id, "entity": "song", "country": "IN"})
                    tracks = tracks_data.get('results', [])[1:] if tracks_data else []
                    
                    while True:
                        try:
                            print("\n🎶 Songs List:")
                            for i, t in enumerate(tracks): print(f"{i+1}. {t.get('trackName', 'Unknown')}")
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
            
            data = fetch_json("https://itunes.apple.com/search", {"term": song_name, "entity": "song", "limit": 25, "country": "IN"})
            songs = data.get('results', []) if data else []
            
            if not songs:
                print("❌ No results found or API blocked. Try again in a few minutes.")
                continue
                
            while True:
                try:
                    idx = paginate_list(songs, lambda i, t: f"{i+1}. {t.get('trackName', 'Unknown')} - {t.get('artistName', 'Unknown')}", "Songs")
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
            print(f"\n❌ ALERT! Critical Error: {e}")
            print("🏠 Returning to Home Menu...")
            
if __name__ == "__main__":
    main()
