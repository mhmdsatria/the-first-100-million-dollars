import os
import uuid
import yt_dlp

def parse_detail_file(filename="detailPopuler.txt"):
    if not os.path.exists(filename):
        print(f"File {filename} nggak ditemukan!")
        return {}

    data_by_niche = {}
    current_niche = None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("- "):
                current_niche = line[2:].strip()
                if current_niche not in data_by_niche:
                    data_by_niche[current_niche] = []
                continue

            if current_niche and " - " in line:
                try:
                    url, rest = line.split(" - ", 1)
                    title_desc, channel = rest.rsplit(" - ", 1)
                    
                    if " - " in title_desc:
                        title, desc = title_desc.split(" - ", 1)
                    else:
                        title, desc = title_desc, "-"

                    data_by_niche[current_niche].append({
                        "url": url.strip(),
                        "title": title.strip(),
                        "description": desc.strip(),
                        "channel": channel.strip()
                    })
                except Exception as e:
                    print(f"Gagal parsing baris: {line} | Error: {e}")

    return data_by_niche

def start_download():
    base_dir = "download"
    data = parse_detail_file("detailPopuler.txt")

    if not data:
        print("Nggak ada data video yang bisa didownload.")
        return

    for niche, videos in data.items():
        niche_folder = os.path.join(base_dir, niche)
        os.makedirs(niche_folder, exist_ok=True)

        print(f"\n--- Memproses Niche: {niche} ({len(videos)} video) ---")

        for idx, item in enumerate(videos, 1):
            url = item["url"]
            title = item["title"]
            desc = item["description"]
            channel = item["channel"]

            random_id = uuid.uuid4().hex[:10]
            output_template = os.path.join(niche_folder, f"{random_id}.%(ext)s")

            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'format': 'bv*+ba/b',  # Mengambil trek video dan audio terbaik
            }

            print(f"[{idx}/{len(videos)}] Downloading -> {random_id} ({title[:30]}...)")

            try:
                # 1. Download Video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # 2. Buat file metadata
                meta_filename = os.path.join(niche_folder, f"{random_id}.txt")
                with open(meta_filename, "w", encoding="utf-8") as meta_file:
                    meta_file.write(f"judul: {title}\n")
                    meta_file.write(f"deskripsi: {desc}\n")
                    meta_file.write(f"chanel: {channel}\n")

            except Exception as e:
                print(f"  [!] Gagal mendownload {url}: {e}")

    print(f"\nSelesai! Semua video dan meta.txt sudah tersimpan rapi di folder '{base_dir}'.")

if __name__ == "__main__":
    start_download()