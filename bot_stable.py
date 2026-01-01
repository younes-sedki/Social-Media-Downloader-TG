import telebot
import yt_dlp
import os
import json
import threading
import time
import requests
import re
from urllib.parse import urlparse

# Bot Configuration
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

# Proxy Configuration
USE_PROXY = False  # Set to True to enable
PROXY_LIST = [
    # Add your SOCKS5 proxies here
    # Supports multiple formats:
    # Format 1: "socks5://username:password@ip:port"
    # Format 2: "ip:port:username:password"
    # Format 3: "ip:port" (no auth)
    # Example:
    # "socks5://123.45.67.89:1080",
    # "123.45.67.89:1080:username:password",
]

def convert_proxy_format(proxy):
    """Convert proxy to standard format"""
    # Already in standard format
    if proxy.startswith('socks5://') or proxy.startswith('http://'):
        return proxy
    
    # Parse ip:port:user:pass format
    parts = proxy.split(':')
    if len(parts) == 4:
        # Format: ip:port:username:password
        ip, port, username, password = parts
        return f"socks5://{username}:{password}@{ip}:{port}"
    elif len(parts) == 2:
        # Format: ip:port (no auth)
        ip, port = parts
        return f"socks5://{ip}:{port}"
    else:
        return proxy  # Return as-is if format unknown

def load_proxies_from_file():
    """Load proxies from proxies.txt file"""
    proxies = []
    if os.path.exists('proxies.txt'):
        try:
            with open('proxies.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        converted = convert_proxy_format(line)
                        proxies.append(converted)
                        if converted != line:
                            print(f"[INFO] Converted proxy: {line.split(':')[0]}:{line.split(':')[1]}")
            if proxies:
                print(f"[INFO] Loaded {len(proxies)} proxies from proxies.txt")
        except Exception as e:
            print(f"[WARNING] Could not load proxies.txt: {e}")
    return proxies

# Convert PROXY_LIST proxies to standard format
PROXY_LIST = [convert_proxy_format(p) for p in PROXY_LIST]

# Load proxies from file if USE_PROXY is enabled
if USE_PROXY:
    file_proxies = load_proxies_from_file()
    if file_proxies:
        PROXY_LIST.extend(file_proxies)

import random
def get_random_proxy():
    """Get random proxy from list"""
    if USE_PROXY and PROXY_LIST:
        return random.choice(PROXY_LIST)
    return None

# Download directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Cleanup settings
CLEANUP_DELAY = 120  # 2 minutes

def schedule_cleanup(file_path, delay=CLEANUP_DELAY):
    """Schedule file deletion after delay"""
    def cleanup():
        time.sleep(delay)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[CLEANUP] Deleted: {file_path}")
        except Exception as e:
            print(f"[CLEANUP] Error: {e}")
    
    threading.Thread(target=cleanup, daemon=True).start()
    print(f"[CLEANUP] Scheduled: {file_path}")

# Supported platforms
SUPPORTED_PLATFORMS = {
    'youtube': ['youtube.com', 'youtu.be'],
    'instagram': ['instagram.com'],
    'tiktok': ['tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com'],
    'twitter': ['twitter.com', 'x.com'],
    'facebook': ['facebook.com', 'fb.watch'],
    'reddit': ['reddit.com'],
    'pinterest': ['pinterest.com', 'pin.it'],
}

def detect_platform(url):
    """Detect which platform the URL is from"""
    try:
        domain = urlparse(url).netloc.lower().replace('www.', '')
        for platform, domains in SUPPORTED_PLATFORMS.items():
            for d in domains:
                if d in domain:
                    return platform
        return None
    except:
        return None

def download_pinterest(url, progress_callback=None):
    """Download from Pinterest using custom method with SOCKS5 proxy support"""
    try:
        # Setup session with proxy if enabled
        session = requests.Session()
        
        proxy = get_random_proxy()
        if proxy:
            print(f"[DEBUG] Using proxy for Pinterest: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            session.proxies = {
                'http': proxy,
                'https': proxy
            }
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        if progress_callback:
            progress_callback("🔍 Getting Pinterest page...")
        
        # Get the actual Pinterest URL if pin.it
        response = session.get(url, allow_redirects=True, timeout=30)
        actual_url = response.url
        
        print(f"[DEBUG] Pinterest actual URL: {actual_url}")
        
        # Extract pin ID from URL
        pin_id_match = re.search(r'/pin/(\d+)', actual_url)
        if not pin_id_match:
            return {'success': False, 'error': 'Could not extract Pinterest pin ID'}
        
        pin_id = pin_id_match.group(1)
        print(f"[DEBUG] Pinterest pin ID: {pin_id}")
        
        if progress_callback:
            progress_callback("🔍 Finding video URL...")
        
        # Try to get video URL from page HTML
        html = response.text
        
        # Look for video URLs in the HTML
        video_patterns = [
            r'"url":"(https://[^"]*\.mp4[^"]*)"',
            r'<video[^>]*src="([^"]*\.mp4[^"]*)"',
            r'"contentUrl":"([^"]*\.mp4[^"]*)"',
            r'"video_url":"([^"]*)"',
        ]
        
        video_url = None
        for pattern in video_patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1)
                # Clean up escaped characters
                video_url = video_url.replace('\\u002F', '/').replace('\\/', '/')
                print(f"[DEBUG] Found video URL: {video_url}")
                break
        
        if not video_url:
            return {'success': False, 'error': 'Could not find video URL. Pin might be an image only.'}
        
        # Download the video using same proxy with progress
        print(f"[DEBUG] Downloading Pinterest video...")
        if progress_callback:
            progress_callback("⬇️ Starting download...")
        
        video_response = session.get(video_url, stream=True, timeout=60)
        
        if video_response.status_code != 200:
            return {'success': False, 'error': f'Failed to download video (status {video_response.status_code})'}
        
        # Get file size
        total_size = int(video_response.headers.get('content-length', 0))
        
        # Save to file with progress
        filename = os.path.join(DOWNLOAD_DIR, f'pinterest_{pin_id}.mp4')
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                
                # Update progress every 100KB
                if progress_callback and total_size > 0 and downloaded % (100 * 1024) < 8192:
                    percent = (downloaded / total_size) * 100
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    progress_callback(f"⬇️ Downloading: {percent:.0f}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)")
        
        print(f"[DEBUG] Pinterest video saved: {filename}")
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return {
                'success': True,
                'file_path': filename,
                'title': f'Pinterest Video {pin_id}',
                'platform': 'pinterest'
            }
        else:
            return {'success': False, 'error': 'Downloaded file is empty'}
            
    except requests.exceptions.ProxyError as e:
        return {'success': False, 'error': f'Proxy connection failed: {str(e)}'}
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Download timeout - try again'}
    except Exception as e:
        print(f"[ERROR] Pinterest download failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': f'Pinterest download error: {str(e)}'}

def download_media(url, format_type='video', progress_callback=None):
    """Download media using yt-dlp or custom downloaders - STABLE VERSION"""
    try:
        platform = detect_platform(url)
        
        # Use custom Pinterest downloader
        if platform == 'pinterest':
            print(f"[DEBUG] Using custom Pinterest downloader")
            return download_pinterest(url, progress_callback=progress_callback)
        
        # For other platforms, use yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
        }
        
        # Add proxy if enabled
        proxy = get_random_proxy()
        if proxy:
            print(f"[DEBUG] Using proxy for yt-dlp: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            ydl_opts['proxy'] = proxy
        
        if format_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }]
        else:
            # Different format strategies for different platforms
            if platform in ['pinterest', 'instagram', 'tiktok']:
                # These platforms have limited formats - just get best available
                ydl_opts['format'] = 'best'
            else:
                # YouTube, Twitter, Facebook, Reddit - use quality limits
                ydl_opts['format'] = 'best[height<=720]/best'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Check if info is None
            if info is None:
                return {'success': False, 'error': 'Could not extract video information'}
            
            # Check if download was successful
            if 'title' not in info:
                return {'success': False, 'error': 'Invalid video data received'}
            
            if format_type == 'audio':
                filename = ydl.prepare_filename(info)
                if filename:
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
                else:
                    return {'success': False, 'error': 'Could not determine filename'}
            else:
                filename = ydl.prepare_filename(info)
                if not filename:
                    return {'success': False, 'error': 'Could not determine filename'}
            
            # Verify file exists
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                if file_size == 0:
                    os.remove(filename)
                    return {'success': False, 'error': 'Downloaded file is empty'}
                
                return {
                    'success': True,
                    'file_path': filename,
                    'title': info.get('title', 'Download'),
                    'platform': platform
                }
            else:
                return {'success': False, 'error': 'File not found after download'}
                
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'Unsupported URL' in error_msg:
            return {'success': False, 'error': 'This Pinterest link format is not supported. Try the full pinterest.com URL instead of pin.it'}
        return {'success': False, 'error': f'Download error: {error_msg}'}
    except Exception as e:
        error_msg = str(e)
        if 'NoneType' in error_msg:
            return {'success': False, 'error': 'Could not extract video data. The pin might be an image only or unavailable.'}
        return {'success': False, 'error': f'Error: {error_msg}'}

@bot.message_handler(commands=['start'])
def start(message):
    """Welcome message"""
    text = """
🎬 <b>Social Media Downloader Bot</b>

Send me any link to download!

<b>Supported:</b>
📹 YouTube
📷 Instagram  
🎵 TikTok
🐦 Twitter/X
👥 Facebook
🔴 Reddit
📌 Pinterest

<b>Commands:</b>
/start - Start
/help - Help

Add "audio" to download audio only
Example: [link] audio
    """
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    """Help message"""
    text = """
<b>How to use:</b>

1. Send any video link
2. Wait for download
3. Receive your file!

<b>Audio download:</b>
Send: [link] audio

<b>Examples:</b>
https://youtube.com/watch?v=xxx
https://tiktok.com/@user/video/xxx audio
https://instagram.com/reel/xxx

Easy! 🎉
    """
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle all messages"""
    try:
        text = message.text.strip()
        
        # Find URL
        import re
        urls = re.findall(r'https?://[^\s]+', text)
        
        if not urls:
            bot.reply_to(message, "Send me a link to download!")
            return
        
        url = urls[0]
        platform = detect_platform(url)
        
        if not platform:
            bot.reply_to(message, "❌ Platform not supported")
            return
        
        # Check if audio requested
        is_audio = any(word in text.lower() for word in ['audio', 'mp3', 'music'])
        
        # Check if ffmpeg is available for audio conversion
        if is_audio:
            try:
                import subprocess
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
                if result.returncode != 0:
                    raise Exception("ffmpeg not working")
            except:
                bot.reply_to(
                    message,
                    "❌ Audio conversion not available\n\n"
                    "ffmpeg is not installed.\n\n"
                    "Install it:\n"
                    "• Windows: choco install ffmpeg\n"
                    "• Linux: sudo apt install ffmpeg\n"
                    "• Mac: brew install ffmpeg\n\n"
                    "Or send the link without 'audio' to get the video."
                )
                return
        
        format_type = 'audio' if is_audio else 'video'
        
        # Send status
        emoji = '🎵' if is_audio else '📹'
        status = bot.reply_to(message, f"{emoji} Downloading from {platform}...\n⏳ Please wait...")
        
        # Progress update function
        last_update = [0]  # Use list to modify in nested function
        
        def update_progress(progress_text):
            """Update status message with progress"""
            import time as t
            current_time = t.time()
            # Update every 2 seconds to avoid rate limits
            if current_time - last_update[0] > 2:
                try:
                    bot.edit_message_text(progress_text, status.chat.id, status.message_id)
                    last_update[0] = current_time
                except:
                    pass
        
        # Download with progress updates
        result = download_media(url, format_type, progress_callback=update_progress)
        
        if result['success']:
            file_path = result['file_path']
            
            # Check file exists
            if not os.path.exists(file_path):
                bot.edit_message_text("❌ Download failed", status.chat.id, status.message_id)
                return
            
            # Check file size (50MB Telegram limit)
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                bot.edit_message_text(
                    f"❌ File too large ({file_size/(1024*1024):.1f}MB)\nTry: [link] audio",
                    status.chat.id,
                    status.message_id
                )
                os.remove(file_path)
                return
            
            # Warn about large files
            if file_size > 20 * 1024 * 1024:
                bot.edit_message_text(
                    f"📤 Uploading ({file_size/(1024*1024):.1f}MB)\nThis may take 1-3 minutes...",
                    status.chat.id,
                    status.message_id
                )
            else:
                bot.edit_message_text(
                    f"📤 Uploading ({file_size/(1024*1024):.1f}MB)...",
                    status.chat.id,
                    status.message_id
                )
            
            caption = f"✅ {result['title']}\n📱 {platform}"
            
            # Retry logic for file sending
            max_retries = 3
            retry_count = 0
            sent = False
            
            while retry_count < max_retries and not sent:
                try:
                    with open(file_path, 'rb') as f:
                        if format_type == 'audio':
                            bot.send_audio(message.chat.id, f, caption=caption, timeout=300)
                        else:
                            bot.send_video(message.chat.id, f, caption=caption, supports_streaming=True, timeout=300)
                    sent = True
                    print(f"[DEBUG] File sent successfully!")
                except Exception as send_error:
                    retry_count += 1
                    print(f"[WARNING] Send attempt {retry_count} failed: {send_error}")
                    if retry_count < max_retries:
                        print(f"[DEBUG] Retrying in 3 seconds...")
                        time.sleep(3)
                    else:
                        # Final failure
                        bot.edit_message_text(
                            f"❌ Failed to send file after {max_retries} attempts\n\nFile saved but Telegram upload timed out.\nTry again or check your connection.",
                            status.chat.id,
                            status.message_id
                        )
                        # Don't schedule cleanup - let user retry
                        return
            
            # Delete status
            try:
                bot.delete_message(status.chat.id, status.message_id)
            except:
                pass
            
            # Schedule cleanup
            schedule_cleanup(file_path)
        
        else:
            error = result['error']
            
            # User-friendly errors
            if 'Unsupported URL' in error:
                error = "This link format isn't supported yet.\n\nTry:\n• Regular video links\n• Update: pip install -U yt-dlp"
            elif 'private' in error.lower():
                error = "This content is private"
            elif 'not available' in error.lower():
                error = "Content not available in your region"
            
            bot.edit_message_text(f"❌ Download failed\n\n{error}", status.chat.id, status.message_id)
    
    except Exception as e:
        try:
            bot.reply_to(message, f"❌ Error: {str(e)}")
        except:
            pass

if __name__ == "__main__":
    # Credits banner
    print("=" * 60)
    print("🤖 Social Media Downloader Bot")
    print("=" * 60)
    print("👨‍💻 Developer: Younes Sedki")
    print("🔗 GitHub: https://github.com/younes-sedki/")
    print("🌐 Portfolio: https://sedkiy.dev")
    print("=" * 60)
    print()
    
    print("📁 Download folder: {DOWNLOAD_DIR}")
    print(f"🗑️  Auto-cleanup: {CLEANUP_DELAY//60} minutes")
    print(f"✅ Platforms: {', '.join(SUPPORTED_PLATFORMS.keys())}")
    
    if USE_PROXY:
        print(f"🔒 Proxy: ENABLED ({len(PROXY_LIST)} proxies loaded)")
    else:
        print(f"🔓 Proxy: DISABLED")
    
    print()
    
    # Update yt-dlp on startup (optional)
    try:
        import subprocess
        print("🔄 Updating yt-dlp...")
        subprocess.run(['pip', 'install', '-U', 'yt-dlp'], capture_output=True)
        print("✅ yt-dlp updated!")
    except:
        print("⚠️  Couldn't auto-update yt-dlp")
    
    print()
    print("=" * 60)
    print("🚀 Bot is ready! Send links to download.")
    print("=" * 60)
    print()
    
    # Start bot with auto-reconnect
    while True:
        try:
            print("🔄 Starting bot polling...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️  Connection error: {e}")
            print("🔄 Reconnecting in 5 seconds...")
            time.sleep(5)