# 🚀 AnyVideo Downloader

**Developer: dr1p7.steez**

A powerful and advanced video downloader that can download videos from **1000+ websites** in the best quality available. Built with Flask and modern web technologies.

## 🔒 Security Features

This application includes comprehensive security protections:
- ✅ **Input Validation** - XSS, SQL injection, code injection protection
- ✅ **Rate Limiting** - DDoS and abuse prevention (10-60 requests/min)
- ✅ **SSRF Prevention** - Blocks internal/private network access
- ✅ **Security Headers** - XSS, clickjacking, MIME sniffing protection
- ✅ **Request Validation** - JSON validation, size limits (2KB max)
- ✅ **Anti-Injection** - Command, path traversal protection
- ✅ **Content Sanitization** - HTML stripping, malicious content removal

## ✨ Features

- 📺 **Universal Support**: Download from YouTube, TikTok, Instagram, Twitter, Facebook, Vimeo, Twitch, Reddit, and 1000+ more websites
- 🎯 **Best Quality**: Always downloads in the highest quality available
- 🔓 **Advanced Bypass**: Geo-restrictions, age verification, SSL issues, and anti-bot protection
- 🌍 **Geo-Bypass**: Download region-locked content from anywhere
- 🛡️ **Protection Bypass**: Age restrictions, SSL certificates, website protections
- 🎨 **Modern UI**: Beautiful, responsive web interface with real-time progress tracking
- ⚡ **Fast & Efficient**: Multi-threaded downloads with progress monitoring
- 📊 **Download History**: Keep track of all your downloads
- 🎵 **Audio Extraction**: Download audio-only in MP3 format
- 🎬 **Multiple Quality Options**: Choose from 4K, 1080p, 720p, or best available
- 💾 **Smart Merging**: Automatically merges best video and audio streams
- 🔄 **Auto-Retry**: 10 retries with 5 extractor attempts for maximum reliability
- 🧹 **Auto-Cleanup**: Removes old files every hour to save storage

## 🌐 Supported Websites

This downloader supports over 1000 websites including:

- **Video Platforms**: YouTube (age-restricted, geo-blocked), Vimeo, Dailymotion, Twitch
- **Social Media**: TikTok, Instagram, Twitter/X, Facebook, Reddit
- **Music**: SoundCloud, Bandcamp, Mixcloud
- **And many more!**

### 🔓 Bypass Capabilities

- ✅ **Geo-restricted content** (region-locked videos)
- ✅ **Age-restricted content** (no login required)
- ✅ **SSL/Certificate issues** (expired or self-signed certificates)
- ✅ **Anti-bot protection** (mimics real browser)
- ✅ **Network issues** (auto-retry with 10 attempts)
- ❌ **DRM-protected content** (Netflix, Disney+, Hulu, etc. - **ILLEGAL** to bypass)

## 📋 Requirements

- Python 3.8 or higher
- FFmpeg (for merging video and audio streams)

## 🔧 Installation

### Step 1: Install Python

Make sure you have Python 3.8+ installed. Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install FFmpeg

FFmpeg is required for merging video and audio streams.

**Windows:**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the zip file
3. Add the `bin` folder to your system PATH
4. Or use Chocolatey: `choco install ffmpeg`

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 3: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- **Flask-Limiter** (rate limiting - SECURITY)
- **Flask-Talisman** (security headers - SECURITY)
- Video processing engine
- gunicorn (production server)
- requests (HTTP library)
- curl-cffi (Cloudflare bypass)
- **bleach** (input sanitization - SECURITY)

## 🚀 Usage

### Starting the Application

**Local Development:**
```bash
python app.py
```

Then open your browser and go to:
```
http://localhost:5000
```

### Using the Web Interface

1. **Paste Video URL**: Enter the URL of the video you want to download
2. **Get Info** (Optional): Click to preview video information
3. **Select Quality**: Choose from Best, 4K, 1080p, 720p, or 480p
4. **Select Format**: Choose Video or Audio (MP3)
5. **Download**: Click the download button
6. **Monitor Progress**: Watch the real-time progress bar
7. **Access File**: Video will download to your browser's Downloads folder

## 🌐 Deploy to Wispbyte (Free 24/7 Hosting)

### Quick Deploy Steps:

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy AnyVideo Downloader"
   git remote add origin YOUR_GITHUB_URL
   git push -u origin main
   ```

2. **Deploy on Wispbyte**:
   - Go to [Wispbyte.com](https://wispbyte.com/)
   - Sign up (FREE)
   - Create new **Web Application**
   - Select **Docker** deployment
   - Link your GitHub repository
   - Set **Port**: `5000`
   - Set **Branch**: `main`
   - Click **Deploy**

3. **Wait 2-5 minutes** for build to complete

4. **Your app is live 24/7!** 🎉

### Why Wispbyte?

- ✅ **100% Free** with 24/7 uptime
- ✅ **No renewals** required
- ✅ **100,000+ users** - trusted platform
- ✅ **Videos save to user's PC** (not server)
- ✅ **Auto-cleanup** prevents storage bloat
- ✅ **Container-based** hosting

## 📝 API Endpoints

### `POST /api/info`
Get video information without downloading.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "title": "Video Title",
  "duration": 180,
  "thumbnail": "https://...",
  "uploader": "Channel Name",
  "view_count": 1000000,
  "description": "Video description..."
}
```

### `POST /api/download`
Start a video download.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "quality": "best",
  "format": "video"
}
```

**Response:**
```json
{
  "download_id": "download_1234567890",
  "message": "Download started"
}
```

### `GET /api/progress/<download_id>`
Get download progress.

**Response:**
```json
{
  "status": "downloading",
  "progress": 45.5,
  "title": "Video Title",
  "file_path": "/path/to/file.mp4"
}
```

## 🔧 Troubleshooting

### FFmpeg not found
- Install FFmpeg using the instructions above
- Make sure FFmpeg is in your system PATH
- Test by running `ffmpeg -version` in terminal

### Video not downloading
- **Geo-blocked**: Automatically bypassed (US location spoofed)
- **Age-restricted**: Automatically bypassed (no login needed)
- **Still failing**: Update dependencies: `pip install --upgrade -r requirements.txt`
- **DRM-protected**: Cannot bypass (Netflix, Disney+, etc.)
- **Private/deleted**: Video might not be accessible

### "Video unavailable" errors
- **First, update dependencies**: `pip install --upgrade -r requirements.txt`
- Try different quality setting (lower quality often works)
- Remove URL tracking parameters (everything after `?`)
- Check if video is truly unavailable

### Rate limit errors
- This is normal - prevents abuse
- Wait a moment and try again
- Rate limits: 10-60 requests/minute depending on endpoint

### Cloudflare errors
- Install Cloudflare bypass: `pip install curl-cffi`
- Restart the application
- Most sites will work without this

## 🔒 Security & Privacy

### Built-in Security:
- ✅ Input validation (XSS, SQL injection prevention)
- ✅ Rate limiting (abuse prevention)
- ✅ SSRF prevention (blocks localhost/private IPs)
- ✅ Security headers (XSS, clickjacking protection)
- ✅ Request size limits (DOS prevention)

### Privacy:
- Videos are downloaded **temporarily** on server
- Files are **sent to user's browser** immediately
- Server **auto-deletes** files after 1 hour
- **No data logging** or user tracking

## ⚖️ Legal Notice

- ✅ Respect copyright laws
- ✅ Only download videos you have permission to download
- ✅ DRM-protected content (Netflix, Disney+, etc.) **cannot** and **will not** be bypassed
- ✅ This tool is for personal, legal use only
- ⚠️ Users are responsible for their own usage

## 📄 License

This project is licensed under the MIT License.

**Developer: dr1p7.steez**

---

## 🎯 Features Summary

| Feature | Status |
|---------|--------|
| 1000+ Website Support | ✅ |
| Best Quality Downloads | ✅ |
| Geo-Bypass | ✅ |
| Age-Restriction Bypass | ✅ |
| SSL/Certificate Bypass | ✅ |
| Audio Extraction (MP3) | ✅ |
| Multiple Quality Options | ✅ |
| Progress Tracking | ✅ |
| Download History | ✅ |
| Modern UI | ✅ |
| Security Features | ✅ |
| Rate Limiting | ✅ |
| Auto-Cleanup | ✅ |
| Free 24/7 Hosting Ready | ✅ |

## 🌟 Why Choose This Downloader?

1. **Universal Support** - Works with 1000+ websites
2. **Advanced Bypass** - Geo-restrictions, age limits, SSL issues
3. **Best Quality** - Always gets highest quality available
4. **Secure** - Built-in security protections
5. **Fast** - Multi-threaded downloads
6. **Easy to Use** - Beautiful web interface
7. **Free to Deploy** - Wispbyte hosting ready
8. **Auto-Cleanup** - No storage bloat
9. **Production Ready** - Docker containerized

---

**Made with ❤️ by dr1p7.steez**

**Ready for free 24/7 deployment on Wispbyte!** 🚀
