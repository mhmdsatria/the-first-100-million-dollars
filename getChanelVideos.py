import json
import os
import re
import urllib.error
import urllib.request

API_KEY = "AIzaSyBgD-FKVqhgxsLTs95jGXmClDEHIdRdWs0"

def extract_video_id(url: str) -> str:
    match = re.search(r'(?:v=|\/embed\/|\/shorts\/|\/v\/|https?:\/\/youtu\.be\/)([0-9A-Za-z_-]{11})', url)
    return match.group(1) if match else None

def get_videos_from_video_id(video_id: str, api_key: str):
    try:
        # 1. Dapatkan Channel ID & Nama Channel dari Video ID
        url_video = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
        req = urllib.request.urlopen(url_video)
        data_video = json.loads(req.read().decode('utf-8'))
        
        items = data_video.get('items', [])
        if not items:
            print(f"[!] Video ID '{video_id}' nggak ditemukan.")
            return []
        
        snippet_video = items[0]['snippet']
        channel_id = snippet_video['channelId']
        fallback_channel_title = snippet_video.get('channelTitle', 'Tanpa Nama Channel').replace('\n', ' ').strip()

        # 2. Dapatkan ID playlist 'uploads'
        url_channel = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
        req = urllib.request.urlopen(url_channel)
        data_channel = json.loads(req.read().decode('utf-8'))
        
        channel_items = data_channel.get('items', [])
        if not channel_items:
            print(f"[!] Channel dari Video ID '{video_id}' nggak ditemukan.")
            return []

        uploads_playlist_id = channel_items[0]['contentDetails']['relatedPlaylists']['uploads']

        # 3. Dapatkan 10 video terbaru
        url_playlist = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults=10&key={api_key}"
        req = urllib.request.urlopen(url_playlist)
        data_playlist = json.loads(req.read().decode('utf-8'))

        videos = []
        for item in data_playlist.get('items', []):
            snippet = item['snippet']
            v_id = snippet['resourceId']['videoId']
            
            clean_title = snippet.get('title', 'Tanpa Judul').replace('\n', ' ').strip()
            clean_desc = (snippet.get('description', '') or '-').replace('\n', ' ').strip()
            channel_title = snippet.get('channelTitle', fallback_channel_title).replace('\n', ' ').strip()
            
            videos.append({
                'url': f"https://www.youtube.com/watch?v={v_id}",
                'title': clean_title,
                'description': clean_desc,
                'channel_title': channel_title
            })

        return videos

    except urllib.error.HTTPError as e:
        print(f"[!] Error HTTP ({e.code}) pada Video ID {video_id}: {e.reason}")
        return []
    except Exception as e:
        print(f"[!] Error pada Video ID {video_id}: {e}")
        return []

def process_populer_file(input_filename="populer.txt", output_filename="detailPopuler.txt"):
    if not os.path.exists(input_filename):
        print(f"File {input_filename} nggak ditemukan.")
        return

    with open(input_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(output_filename, "w", encoding="utf-8") as out:
        for line in lines:
            line = line.strip()
            if not line or " - " not in line:
                continue

            last_dash = line.rfind(" - ")
            video_url = line[:last_dash].strip()
            niche = line[last_dash + 3:].strip()

            out.write(f"- {niche}\n")

            video_id = extract_video_id(video_url)
            if not video_id:
                continue

            print(f"Memproses {niche} (ID: {video_id})...")
            videos = get_videos_from_video_id(video_id, API_KEY)

            for v in videos:
                desc = v['description'][:150] + "..." if len(v['description']) > 150 else v['description']
                out.write(f"{v['url']} - {v['title']} - {desc} - {v['channel_title']}\n")

    print(f"\nSelesai! Hasil disimpan ke {output_filename}")

if __name__ == "__main__":
    process_populer_file()