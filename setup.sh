#!/bin/bash
pkg update -y && pkg install python ffmpeg -y
pip install requests yt-dlp
curl -O https://raw.githubusercontent.com/sadiqumaru41-creator/termux-downloader/main/dl.py
curl -O https://raw.githubusercontent.com/sadiqumaru41-creator/termux-downloader/main/bulk.py
echo "Setup complete! Run 'python dl.py' to start."
