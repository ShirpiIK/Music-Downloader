import os
import requests
import readline

DOWNLOAD_PATH = "/data/data/com.termux/files/home/storage/shared/Download/Myfy"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Navigation Exceptions
class GoHome(Exception): pass
class GoBack(Exception): pass

# Smart Input function
def ask(prompt_text):
    ans = input(prompt_text).strip().upper()
    if ans == '0': raise GoHome()
    if ans == 'B': raise GoBack()
    return ans

# Feature 1: Pagination (10 items per page)
def paginate_list(items, format_func, title):
    total = len(items)
    if total == 0:
        print("❌ Edhuvum kedaikkala!")
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
            else: print("❌ Thappana number!")
        else: print("❌ Thappana choice!")

def get_quality_choice():
    print("\n🎧 Audio Quality Choose Pannunga:")
    print("1. 128 kbps | 2. 160 kbps | 3. 192 kbps | 4. 256 kbps | 5. 320 kbps")
    q_choice = ask("Option (1-5) (Enter: B=Back, 0=Home): ")
    q_map = {'1': '128', '2': '160', '3': '192', '4': '256', '5': '320'}
    return q_map.get(q_choice, '192')

def download_track(track, bitrate):
    title = track.get('trackName', 'Unknown').replace('"', '').replace('/', '')
    artist = track.get('artistName', 'Unknown').replace('"', '').replace('/', '')
    album = track.get('collectionName', 'Unknown').replace('"', '').replace('/', '')
    cover_url = track.get('artworkUrl100', '').replace('100x100bb', '600x600bb')
    
    duration_ms = track.get('trackTimeMillis', 0)
    target_sec = duration_ms / 1000
    
    print(f"\n⏳ Downloading Pure Audio: {title}...")
    
    if cover_url:
        open("cover.jpg", "wb").write(requests.get(cover_url).content)
    
    search_query = f"ytsearch10:{title} {artist} Topic audio"
    min_d = target_sec - 10
    max_d = target_sec + 10
    
    os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k "
              f"--match-filter \"duration > {min_d} & duration < {max_d}\" "
              f"--max-downloads 1 -o 'temp.mp3' '{search_query}'")

    if not os.path.exists("temp.mp3"):
        print("⚠️ Exact Duration Match kedaikkala. Normal searching fallback...")
        os.system(f"yt-dlp -x --audio-format mp3 --audio-quality {bitrate}k --max-downloads 1 -o 'temp.mp3' 'ytsearch1:{title} {artist} Topic'")

    final_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.mp3"
    os.system(f"ffmpeg -y -i temp.mp3 -i cover.jpg -map 0:0 -map 1:0 -c copy -id3v2_version 3 -metadata title=\"{title}\" -metadata artist=\"{artist}\" -metadata album=\"{album}\" \"{final_path}\" -loglevel quiet")
    os.system(f"termux-media-scan '{final_path}'")
    
    # Feature 2: Robust Lyrics (LRC) logic
    print("🔍 Lyrics theduren...")
    lrc_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.lrc"
    try:
        lrc_data = requests.get("https://lrclib.net/api/search", params={"q": f"{title} {artist}"}).json()
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
                print("📜 Lyrics save aagiduchu!")
            else:
                print("⚠️ Lyrics DB-la kedaikkala.")
    except Exception:
        print("❌ Lyrics API Error.")

    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    if os.path.exists("cover.jpg"): os.remove("cover.jpg")
    print(f"✅ Success! '{title}' downloaded.")

# Feature 3: Smart Navigation Flow for Movies
def search_movie():
    while True:
        try:
            movie_name = ask("\n🎬 Padam peru (Enter: B=Back, 0=Home): ")
            data = requests.get(f"https://itunes.apple.com/search?term={movie_name}&entity=album&limit=50").json()
            albums = data['results']
            
            while True:
                try:
                    idx = paginate_list(albums, lambda i, a: f"{i+1}. {a['collectionName']} ({a['artistName']})", "Albums")
                    if idx is None: raise GoBack()
                    
                    album_id = albums[idx]['collectionId']
                    tracks = requests.get(f"https://itunes.apple.com/lookup?id={album_id}&entity=song").json()['results'][1:]
                    
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
                            return # Success aanadhum Home-kku poyidum
                        except GoBack: pass # Album List-kku thirumbum
                except GoBack: break # Movie search-kku thirumbum
        except GoBack: return # Main menu-kku thirumbum

# Smart Navigation Flow for Songs
def search_song():
    while True:
        try:
            song_name = ask("\n🎵 Paattu peru (Enter: B=Back, 0=Home): ")
            data = requests.get(f"https://itunes.apple.com/search?term={song_name}&entity=song&limit=50").json()
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
            print("1. Padam Search | 2. Paattu Search | 3. Exit")
            choice = input("\nChoice (1, 2 or 3): ").strip()
            
            if choice == '3':
                print("👋 Bye Bye!")
                break
            elif choice == '1': search_movie()
            elif choice == '2': search_song()
            else: print("❌ Thappana choice.")
        except GoHome:
            print("\n🏠 Home-kku thirumbugirom...")
        except KeyboardInterrupt:
            print("\n👋 App close aagudhu...")
            break
        except Exception as e:
            print(f"\n❌ Error. Home-kku pogirom.")
            
if __name__ == "__main__":
    main()
