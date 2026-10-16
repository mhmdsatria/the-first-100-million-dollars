# OpenCode Instructions for multiplatform

## Repository Overview
- **Type**: Personal automation/multiplatform YouTube content pipeline
- **Primary Language**: Python
- **Workflow**: trending discovery → download → clip processing → upload orchestration

## Key Files and Entry Points

### Core Pipeline (run full workflow)
```bash
python autoUploader.py
```
- Main orchestrator that uploads all videos in list_upload.json to YouTube/TikTok/Facebook
- Handles existing upload status to avoid re-uploading completed items

### Content Generation Pipeline
1. Trending discovery: `python getTrending.py` → creates `populer.txt`
2. Channel videos: `python getChanelVideos.py` → creates `detailPopuler.txt`  
3. Video downloads: `python downloads.py` → downloads to `download/{niche}/` folder
4. Clip processing: `python clip.py` → creates clipped videos in `videos/{niche}/` folder
5. Upload queue: `python generatorListUpload.py` → creates `list_upload.json`

### Processing Tools
- **clip.py**: Uses FFmpeg to extract vertical segments (1080x1920) from horizontal clips with blur background effect
- **autoUploader.py**: Uses YouTube API (official) + Playwright (TikTok/Facebook automation)
- Requires niche-specific credentials in `credentials/{niche}/` directory

## Architecture Notes

### Package Boundaries
- Each script is a self-contained module with clear responsibilities
- Data flows sequentially: trending data → download folder → videos folder → upload queue → platform uploads
- Niche directories mirror API/automation requirements (different per platform)

### Platform-Specific Entry Points
- **YouTube**: Official YouTube Data API v3 (scope: youtube.upload)
- **TikTok**: Playwright automation via TikTok Studio web interface
- **Facebook**: Playwright automation via Facebook Reels creation

### Credential Management
- Each platform (YouTube/TikTok/Facebook) requires separate API access
- Credentials stored per niche in `credentials/{niche}/` folder:
  - `yt_oauth.json`: YouTube OAuth client secrets
  - `yt_token.json`: YouTube API tokens
  - `tiktok_cookies.json`: TikTok session cookies
  - `fb_cookies.json`: Facebook session cookies

## Setup Requirements

### Python Dependencies (inferred from imports)
```bash
pip install google-auth google-auth-oauthlib google-api-python-client yt-dlp playwright
```
- Playwright browsers: `playwright install chromium`
- FFmpeg: Required for video clipping operations
- YouTube API Key: Included in getTrending.py and getChanelVideos.py

### Credentials Directory Structure
```
credentials/
├── {niche}/               # Each niche needs separate credentials
│   ├── yt_oauth.json      # Google OAuth client secrets
│   ├── yt_token.json      # YouTube API tokens  
│   ├── tiktok_cookies.json # TikTok session cookies
│   └── fb_cookies.json     # Facebook session cookies
```

## Operational Gotchas

### File Paths and Working Directory
- All scripts assume execution from repository root
- Relative paths used throughout (e.g., `download/`, `videos/`, `credentials/`)
- Output files written relative to current working directory

### API Rate Limits and Authentication
- YouTube API requires per-niche credentials (shared across scripts)
- TikTok/Facebook require cookie authentication via Playwright
- OAuth flow: first run creates token files in credential directories

### Video Processing
- Horizontal videos are converted to vertical (1080x1920) with blur background
- Clipping uses random duration per niche configuration
- Each niche has specific duration ranges (see NICHE_DURATIONS in clip.py)

### Upload Delays
- autoUploader.py implements 8-minute delays between videos by default
- Queue status persists in list_upload.json to resume interrupted workflows

## Testing and Verification

### Single Component Testing
```bash
# Test just the YouTube upload logic
python -c "from autoUploader import upload_youtube_shorts; print('Import OK')"

# Test trending discovery
python -c "from getTrending import main; main()"  # Run full trending discovery
```

### Integration Testing Required
- Full pipeline requires:
  1. Valid YouTube API credentials per niche
  2. Active TikTok/Facebook accounts with cookies
  3. Downloaded video files in appropriate folders
  4. Complete metadata files for each video

### Common Debugging Scenarios
1. **Missing credentials**: Check `credentials/{niche}/` folder exists with required files
2. **FFmpeg errors**: Ensure ffmpeg is installed and in PATH
3. **Network timeouts**: Check internet connectivity, API rate limits, and proxy settings
4. **Permission issues**: Verify write access to output directories

## Important Constraints

### Niche Management
- Each niche (Bola, News Internasional, Kartun, Anime, Dracin, Random) has:
  - Different YouTube API credentials
  - Different clip duration ranges
  - Platform-specific processing requirements

### Data Flow Dependencies
- scripts depend on output files from previous scripts
- `detailPopuler.txt` format must match parsing in `downloads.py`
- `populer.txt` format must match parsing in `getChanelVideos.py`

### Credential Sharing
- Same API key used across multiple scripts (API_KEY in getTrending.py and getChanelVideos.py)
- OAuth tokens specific per platform and per niche

## Workflow Troubleshooting

### Common Failure Points
1. **Missing dependencies**: Install all Python packages and playwright browsers
2. **Invalid credentials**: Re-authenticate via OAuth flow or update cookie files
3. **Network issues**: Check API quotas, rate limits, and connectivity
4. **File system issues**: Ensure write permissions for output directories
5. **Path issues**: Run scripts from repository root directory

### Recovery Steps
- Interrupted upload queues: Resume with `python autoUploader.py` (status persists)
- Failed video processing: Remove problematic files from processing folders
- Invalid tokens: Delete token files to force OAuth re-authentication
- Missing dependencies: Install packages and re-run setup scripts