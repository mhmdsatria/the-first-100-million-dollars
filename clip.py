import json
import os
import random
import subprocess
import uuid

# Configuration durasi acak per niche (minimal & maksimal dalam detik)
NICHE_DURATIONS = {
    "Bola": (15, 30),
    "News Internasional": (30, 60),
    "Kartun": (15, 30),
    "Anime": (20, 40),
    "Dracin": (45, 90),
    "Random": (15, 25)
}

DEFAULT_DURATION = (15, 30)

def get_video_info(file_path: str):
    """Mengambil durasi, lebar, dan tinggi video menggunakan ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration",
        "-of", "json",
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        stream = data['streams'][0]
        width = int(stream['width'])
        height = int(stream['height'])
        duration = float(stream['duration'])
        return duration, width, height
    except Exception as e:
        print(f"[!] Gagal mengambil info video '{file_path}': {e}")
        return None, None, None

def parse_master_meta(meta_path: str):
    """Membaca data dari file meta.txt induk di folder download."""
    metadata = {"judul": "-", "deskripsi": "-", "chanel": "-"}
    if not os.path.exists(meta_path):
        return metadata

    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("judul:"):
                metadata["judul"] = line.replace("judul:", "").strip()
            elif line.startswith("deskripsi:"):
                metadata["deskripsi"] = line.replace("deskripsi:", "").strip()
            elif line.startswith("chanel:"):
                metadata["chanel"] = line.replace("chanel:", "").strip()
    return metadata

def generate_clip_metadata(master_title: str, master_desc: str, channel_name: str, niche: str, part_num: int) -> str:
    """
    Fungsi modular untuk generate teks metadata klip baru.
    Nanti jika ingin pakai NVIDIA Llama 3.2 90B, cukup ganti isi di dalam fungsi ini.
    """
    clean_niche = niche.replace(" ", "")
    words = [w for w in master_title.split() if len(w) > 3][:3]
    dynamic_hashtags = " ".join([f"#{w.strip(',.?!')}" for w in words])
    
    # Variasi judul sederhana (Opsi B)
    variations = ["Keseruan", "Update", "Momen", "Sorotan", "Fakta"]
    prefix = random.choice(variations)
    
    clip_title = f"{prefix} {master_title} - Part {part_num}"
    clip_desc = f"Cuplikan menarik seputar {master_title}. Simak potongan selengkapnya pada bagian ke-{part_num} ini."
    hashtags = f"#A #B #{clean_niche} {dynamic_hashtags}".strip()

    meta_content = f"""judul: {clip_title}
deskripsi: {clip_desc}
hastag: {hashtags}

deskripsi - metaOg:
Terimakasih mohon maaf bila ada kesalahan, bisa tonton video selanjutnya di:
facebook: A
tiktok: A
youtube: A
videos by: {channel_name}"""

    return meta_content

def process_clipping():
    source_dir = "download"
    target_dir = "videos"

    if not os.path.exists(source_dir):
        print(f"Folder '{source_dir}' tidak ditemukan. Jalankan downloader terlebih dahulu.")
        return

    for niche in os.listdir(source_dir):
        niche_src_folder = os.path.join(source_dir, niche)
        if not os.path.isdir(niche_src_folder):
            continue

        niche_tgt_folder = os.path.join(target_dir, niche)
        os.makedirs(niche_tgt_folder, exist_ok=True)

        print(f"\n==========================================")
        print(f" Memproses Niche: {niche}")
        print(f"==========================================")

        min_dur, max_dur = NICHE_DURATIONS.get(niche, DEFAULT_DURATION)

        for file_name in os.listdir(niche_src_folder):
            if not file_name.endswith(('.mp4', '.mkv', '.avi')):
                continue

            video_path = os.path.join(niche_src_folder, file_name)
            base_name = os.path.splitext(file_name)[0]
            meta_path = os.path.join(niche_src_folder, f"{base_name}.txt")

            master_meta = parse_master_meta(meta_path)
            total_duration, width, height = get_video_info(video_path)

            if not total_duration:
                continue

            is_vertical = height > width
            print(f"\n-> Memotong file: {file_name} (Durasi: {total_duration:.1f}s | Vertical: {is_vertical})")

            # Kalkulasi segment durasi
            start_time = 0.0
            clip_index = 1

            while start_time < total_duration:
                target_clip_dur = float(random.randint(min_dur, max_dur))
                remaining = total_duration - start_time

                # Jika sisa durasi kurang dari batas minimal niche, gabungkan ke klip terakhir
                if remaining < min_dur:
                    if clip_index > 1:
                        # Biarkan loop selesai, durasi klip sebelumnya sudah mencakup sisanya
                        break
                    else:
                        current_clip_dur = remaining
                elif remaining <= (target_clip_dur + min_dur):
                    current_clip_dur = remaining
                else:
                    current_clip_dur = target_clip_dur

                clip_uuid = uuid.uuid4().hex[:10]
                out_video = os.path.join(niche_tgt_folder, f"{clip_uuid}.mp4")
                out_meta = os.path.join(niche_tgt_folder, f"{clip_uuid}.txt")

                # Filter FFmpeg: jika horizontal (16:9), pasang blur background 9:16 (1080x1920)
                if is_vertical:
                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-ss", str(start_time), "-t", str(current_clip_dur),
                        "-i", video_path, "-c:v", "libx264", "-c:a", "aac", out_video
                    ]
                else:
                    filter_complex = (
                        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                        "crop=1080:1920,boxblur=20:5[bg];"
                        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
                        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
                    )
                    ffmpeg_cmd = [
                        "ffmpeg", "-y", "-ss", str(start_time), "-t", str(current_clip_dur),
                        "-i", video_path, "-vf", filter_complex,
                        "-c:v", "libx264", "-crf", "23", "-c:a", "aac", out_video
                    ]

                print(f"   [Klip #{clip_index}] {start_time:.1f}s - {start_time + current_clip_dur:.1f}s | UUID: {clip_uuid}")
                
                try:
                    subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)

                    # Buat file metadata klip baru
                    clip_meta_text = generate_clip_metadata(
                        master_meta["judul"],
                        master_meta["deskripsi"],
                        master_meta["chanel"],
                        niche,
                        clip_index
                    )
                    with open(out_meta, "w", encoding="utf-8") as f:
                        f.write(clip_meta_text)

                except subprocess.CalledProcessError as e:
                    print(f"   [!] Gagal memotong klip pada detik {start_time}: {e.stderr}")
                    break

                start_time += current_clip_dur
                clip_index += 1

    print("\nSelesai! Seluruh klip video dan file metadata baru tersimpan di folder 'videos/'.")

if __name__ == "__main__":
    process_clipping()