# Social Media Downloader Bot - README

**Developer:** Younes Sedki  
**GitHub:** https://github.com/younes-sedki/  
**Portfolio:** https://sedkiy.dev

---

## What This Bot Does

Downloads videos and audio from 7 social media platforms directly to Telegram.

---

## Supported Platforms

1. YouTube (youtube.com, youtu.be)
2. Instagram (instagram.com)
3. TikTok (tiktok.com, vm.tiktok.com, vt.tiktok.com)
4. Twitter/X (twitter.com, x.com)
5. Facebook (facebook.com, fb.watch)
6. Reddit (reddit.com)
7. Pinterest (pinterest.com, pin.it) - Custom downloader

---

## Quick Setup

### 1. Install Requirements
```bash
pip install pyTelegramBotAPI yt-dlp requests PySocks
```

### 2. Configure
Edit `bot_stable.py` line 12:
```python
BOT_TOKEN = "your_telegram_bot_token_here"
```

### 3. Run
```bash
python bot_stable.py
```

---

## How to Use

### Download Video
Send any link:
```
https://youtube.com/watch?v=xxx
```

### Download Audio
Add "audio" or "mp3" to your message:
```
https://youtube.com/watch?v=xxx audio
```

### Commands
- `/start` - Welcome message
- `/help` - Usage instructions

---

## Features

✅ **Progress Updates** - Shows download percentage and file size
✅ **Auto-Cleanup** - Files deleted after 2 minutes
✅ **SOCKS5 Proxies** - Random rotation for each download
✅ **Auto-Reconnect** - Never crashes on connection errors
✅ **Retry Logic** - 3 automatic retry attempts
✅ **Large File Warning** - Alerts for files >20MB
✅ **Custom Pinterest** - Works when yt-dlp is blocked

---

## Proxy Setup (Optional)

### Enable Proxies
Line 16:
```python
USE_PROXY = True
```

### Add Proxies

**Method 1: In Code** (lines 17-26)
```python
PROXY_LIST = [
    "142.111.48.253:7030:username:password",
    "23.95.150.145:6114:username:password",
]
```

**Method 2: In File** (proxies.txt)
```
142.111.48.253:7030:username:password
23.95.150.145:6114:username:password
```

Both formats work:
- `ip:port:username:password`
- `socks5://username:password@ip:port`

---

## Configuration

### Settings (at top of file)

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Line 12
USE_PROXY = False                       # Line 16
CLEANUP_DELAY = 120                     # Line 87 (2 minutes)
DOWNLOAD_DIR = "downloads"              # Line 83
```

---

## User Experience

### Download Process
```
User sends: https://youtube.com/watch?v=xxx

Bot shows:
📹 Downloading from youtube...
⬇️ Downloading: 45% (5.2MB / 11.5MB)
⬇️ Downloading: 78% (9.0MB / 11.5MB)
📤 Uploading (11.5MB)...
[Video sent]
```

### Audio Download
```
User sends: https://youtube.com/watch?v=xxx audio

Bot shows:
🎵 Downloading from youtube...
📤 Uploading (3.2MB)...
[MP3 sent]
```

---

## Startup Banner

```
============================================================
🤖 Social Media Downloader Bot
============================================================
👨‍💻 Developer: Younes Sedki
🔗 GitHub: https://github.com/younes-sedki/
🌐 Portfolio: https://sedkiy.dev
============================================================

📁 Download folder: downloads
🗑️  Auto-cleanup: 2 minutes
✅ Platforms: youtube, instagram, tiktok, twitter, facebook, reddit, pinterest
🔒 Proxy: ENABLED (10 proxies loaded)

🔄 Updating yt-dlp...
✅ yt-dlp updated!

============================================================
🚀 Bot is ready! Send links to download.
============================================================

🔄 Starting bot polling...
```

---

## Requirements

### Python Packages
- `pyTelegramBotAPI` - Telegram bot framework
- `yt-dlp` - Video downloader
- `requests` - HTTP library
- `PySocks` - SOCKS proxy support (optional)

### System
- Python 3.8+
- `ffmpeg` (for audio conversion)

### Install ffmpeg
```bash
# Windows
choco install ffmpeg

# Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

---

## Error Messages

### Audio Without ffmpeg
```
❌ Audio conversion not available

ffmpeg is not installed.

Install it:
• Windows: choco install ffmpeg
• Linux: sudo apt install ffmpeg
• Mac: brew install ffmpeg

Or send the link without 'audio' to get the video.
```

### File Too Large
```
❌ File too large (65.2MB)
Telegram limit is 50MB.
Try: [link] audio
```

### Connection Error
```
⚠️  Connection error: Remote end closed connection
🔄 Reconnecting in 5 seconds...
```

---

## How It Works

### 1. Platform Detection
Bot detects which platform from URL

### 2. Downloader Selection
- Pinterest → Custom downloader
- Others → yt-dlp

### 3. Proxy Selection (if enabled)
Random proxy from your list

### 4. Download
Shows progress updates every 2 seconds

### 5. Upload to Telegram
3 retry attempts with 5-minute timeout

### 6. Cleanup
File deleted after 2 minutes

---

## Pinterest Special Features

Pinterest blocks yt-dlp, so this bot has a custom downloader that:

1. Follows redirects (pin.it → pinterest.com)
2. Extracts video URL from HTML
3. Downloads with SOCKS5 proxy (   YOU CAN TAKE 10 PROXIES FROM [webshare.io](https://webshare.io/) FOR TEST   )
4. Shows progress updates

Works with both:
- `https://pinterest.com/pin/123456789/`
- `https://pin.it/abc123`

---

## Technical Details

### Code Structure
- **Lines 1-101:** Configuration and utilities
- **Lines 103-230:** Custom Pinterest downloader
- **Lines 232-342:** yt-dlp integration
- **Lines 344-540:** Bot handlers
- **Lines 542-587:** Startup and main loop

### Proxy System
- Auto-converts formats
- Random rotation
- Works with Pinterest and yt-dlp
- Loads from file or code

### Auto-Cleanup
- Background threads
- 2-minute delay
- Prevents disk waste
- Safe deletion

### Auto-Reconnect
- Infinite loop
- 5-second retry
- Never exits on error

---

## Troubleshooting

### Bot Not Responding
Check bot token is correct

### Downloads Fail
Update yt-dlp:
```bash
pip install -U yt-dlp
```

### Pinterest Not Working
Enable proxies (required for Pinterest)

### Audio Fails
Install ffmpeg

### Proxy Errors
Test proxies first, use residential proxies for best results

---

## Performance

### Download Speed
- YouTube: 5-15 seconds
- TikTok: 3-8 seconds
- Instagram: 5-10 seconds
- Pinterest: 8-15 seconds (with proxy)

### Upload Speed
- Small (<10MB): 5-10 seconds
- Medium (10-30MB): 15-45 seconds
- Large (30-50MB): 45-90 seconds

### Storage
- Without cleanup: 10-100GB/month
- With 2-min cleanup: 100-500MB

---

## Credits

**Developer:** Younes Sedki  
**GitHub:** https://github.com/younes-sedki/  
**Portfolio:** https://sedkiy.dev

**Built with:**
- pyTelegramBotAPI
- yt-dlp
- requests
- Python

---

## License

Personal and educational use.  
Keep credits when using.

---

**Ready to download!** 🚀
