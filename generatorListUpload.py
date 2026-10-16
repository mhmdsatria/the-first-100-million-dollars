import os
import json

def parse_meta_file(meta_path: str):
    """
    Membaca isi file meta.txt klip.
    Mengambil 'judul' secara spesifik dan menyimpan seluruh teks sebagai 'deskripsi_lengkap'.
    """
    judul = "-"
    deskripsi_lengkap = ""

    if not os.path.exists(meta_path):
        return judul, deskripsi_lengkap

    with open(meta_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        deskripsi_lengkap = content  # Isi lengkap teks metadata

        # Mengambil judul dari baris 'judul:'
        for line in content.splitlines():
            if line.startswith("judul:"):
                judul = line.replace("judul:", "", 1).strip()
                break

    return judul, deskripsi_lengkap


def generate_upload_list(videos_dir="videos", output_json="list_upload.json"):
    """
    Memindai folder videos/ dan menyusun list_upload.json
    """
    if not os.path.exists(videos_dir):
        print(f"[!] Folder '{videos_dir}' tidak ditemukan. Pastikan clipper.py sudah dijalankan.")
        return

    # 1. Muat data lama jika list_upload.json sudah ada (agar status completed tidak terreset)
    existing_list = []
    existing_paths = set()

    if os.path.exists(output_json):
        try:
            with open(output_json, "r", encoding="utf-8") as f:
                existing_list = json.load(f)
                existing_paths = {item["video_path"] for item in existing_list}
            print(f"[i] Berhasil memuat {len(existing_list)} data dari '{output_json}' yang sudah ada.")
        except Exception as e:
            print(f"[!] Gagal membaca '{output_json}' lama: {e}. Membuat antrean baru dari awal.")
            existing_list = []
            existing_paths = set()

    upload_list = list(existing_list)
    next_id = max([item["id"] for item in upload_list], default=0) + 1
    new_items_count = 0

    # 2. Scan folder niche di dalam videos/
    for niche in os.listdir(videos_dir):
        niche_folder = os.path.join(videos_dir, niche)
        if not os.path.isdir(niche_folder):
            continue

        # Ambil semua file .mp4
        for file_name in os.listdir(niche_folder):
            if not file_name.endswith(('.mp4', '.mkv', '.avi')):
                continue

            video_path = os.path.normpath(os.path.join(niche_folder, file_name))

            # Jika video sudah ada di list_upload.json, lewati
            if video_path in existing_paths:
                continue

            base_name = os.path.splitext(file_name)[0]
            meta_path = os.path.normpath(os.path.join(niche_folder, f"{base_name}.txt"))

            judul, deskripsi_lengkap = parse_meta_file(meta_path)

            item_data = {
                "id": next_id,
                "niche": niche,
                "video_path": video_path.replace("\\", "/"),
                "meta_path": meta_path.replace("\\", "/"),
                "judul": judul,
                "deskripsi_lengkap": deskripsi_lengkap,
                "status": {
                    "youtube": "pending",
                    "tiktok": "pending",
                    "facebook": "pending"
                }
            }

            upload_list.append(item_data)
            existing_paths.add(video_path)
            next_id += 1
            new_items_count += 1

    # 3. Simpan hasil ke list_upload.json
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(upload_list, f, indent=4, ensure_ascii=False)

    print("\n==========================================")
    print(f" Selesai! Antrean Upload Diperbarui")
    print("==========================================")
    print(f"- Total Video Baru Ditambahkan : {new_items_count}")
    print(f"- Total Antrean Keseluruhan   : {len(upload_list)}")
    print(f"- File disimpan di           : {output_json}\n")


if __name__ == "__main__":
    generate_upload_list()