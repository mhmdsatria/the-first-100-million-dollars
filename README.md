# 🎬 Multiplatform Auto-Uploader

> **"The First 100 Million Dollars"** — an automated pipeline that turns trending YouTube content into vertical short-form videos and distributes them across YouTube Shorts, TikTok, and Facebook Reels.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![YouTube API](https://img.shields.io/badge/YouTube%20API-v3-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://developers.google.com/youtube/v3)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Video%20Processing-007808?style=flat-square)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## ✨ What It Does

This project automates the entire lifecycle of short-form content creation and distribution:

```
🔍 Discover trending videos
        │
        ▼
📥 Download source videos (yt-dlp)
        │
        ▼
✂️  Clip into vertical shorts (FFmpeg · 1080×1920 · blur background)
        │
        ▼
📋 Generate upload queue (JSON)
        │
        ▼
🚀 Upload to YouTube Shorts · TikTok · Facebook Reels
```

Each niche (Bola, News, Kartun, Anime, Dracin, Random) is processed independently with its own duration rules, credentials, and queue.

---

## 🗂️ Project Structure

```
multiplatform/
├── getTrending.py          # ① Search YouTube for trending videos per niche → populer.txt
├── getChanelVideos.py      # ② Expand each result to 10 latest channel uploads → detailPopuler.txt
├── downloads.py            # ③ Download videos + metadata via yt-dlp → download/{niche}/
├── clip.py                 # ④ Split into vertical clips with FFmpeg → videos/{niche}/
├── generatorListUpload.py  # ⑤ Build persistent upload queue → list_upload.json
├── autoUploader.py         # ⑥ Upload to YouTube / TikTok / Facebook
├── credentials/            # Per-niche auth (gitignored)
│   └── {niche}/
│       ├── yt_oauth.json       # Google OAuth client secrets
│       ├── yt_token.json       # YouTube token (auto-generated)
│       ├── tiktok_cookies.json # TikTok session cookies
│       └── fb_cookies.json     # Facebook session cookies
├── AGENTS.md               # Agent / contributor quick-start
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.9+** | |
| **FFmpeg** | Must be in `PATH` (`ffmpeg -version`) |
| **YouTube Data API key** | Set `API_KEY` inside `getTrending.py` & `getChanelVideos.py` |
| **Google OAuth credentials** | One `yt_oauth.json` per niche in `credentials/{niche}/` |
| **TikTok / Facebook cookies** | Exported as JSON to `credentials/{niche}/` |

### 2. Install

```bash
git clone https://github.com/mhmdsatria/the-first-100-million-dollars.git
cd the-first-100-million-dollars

pip install google-auth google-auth-oauthlib google-api-python-client yt-dlp playwright requests
playwright install chromium
```

> **FFmpeg** — Windows: `winget install FFmpeg` or `choco install ffmpeg` · macOS: `brew install ffmpeg` · Linux: `apt install ffmpeg`

### 3. Configure Credentials

Create a folder per niche inside `credentials/` and drop the required files:

```
credentials/
├── Bola/
│   ├── yt_oauth.json
│   ├── tiktok_cookies.json
│   └── fb_cookies.json
├── Anime/
│   └── ...
└── Dracin/
    └── ...
```

On first YouTube upload, a browser window will open for OAuth — the resulting `yt_token.json` is saved automatically.

---

## 🔄 Usage

Run the pipeline **in order**. Each step writes the input for the next.

```bash
# 1 — Find trending videos (→ populer.txt, deduplicated via temp.txt)
python getTrending.py

# 2 — Expand to latest channel uploads (→ detailPopuler.txt)
python getChanelVideos.py

# 3 — Download videos + metadata (→ download/{niche}/{uuid}.mp4 + .txt)
python downloads.py

# 4 — Clip into vertical shorts (→ videos/{niche}/{uuid}.mp4 + .txt)
python clip.py

# 5 — Build upload queue (→ list_upload.json, idempotent — never resets completed)
python generatorListUpload.py

# 6 — Upload everywhere (resumable, 8-minute delay between items by default)
python autoUploader.py
```

> 💡 Re-running `generatorListUpload.py` only appends **new** clips — existing queue status is preserved. Re-running `autoUploader.py` skips anything already marked `completed`.

---

## ⚙️ Configuration

### Clip Durations (`clip.py` — `NICHE_DURATIONS`)

| Niche | Min – Max |
|-------|-----------|
| Bola | 15 – 30 s |
| News Internasional | 30 – 60 s |
| Kartun | 15 – 30 s |
| Anime | 20 – 40 s |
| Dracin | 45 – 90 s |
| Random | 15 – 25 s |

### Search Queries (`getTrending.py` — `NICHES`)

Each niche defines `query`, `backup` query, `region`, `lang`, and `exclude` keywords. The search falls back through 4 layers (primary + long-duration → primary → backup + long-duration → backup) to guarantee a result.

### Upload Delay (`autoUploader.py`)

```python
run_auto_uploader(delay_minutes=8)  # default
```

---

## 🔐 Security Notes

- **Never commit** `credentials/`, `keyFree.txt`, or API keys. They are gitignored.
- Rotate your YouTube API key if it was ever committed.
- `tesModel.py` (NVIDIA API experiment with a hard-coded bearer token) is intentionally excluded from the repository.

---

## 🛠️ Troubleshooting

| Symptom | Fix |
|---------|-----|
| `FileNotFoundError: yt_oauth.json` | Add OAuth client file to `credentials/{niche}/` |
| `Cookie … not found` | Re-export TikTok/Facebook cookies as JSON |
| `ffprobe` / `ffmpeg` not found | Install FFmpeg and ensure it is in `PATH` |
| YouTube quota exceeded | Wait for quota reset or use a different API key |
| Upload stuck / interrupted | Just re-run `python autoUploader.py` — it resumes from `list_upload.json` |

---

## 📄 License

MIT — do whatever you want, just don't blame us when TikTok changes its DOM at 3 AM.

---

<p align="center">Built with ☕ and too many FFmpeg flags.</p>
