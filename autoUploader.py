import os
import json
import time
import traceback
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Scope yang dibutuhkan untuk YouTube Data API
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def save_queue_status(data, json_path="list_upload.json"):
    """Menyimpan status antrean secara instan agar tidak hilang saat terjadi gangguan."""
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Gagal memperbarui {json_path}: {e}")

# ==========================================
# 1. YOUTUBE SHORTS UPLOADER (OFFICIAL API)
# ==========================================
def upload_youtube_shorts(niche: str, video_path: str, title: str, description: str):
    cred_folder = os.path.join("credentials", niche)
    client_secret_file = os.path.join(cred_folder, "yt_oauth.json")
    token_file = os.path.join(cred_folder, "yt_token.json")

    if not os.path.exists(client_secret_file) and not os.path.exists(token_file):
        raise FileNotFoundError(f"Kredensial YouTube untuk niche '{niche}' tidak ditemukan di {cred_folder}")

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, YOUTUBE_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],  # YouTube membatasi judul maks 100 karakter
            "description": description,
            "tags": [niche, "shorts", "viral"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   [YouTube] Progress: {int(status.progress() * 100)}%")

    print(f"   [✓] YouTube Upload Berhasil! Video ID: {response.get('id')}")
    return True


# ==========================================
# 2. TIKTOK UPLOADER (PLAYWRIGHT AUTOMATION)
# ==========================================
def upload_tiktok(niche: str, video_path: str, description: str):
    cookie_file = os.path.join("credentials", niche, "tiktok_cookies.json")
    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie TikTok untuk niche '{niche}' tidak ditemukan di {cookie_file}")

    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="networkidle")
        time.sleep(3)

        # Upload file video
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(os.path.abspath(video_path))

        # Tunggu proses upload selesai
        page.wait_for_selector('div[contenteditable="true"]', timeout=60000)
        time.sleep(5)

        # Isi Deskripsi/Caption
        caption_box = page.locator('div[contenteditable="true"]')
        caption_box.fill("")
        caption_box.type(description[:2000])

        # Klik tombol Post
        post_button = page.locator('button:has-text("Post"), button:has-text("Posting")')
        post_button.click()

        time.sleep(10)
        browser.close()
        print("   [✓] TikTok Upload Berhasil!")
        return True


# ==========================================
# 3. FACEBOOK REELS UPLOADER (PLAYWRIGHT)
# ==========================================
def upload_facebook_reels(niche: str, video_path: str, description: str):
    cookie_file = os.path.join("credentials", niche, "fb_cookies.json")
    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie Facebook untuk niche '{niche}' tidak ditemukan di {cookie_file}")

    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        page.goto("https://www.facebook.com/reels/create", wait_until="networkidle")
        time.sleep(4)

        # Upload file video
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(os.path.abspath(video_path))
        time.sleep(5)

        # Isi deskripsi Reel
        desc_box = page.locator('div[aria-label="Describe your reel..."], textarea')
        if desc_box.count() > 0:
            desc_box.first.fill(description)

        # Klik Selanjutnya/Publish
        next_btn = page.locator('button:has-text("Next"), button:has-text("Selanjutnya"), button:has-text("Publish")')
        while next_btn.is_visible():
            next_btn.click()
            time.sleep(3)

        time.sleep(10)
        browser.close()
        print("   [✓] Facebook Reels Upload Berhasil!")
        return True


# ==========================================
# MAIN EXECUTION LOOP WITH DELAY
# ==========================================
def run_auto_uploader(json_path="list_upload.json", delay_minutes=8):
    if not os.path.exists(json_path):
        print(f"[!] File {json_path} tidak ditemukan.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        queue = json.load(f)

    delay_seconds = delay_minutes * 60

    for index, item in enumerate(queue):
        status = item["status"]

        # Lewati jika semua platform sudah ter-upload
        if all(s == "completed" for s in status.values()):
            continue

        video_id = item["id"]
        niche = item["niche"]
        video_path = item["video_path"]
        judul = item["judul"]
        deskripsi = item["deskripsi_lengkap"]

        print(f"\n==========================================")
        print(f" Memproses Item #{video_id} | Niche: {niche}")
        print(f" Judul: {judul[:50]}...")
        print(f"==========================================")

        if not os.path.exists(video_path):
            print(f"[!] File video tidak ditemukan di path: {video_path}")
            continue

        # 1. Upload YouTube
        if status["youtube"] == "pending":
            print(" -> Mengunggah ke YouTube Shorts...")
            try:
                upload_youtube_shorts(niche, video_path, judul, deskripsi)
                item["status"]["youtube"] = "completed"
            except Exception as e:
                print(f"   [!] YouTube Gagal: {e}")
                item["status"]["youtube"] = f"failed: {str(e)[:100]}"
            save_queue_status(queue, json_path)

        # 2. Upload TikTok
        if status["tiktok"] == "pending":
            print(" -> Mengunggah ke TikTok...")
            try:
                upload_tiktok(niche, video_path, deskripsi)
                item["status"]["tiktok"] = "completed"
            except Exception as e:
                print(f"   [!] TikTok Gagal: {e}")
                item["status"]["tiktok"] = f"failed: {str(e)[:100]}"
            save_queue_status(queue, json_path)

        # 3. Upload Facebook
        if status["facebook"] == "pending":
            print(" -> Mengunggah ke Facebook Reels...")
            try:
                upload_facebook_reels(niche, video_path, deskripsi)
                item["status"]["facebook"] = "completed"
            except Exception as e:
                print(f"   [!] Facebook Gagal: {e}")
                item["status"]["facebook"] = f"failed: {str(e)[:100]}"
            save_queue_status(queue, json_path)

        # Cek apakah masih ada item pending setelah item ini
        remaining_items = any(
            any(s == "pending" for s in next_item["status"].values())
            for next_item in queue[index + 1:]
        )

        if remaining_items:
            print(f"\n[i] Menunggu {delay_minutes} menit ({delay_seconds} detik) sebelum memproses video berikutnya...")
            time.sleep(delay_seconds)

    print("\n[✓] Seluruh antrean upload selesai diproses!")


if __name__ == "__main__":
    run_auto_uploader()