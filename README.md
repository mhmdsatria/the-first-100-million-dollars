# Multiplatform Video Automation Pipeline

A Python-based automation pipeline for discovering, downloading, clipping, and uploading short-form video content across multiple platforms.

## Workflow

1. **Trending Discovery** - `getTrending.py` scrapes YouTube for trending videos by niche
2. **Channel Videos** - `getChanelVideos.py` extracts channel video data
3. **Download** - `downloads.py` downloads videos to niche-specific folders
4. **Clipping** - `clip.py` extracts vertical segments (1080x1920) with blur background using FFmpeg
5. **Upload Queue** - `generatorListUpload.py` creates `list_upload.json` for batch processing
6. **Upload Orchestration** - `autoUploader.py` publishes to YouTube Shorts, TikTok, and Facebook Reels

## Platforms

- **YouTube**: Official YouTube Data API v3
- **TikTok**: Playwright automation via TikTok Studio
- **Facebook**: Playwright automation via Facebook Reels Creator

## Niche Support

Each niche has independent credentials and processing parameters:
- Bola, News Internasional, Kartun, Anime, Dracin, Random

## Requirements

- Python 3.9+
- FFmpeg (for video processing)
- Playwright browsers (`playwright install chromium`)
- Google YouTube API key and OAuth credentials per niche
- TikTok and Facebook session cookies per niche

## Pipeline Commands

```bash
python getTrending.py           # Generate populer.txt
python getChanelVideos.py       # Generate detailPopuler.txt
python downloads.py             # Download videos to download/{niche}/
python clip.py                  # Generate vertical clips in videos/{niche}/
python generatorListUpload.py   # Create list_upload.json
python autoUploader.py          # Upload all queued videos
```

## Credentials

Store per-niche credentials in `credentials/{niche}/`:
- `yt_oauth.json` - YouTube OAuth client secrets
- `yt_token.json` - YouTube API tokens
- `tiktok_cookies.json` - TikTok session cookies
- `fb_cookies.json` - Facebook session cookies

## Notes

- Uploads include 8-minute delays between videos to respect rate limits
- Queue status persists in `list_upload.json` for resume after interruption
- Each niche requires separate API credentials and cookie authentication