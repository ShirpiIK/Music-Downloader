import os
import requests
import readline

DOWNLOAD_PATH = "/data/data/com.termux/files/home/storage/shared/Download/Myfy"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

class GoHome(Exception):
    pass

def ask(prompt_text):
    ans = input(prompt_text).strip()
    if ans == '0':
        raise GoHome()
    return ans

def get_quality_choice():
    print("\n🎧 Audio Quality Choose Pannunga:")
    print("1. 128 kbps | 2. 160 kbps | 3. 192 kbps | 4. 256 kbps | 5. 320 kbps")
    q_map = {'1': '128', '2': '160', '3': '192', '4': '256', '5': '320'}
    q_choice = ask("Option (1-5) (or) Home(Enter: 0): ")
    return q_map.get(q_choice, '192')

def download_track(track, bitrate):
    title = track.get('trackName', 'Unknown').replace('"', '').replace('/', '')
    artist = track.get('artistName', 'Unknown').replace('"', '').replace('/', '')
    album = track.get('collectionName', 'Unknown').replace('"', '').replace('/', '')
    cover_url = track.get('artworkUrl100', '').replace('100x100bb', '600x600bb')
    
    duration_ms = track.get('trackTimeMillis', 0)
    target_sec = duration_ms / 1000
    
    print(f"\n⏳ Pure Studio Audio (Target: ~{int(target_sec)}s) theduren: {title}...")
    
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
    
    # Lyrics (LRC) logic
    lrc_path = f"{DOWNLOAD_PATH}/{title}_{bitrate}k.lrc"
    try:
        lrc_data = requests.get("https://lrclib.net/api/search", params={"q": f"{title} {artist}"}).json()
        if lrc_data and isinstance(lrc_data, list):
            lrc_content = lrc_data[0].get('syncedLyrics') or lrc_data[0].get('plainLyrics')
            if lrc_content:
                open(lrc_path, 'w', encoding='utf-8').write(lrc_content)
                os.system(f"termux-media-scan '{lrc_path}'")
                print("📜 Lyrics save aagiduchu!")
    except: pass

    if os.path.exists("temp.mp3"): os.remove("temp.mp3")
    if os.path.exists("cover.jpg"): os.remove("cover.jpg")
    print(f"✅ Success! '{title}' ippa pure quality-la irukkum.")

def main():
    while True:
        try:
            print("\n" + "="*45 + "\n🎵 Pro Music Downloader (Advanced Filter) 🎵\n" + "="*45)
            print("1. Padam Search | 2. Paattu Search | 3. Exit")
            choice = input("\nChoice (1, 2 or 3): ").strip()
            
            if choice == '3': break
            elif choice == '1':
                movie_name = ask("\nPadam peru (or) Home(Enter: 0): ")
                data = requests.get(f"https://itunes.apple.com/search?term={movie_name}&entity=album&limit=5").json()
                if data['resultCount'] == 0: 
                    print("❌ Padam kedaikkala!")
                    continue
                for i, alb in enumerate(data['results']): 
                    print(f"{i+1}. {alb['collectionName']} ({alb['artistName']})")
                idx = int(ask("\nNumber (or) Home(Enter: 0): ")) - 1
                tracks = requests.get(f"https://itunes.apple.com/lookup?id={data['results'][idx]['collectionId']}&entity=song").json()['results'][1:]
                
                print("\n🎶 Songs List:")
                for i, track in enumerate(tracks):
                    print(f"{i+1}. {track['trackName']}")
                
                dl_choice = ask("\nOption 'A' (All) or Numbers (eg: 1,3) (or) Home(Enter: 0): ").upper()
                bitrate = get_quality_choice()
                if dl_choice == 'A' or dl_choice == "'A'":
                    for t in tracks: download_track(t, bitrate)
                else:
                    for s in [int(x)-1 for x in dl_choice.split(',')]: download_track(tracks[s], bitrate)
            elif choice == '2':
                song_name = ask("\nPaattu peru (or) Home(Enter: 0): ")
                data = requests.get(f"https://itunes.apple.com/search?term={song_name}&entity=song&limit=7").json()
                if data['resultCount'] == 0: 
                    print("❌ Paattu kedaikkala!")
                    continue
                for i, t in enumerate(data['results']): 
                    print(f"{i+1}. {t['trackName']} - {t['artistName']}")
                idx = int(ask("\nNumber (or) Home(Enter: 0): ")) - 1
                download_track(data['results'][idx], get_quality_choice())
        except GoHome: continue
        except Exception: print("\n❌ Error. Home-kku pogirom."); continue

if __name__ == "__main__":
    main()
