import os
import requests
import random
import time
import readline
import difflib
from ytmusicapi import YTMusic

DOWNLOAD_PATH = "/data/data/com.termux/files/home/storage/shared/Download/Myfy"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

class GoHome(Exception): pass
class GoBack(Exception): pass

def fetch_json(url, params=None):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15'
    ]
    if params is not None:
        params['nocache'] = int(time.time() * 1000)
        if params.get('country') == 'IN':
            params['country'] = random.choice(['IN', 'US', 'GB']) 
            
    headers = {'User-Agent': random.choice(user_agents), 'Accept': 'application/json', 'Referer': 'https://music.apple.com/'}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=15)
        if res.status_code == 200 and 'newNullResponse' not in res.text: return res.json()
        return None
    except: return None

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
        for i in range(start, end): print(format_func(i, items[i]))
        print("-" * 35)
        opts = []
        if end < total: opts.append("'N' Next Page")
        if page > 0: opts.append("'P' Prev Page")
        choice = input(f"👉 Number | {', '.join(opts)} | 'B' Back | '0' Home: ").strip().upper()
        
        if choice == '0': raise GoHome()
        if choice == 'B': raise GoBack()
        if choice == 'N' and end < total: page += 1
        elif choice == 'P' and page > 0: page -= 1
        elif choice.isdigit() and 0 <= int(choice)-1 < total: return int(choice) - 1
        else: print("❌ Invalid choice!")

def get_quality_choice():
    print("\n🎧 Choose Audio Quality:")
    print("1. 128 kbps | 2. 160 kbps | 3. 192 kbps | 4. 256 kbps | 5. 320 kbps")
    q_choice = ask("Option (1-5) (Enter: B=Back, 0=Home): ")
    return {'1':'128', '2':'160', '3':'192', '4':'256', '5':'320'}.get(q_choice, '192')

def download_track(track, bitrate):
    title = track.get('trackName', 'Unknown').replace('"', '').replace('/', '')
    artist = track.get('artistName', 'Unknown').replace('"', '').replace('/', '')
    album = track.get('collectionName', 'Unknown').replace('"', '').replace('/', '')
    cover_url = track.get('artworkUrl100', '').replace('100x100bb', '600x600bb')
    
    c_title = title.split('(')[0].split('[')[0].split('-')[0].strip()
    c_artist = artist.split(',')[0].split('&')[0].strip()
    
    # 🔥 FIX: Cut the album name cleanly to use in search (e.g., "Ko (Original Soundtrack)" -> "Ko")
    c_album = album.split('(')[0].split('-')[0].split('[')[0].strip()
    
    known_langs = ['tamil', 'telugu', 'hindi', 'malayalam', 'kannada', 'marathi', 'bengali', 'english']
    target_lang = ""
    for lang in known_langs:
        if lang in album.lower() or lang in title.lower():
            target_lang = lang
            break
            
    # 🔥 FIX: Search Base now strictly includes the Movie Name!
    search_base = f"{title} {c_album} {c_artist}"
    if target_lang and target_lang not in title.lower() and target_lang not in c_album.lower():
        search_base += f" {target_lang}"
        
    duration_ms = track.get('trackTimeMillis', 0)
    target_sec = int(duration_ms / 1000)
    
    lang_display = target_lang.capitalize() if target_lang else 'Standard'
    print(f"\n⏳ Downloading Audio: {title} ({lang_display} | Target: {target_sec}s)...")
    
    if cover_url:
        try: open("cover.jpg", "wb").write(requests.get(cover_url).content)
        except: pass
    
    ytmusic = YTMusic()
    try:
        print(f"🔍 Analyzing search results with Movie Name & High Confidence Score...")
        search_results = ytmusic.search(search_base, filter="songs", limit=15)
        
        video_id = None
        best_score = 0
        
        if search_results:
            for result in search_results:
                res_sec = result.get('duration_seconds')
                if not res_sec and result.get('duration'):
                    try: res_sec = sum(x * int(t) for x, t in zip([60, 1], str(result['duration']).split(":")))
                    except: res_sec = 0
                
                if res_sec and abs(res_sec - target_sec) <= 5:
                    res_album = result.get('album', {}).get('name', '').lower() if result.get('album') else ''
                    res_title = result.get('title', '').lower()
                    
                    lang_match = True
                    if target_lang:
                        if target_lang not in res_title and target_lang not in res_album:
                            lang_match = False
                            
                    if lang_match:
                        # 🔥 FIX: Similarity Score checks both title and now requires 75% minimum!
                        score = difflib.SequenceMatcher(None, c_title.lower(), res_title.split('(')[0].strip()).ratio()
                        if score > best_score:
                            best_score = score
                            video_id = result['videoId']
                            
            # 🔥 FIX: Increased threshold to 0.75 (75%)
            if video_id and best_score < 0.75:
                print(f"⚠️ Confidence Low ({int(best_score*100)}%). Strict verification failed.")
                video_id = None 
                
        if video_id:
            print(f"✅ High Confidence Match Found! ({int(best_score*100)}%)")
            yt_url = f"https://music.youtube.com/watch?v={video_id}"
            os.system(f"yt-dlp --newline -x --audio-format mp3 --audio-quality {bitrate}k -o 'temp.mp3' '{yt_url}'")
        else:
            print("⚠️ Strict match missed. Trying direct YouTube Search fallback...")
            os.system(f"yt-dlp --newline -x --audio-format mp3 --audio-quality {bitrate}k --match-filter \"duration >= {target_sec-5} & duration <= {target_sec+5}\" --max-downloads 1 -o 'temp.mp3' 'ytsearch15:{search_base} official audio'")
    except Exception as e:
        print(f"❌ Error: {e}")

    if not os.path.exists("temp.mp3"):
        print(f"❌ Error: Song download fail aagiduchu.")
        if os.path.exists("cover.jpg"): os.remove("cover.jpg")
        return

    final_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.mp3"
    os.system(f"ffmpeg -y -i temp.mp3 -i cover.jpg -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata title=\"{title}\" -metadata artist=\"{artist}\" -metadata album=\"{album}\" \"{final_path}\" -loglevel quiet")
    os.system(f"termux-media-scan '{final_path}'")
    
    # ---------------------------------------------------------
    # 🔥 ULTIMATE SCENARIO-BASED LYRICS MATCHER
    # ---------------------------------------------------------
    print(f"🔍 Searching for synced lyrics ({title})...")
    lrc_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.lrc"
    
    try:
        lrc_data = fetch_json("https://lrclib.net/api/search", {"track_name": title, "artist_name": c_artist})
        
        if not lrc_data or len(lrc_data) == 0:
            lrc_data = fetch_json("https://lrclib.net/api/search", {"track_name": c_title, "artist_name": c_artist})

        if not lrc_data or len(lrc_data) == 0:
            print("⚠️ Artist match failed. Searching by Track Name only...")
            lrc_data = fetch_json("https://lrclib.net/api/search", {"track_name": c_title})

        if lrc_data and isinstance(lrc_data, list) and len(lrc_data) > 0:
            synced_only_data = [item for item in lrc_data if item.get('syncedLyrics')]
            if not synced_only_data:
                print("⚠️ Synced Lyrics not found (Only plain text available, skipped).")
            else:
                selected_lrc = None
                if target_lang:
                    for item in synced_only_data:
                        item_album = item.get('albumName', '').lower() if item.get('albumName') else ''
                        item_title = item.get('trackName', '').lower() if item.get('trackName') else ''
                        item_dur = item.get('duration', 0)
                        if (target_lang in item_album or target_lang in item_title) and (item_dur and abs(item_dur - target_sec) <= 8):
                            selected_lrc = item
                            break
                if not selected_lrc:
                    for item in synced_only_data:
                        item_dur = item.get('duration', 0)
                        if item_dur and abs(item_dur - target_sec) <= 8:
                            selected_lrc = item
                            break
                if not selected_lrc:
                    print("⚠️ Strict match failed. Taking the best available synced lyric...")
                    selected_lrc = synced_only_data[0]
                        
                if selected_lrc:
                    open(lrc_path, 'w', encoding='utf-8').write(selected_lrc['syncedLyrics'])
                    os.system(f"termux-media-scan '{lrc_path}'")
                    print(f"📜 Synced Lyrics saved successfully!")
                else: print("⚠️ Lyrics not found in database.")
        else: print("⚠️ Lyrics not found in database.")
    except Exception as e: print(f"❌ Lyrics Error: Skipped.")

    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    if os.path.exists("cover.jpg"): os.remove("cover.jpg")
    print(f"✅ Success! '{title}' downloaded.")

def download_url():
    try:
        url = ask("\n🔗 Paste YouTube/Soundcloud URL (Playlist or Song) (Enter: B=Back, 0=Home): ")
        bitrate = get_quality_choice()
        print(f"\n⏳ Analyzing URL and starting download...")
        output_template = f"{DOWNLOAD_PATH}/%(title)s_{bitrate}k.%(ext)s"
        os.system(f"yt-dlp --newline -x --audio-format mp3 --audio-quality {bitrate}k --embed-thumbnail --add-metadata -o '{output_template}' '{url}'")
        os.system(f"termux-media-scan -r '{DOWNLOAD_PATH}'")
        print("✅ URL/Playlist download complete!")
    except GoBack: return
    except GoHome: raise GoHome()

def search_movie():
    while True:
        try:
            movie_name = ask("\n🎬 Enter Movie Name (Enter: B=Back, 0=Home): ")
            data = fetch_json("https://itunes.apple.com/search", {"term": movie_name, "entity": "album", "limit": 50, "country": "IN"})
            albums = data.get('results', []) if data else []
            if not albums:
                print("❌ No results found or API blocked. Try again in a few minutes or use Option 2.")
                continue
            while True:
                try:
                    idx = paginate_list(albums, lambda i, a: f"{i+1}. {a.get('collectionName', 'Unknown')} ({a.get('artistName', 'Unknown')})", "Albums")
                    if idx is None: raise GoBack()
                    tracks_data = fetch_json("https://itunes.apple.com/lookup", {"id": albums[idx]['collectionId'], "entity": "song", "country": "IN"})
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
                                for s in [int(x.strip())-1 for x in dl_choice.split(',')]: download_track(tracks[s], bitrate)
                            return 
                        except GoBack: pass 
                except GoBack: break 
        except GoBack: return 

def search_song():
    while True:
        try:
            song_name = ask("\n🎵 Enter Song Name (Enter: B=Back, 0=Home): ")
            data = fetch_json("https://itunes.apple.com/search", {"term": song_name, "entity": "song", "limit": 50, "country": "IN"})
            songs = data.get('results', []) if data else []
            if not songs:
                print("❌ No results found or API blocked.")
                continue
            while True:
                try:
                    idx = paginate_list(songs, lambda i, t: f"{i+1}. {t.get('trackName', 'Unknown')} - {t.get('artistName', 'Unknown')}", "Songs")
                    if idx is None: raise GoBack()
                    download_track(songs[idx], get_quality_choice())
                    return 
                except GoBack: break 
        except GoBack: return

def main():
    while True:
        try:
            print("\n" + "="*45 + "\n🎵 Pro Music Downloader (Ultimate UI) 🎵\n" + "="*45)
            print("1. Search by Movie/Album\n2. Search by Song\n3. Download via Link\n4. Exit")
            choice = input("\nChoice (1, 2, 3 or 4): ").strip()
            if choice == '4':
                print("👋 Exiting App. Bye Bye!")
                break
            elif choice == '1': search_movie()
            elif choice == '2': search_song()
            elif choice == '3': download_url()
            else: print("❌ Invalid choice.")
        except GoHome: print("\n🏠 Returning to Home Menu...")
        except KeyboardInterrupt: break
        except Exception as e: print(f"\n❌ ALERT! Critical Error: {e}")
            
if __name__ == "__main__": main()
