import datetime
import os
import random
import requests

# Masukkan YouTube Data API Key Anda di sini
API_KEY = "AIzaSyBgD-FKVqhgxsLTs95jGXmClDEHIdRdWs0"

TEMP_FILE = "temp.txt"
OUTPUT_FILE = "populer.txt"

# Semua niche dikonfigurasi murni untuk wilayah dan konten Luar Negeri (Non-Indonesia)
NICHES = {
    "Dracin": {
        "query": "Chinese drama full movie sub english",
        "backup": "cdrama full episode english sub",
        "region": "US", 
        "lang": "en",
        "exclude": []
    },
    "News Internasional": {
        "query": "CNN News OR BBC News OR Fox News OR Al Jazeera full broadcast",
        "backup": "international breaking news live world update",
        "region": "US",  
        "lang": "en",
        "exclude": []
    },
    "Anime": {
        "query": "anime full movie english sub",
        "backup": "anime English dubbed full movie",
        "region": "US", 
        "lang": "en",
        "exclude": []
    },
    "Random": {
        "query": "global podcast full episode interview talkshow",
        "backup": "popular documentary full length English",
        "region": "US", 
        "lang": "en",
        "exclude": ["music", "song", "karaoke", "lyrics", "album", "remix", "dj", "cover", "indonesia", "indo"]
    },
    "Bola": {
        "query": "full match 90 minutes football highlights premier league",
        "backup": "champions league full match highlights",
        "region": "GB", 
        "lang": "en",
        "exclude": []
    },
    "Kartun": {
        "query": "SpongeBob SquarePants full episodes compilation OR Tom and Jerry full",
        "backup": "Looney Tunes full cartoon compilation",
        "region": "US", 
        "lang": "en",
        "exclude": []
    }
}

def load_used_urls():
    if os.path.exists(TEMP_FILE):
        with open(TEMP_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_used_url(url):
    with open(TEMP_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def search_youtube(query, region, lang, use_long_duration=True):
    url = "https://www.googleapis.com/youtube/v3/search"
    published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=180)).isoformat() + "Z"
    
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'order': 'viewCount',
        'publishedAfter': published_after,
        'regionCode': region,
        'relevanceLanguage': lang,
        'maxResults': 30, 
        'key': API_KEY
    }
    
    if use_long_duration:
        params['videoDuration'] = 'long'
        
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items']
    except Exception as e:
        pass
    return []

def get_unique_filtered_video(niche_name, config):
    used_urls = load_used_urls()
    
    # 4 Lapisan Pencarian (Anti Not Found)
    search_steps = [
        (config['query'], True),   # 1. Query Utama + Durasi Panjang
        (config['query'], False),  # 2. Query Utama bebas
        (config['backup'], True),  # 3. Query Cadangan + Durasi Panjang
        (config['backup'], False)  # 4. Query Cadangan bebas (Dijamin Ketemu)
    ]
    
    items = []
    for q, duration_flag in search_steps:
        items = search_youtube(q, config['region'], config['lang'], duration_flag)
        if items:
            break
            
    valid_videos = []
    if items:
        for item in items:
            title = item['snippet']['title'].lower()
            video_id = item['id']['videoId']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Cek kata yang dikecualikan (termasuk memblokir kata indonesia/indo jika ada)
            skip = False
            for bad_word in config['exclude']:
                if bad_word in title:
                    skip = True
                    break
            
            if not skip and url not in used_urls:
                valid_videos.append(url)
        
        if not valid_videos:
            for item in items:
                video_id = item['id']['videoId']
                url = f"https://www.youtube.com/watch?v={video_id}"
                valid_videos.append(url)
        
        if valid_videos:
            chosen_url = random.choice(valid_videos)
            save_used_url(chosen_url)
            return chosen_url
            
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def main():
    if API_KEY == "MASUKKAN_YOUTUBE_API_KEY_ANDA_DI_SINI":
        print("PERINGATAN: Harap masukkan YouTube API Key Anda terlebih dahulu!")
        return

    scraped_data = []
    print("Memproses pencarian video populer khusus luar negeri (Non-Indonesia)...")

    for niche, config in NICHES.items():
        print(f"Mengambil data untuk niche: {niche}...")
        url = get_unique_filtered_video(niche, config)
        scraped_data.append(f"{url} - {niche}")

    # Simpan ke file populer.txt
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in scraped_data:
            f.write(line + "\n")

    print(f"\nSelesai! Hasil luar negeri berhasil disimpan ke **{OUTPUT_FILE}**.")

if __name__ == "__main__":
    main()