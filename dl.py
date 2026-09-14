import os
import sys
import subprocess
import requests
from bs4 import BeautifulSoup

# Base Download Directory in phone gallery
BASE_DOWNLOAD_DIR = "/sdcard/Download"

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def print_banner():
    banner = """
  ____  ___ ____ _   _   _  _____ ____  
 |  _ \|_ _|  __/ \ | | | |/ /_ _|  _ \ 
 | |_) || || | / _ \| |_| ' < | || | | |
 |  _ < | || |/ ___ \  _  | . \| || |_| |
 |_| \_\___|_/_/   \_\_| |__|\_\___|____/ 
                                          
      === MEDIA DOWNLOADER HUB ===
"""
    print(banner)

def get_quality_format(quality_choice):
    # HD: Best video + best audio merged
    if quality_choice == "1":
        return "bestvideo+bestaudio/best"
    # SD: Up to 720p or standard video
    elif quality_choice == "2":
        return "bestvideo[height<=720]+bestaudio/best[height<=720]/best"
    # Audio Only MP3
    elif quality_choice == "3":
        return "bestaudio/best"
    return "bestvideo+bestaudio/best"

def download_pinterest_image(url, target_dir):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        img_tag = soup.find("property", {"property": "og:image"}) or soup.find("meta", {"name": "og:image"})
        
        if img_tag and img_tag.get("content"):
            img_url = img_tag["content"]
            img_data = requests.get(img_url).content
            filename = os.path.join(target_dir, img_url.split("/")[-1])
            
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"[✓] Image saved to: {filename}")
            return True
    except Exception as e:
        print(f"[!] Image scraping error: {e}")
    return False

def process_download(platform_name, quality_choice):
    target_dir = os.path.join(BASE_DOWNLOAD_DIR, platform_name)
    os.makedirs(target_dir, exist_ok=True)

    while True:
        clear_screen()
        print_banner()
        print(f"--- {platform_name.upper()} DOWNLOADER ---")
        print("Type 'back' to return to the main menu.\n")
        
        url = input(f"Paste {platform_name} link: ").strip()
        
        if url.lower() == "back":
            break
        if not url:
            continue

        print(f"\n[+] Processing {platform_name} URL: {url}")
        format_spec = get_quality_format(quality_choice)

        # Build yt-dlp command
        command = [
            "yt-dlp",
            "-f", format_spec,
            "-o", f"{target_dir}/%(title)s.%(ext)s",
            url
        ]

        if quality_choice == "3":
            command.extend(["-x", "--audio-format", "mp3"])

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"\n[✓] Download finished! Saved to: {target_dir}")
        else:
            # Pinterest fallback for images
            if platform_name.lower() == "pinterest":
                print("[!] Video download failed or not detected. Extracting high-res image...")
                success = download_pinterest_image(url, target_dir)
                if not success:
                    print("[!] Could not extract media from this Pinterest link.")
            else:
                print(f"[!] Download failed: {result.stderr.strip()[:150]}")

        input("\nPress Enter to continue...")

def select_quality():
    clear_screen()
    print_banner()
    print("--- SELECT QUALITY ---")
    print(" 1. HD (Best Available Quality)")
    print(" 2. SD (Standard 720p Quality)")
    print(" 3. Audio Only (MP3)")
    print(" 4. Back")
    print("----------------------")
    choice = input("Select quality option [1-4]: ").strip()
    return choice if choice in ["1", "2", "3"] else None

def main_menu():
    platforms = {
        "1": "Pinterest",
        "2": "X",
        "3": "Facebook",
        "4": "Instagram",
        "5": "TikTok",
        "6": "YouTube",
        "7": "Snapchat",
        "8": "Reddit",
        "9": "LinkedIn",
        "10": "Twitch"
    }

    while True:
        clear_screen()
        print_banner()
        print("--- PLATFORM MENU ---")
        for key, name in platforms.items():
            print(f" {key}. {name}")
        print(" 0. Exit")
        print("---------------------")

        choice = input("Select platform [0-10]: ").strip()

        if choice == "0":
            print("\nExiting. Goodbye Rich Kid!")
            sys.exit(0)

        if choice in platforms:
            platform_name = platforms[choice]
            quality = select_quality()
            if quality:
                process_download(platform_name, quality)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
        sys.exit(0)

