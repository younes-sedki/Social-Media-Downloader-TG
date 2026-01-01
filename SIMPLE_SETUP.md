# SIMPLE SETUP - NO ERRORS! 🎯

## 🚀 Quick Start (3 Steps)

### 1. Install
```bash
pip install pyTelegramBotAPI yt-dlp
```

### 2. Get Bot Token
- Open Telegram → @BotFather
- Send: `/newbot`
- Copy the token

### 3. Run
```python
# Edit bot_stable.py
BOT_TOKEN = "your_token_here"

# Run
python bot_stable.py
```

**Done!** ✅

---

## 📱 How to Use

Send any link:
```
https://youtube.com/watch?v=xxx
https://tiktok.com/@user/video/xxx
https://instagram.com/reel/xxx
```

Want audio only? Add "audio":
```
https://youtube.com/watch?v=xxx audio
```

**That's it!**

---

## ✅ What Works

- ✅ YouTube (videos, shorts)
- ✅ Instagram (posts, reels)
- ✅ TikTok (videos)
- ✅ Twitter/X
- ✅ Facebook
- ✅ Reddit
- ✅ Pinterest

---

## 🔧 If Something Breaks

### Error: "Unsupported URL"
**Fix:**
```bash
pip install -U yt-dlp
```

### Error: "File too large"
**Fix:**
```
Send: [link] audio
```

### Error: "ffmpeg not found"
**Fix:**
```bash
# Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows
Download from: https://ffmpeg.org/download.html
```

---

## 💡 Features

✅ Auto-cleanup (files deleted after 2 min)
✅ Audio extraction
✅ Progress updates
✅ User-friendly errors
✅ Auto yt-dlp updates on startup
✅ 50MB file size handling
✅ All major platforms

---

## 🎯 This Version is STABLE

**No complex features = No errors!**

Simple, reliable, works every time.

If you need advanced features (carousels, etc.), use the full `bot.py` version.

---

## 📊 Comparison

| Feature | bot_stable.py | bot.py (full) |
|---------|---------------|---------------|
| Simplicity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Stability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Platforms | 7 | 9 |
| Carousels | ❌ | ✅ |
| Speed opts | Basic | Advanced |
| Error handling | Simple | Complex |

**For most users:** Use `bot_stable.py`
**For power users:** Use `bot.py`

---

Enjoy! 🎉
