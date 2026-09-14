import os
import sys
import time
import subprocess

BASE_DOWNLOAD_DIR = "/sdcard/Download"
COOKIE_FILE = "/sdcard/Download/cookies.txt"

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def print_banner():
    banner = """
  ____  ___ ____ _   _   _  _____ ____  
 |  _ \|_ _|  __/ \ | | | |/ /_ _|  _ \ 
 | |_) || || | / _ \| |_| ' < | || | | |
 |  _ < | || |/ ___ \  _  | . \| || |_| |
 |_| \_\___|_/_/   \_\_| |__|\_\___|____/ 
                                          
      === SAFE BULK EXTRACTOR ===
"""
    print(banner)

def get_platform_info(platform_choice, raw_username):
    username = raw_username.replace("@", "").strip()
    platforms = {
        "1": (f"https://www.pinterest.com/{username}/", "Pinterest"),
        "2": (f"https://x.com/{username}/media", "X"),
        "3": (f"https://www.tiktok.com/@{username}", "TikTok"),
        "4": (f"https://www.instagram.com/{username}/", "Instagram"),
        "5": (f"https://www.youtube.com/@{username}/videos", "YouTube"),
        "6": (f"https://www.reddit.com/user/{username}/submitted/", "Reddit")
    }
    url, platform_name = platforms.get(platform_choice, (None, None))
    return url, platform_name, username

def fetch_all_media_links(profile_url):
    """
    Phase 1: Deep scan profile and return raw list of URLs.
    """
    print(f"\n[+] Scanning profile: {profile_url}")
    print("[+] Fetching all available media links... Please wait.\n")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "url",
        profile_url
    ]

    if os.path.exists(COOKIE_FILE):
        cmd.extend(["--cookies", COOKIE_FILE])

    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        raw_links = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        # Remove duplicates while preserving order
        unique_links = list(dict.fromkeys(raw_links))
        return unique_links
    
    return []

def classify_links(links):
    """
    Categorizes links into estimated video vs image categories.
    """
    video_keywords = ["/video/", "/watch", "/v/", "/reel/", "status"]
    videos = []
    pictures = []

    for link in links:
        if any(keyword in link.lower() for keyword in video_keywords):
            videos.append(link)
        else:
            pictures.append(link)

    # If classification is ambiguous, keep them combined safely
    if not videos and not pictures:
        pictures = links

    return videos, pictures

def export_links_to_file(links, platform_name, username):
    target_dir = os.path.join(BASE_DOWNLOAD_DIR, platform_name, username)
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, "extracted_links.txt")

    with open(file_path, "w") as f:
        for link in links:
            f.write(link + "\n")

    print(f"\n[✓] All links exported successfully to:\n    {file_path}")

def start_safe_download(links_to_download, target_dir, delay_seconds=10):
    os.makedirs(target_dir, exist_ok=True)
    total = len(links_to_download)

    print(f"\n[+] Starting safe download for {total} items.")
    print(f"[+] Pause timer set to {delay_seconds} seconds between downloads.\n")

    for index, item_url in enumerate(links_to_download, start=1):
        print(f"[{index}/{total}] Processing: {item_url}")

        cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",        # Always require video + audio together
            "--merge-output-format", "mp4",          # Combine into a single MP4 video file
            "--match-filter", "vcodec != 'none'",   # Reject any standalone audio-only stream
            "-o", f"{target_dir}/%(title)s.%(ext)s",
            item_url
        ]

        if os.path.exists(COOKIE_FILE):
            cmd.extend(["--cookies", COOKIE_FILE])

        subprocess.run(cmd)

        if index < total:
            print(f"[⏱] Waiting {delay_seconds} seconds before fetching the next link...")
            time.sleep(delay_seconds)

    print(f"\n[✓] Completed safe extraction for all items! Saved to:\n    {target_dir}")

def main():
    while True:
        clear_screen()
        print_banner()
        print("--- SELECT PLATFORM FOR SCANNING ---")
        print(" 1. Pinterest")
        print(" 2. X / Twitter (Media Tab)")
        print(" 3. TikTok")
        print(" 4. Instagram")
        print(" 5. YouTube")
        print(" 6. Reddit")
        print(" 0. Exit")
        print("-----------------------------------")

        choice = input("Select platform [0-6]: ").strip()
        if choice == "0":
            print("\nExiting. Goodbye Rich Kid!")
            sys.exit(0)

        if choice not in ["1", "2", "3", "4", "5", "6"]:
            continue

        raw_username = input("\nEnter Username (with or without @): ").strip()
        if not raw_username:
            continue

        profile_url, platform_name, username = get_platform_info(choice, raw_username)
        
        # Step 1: Deep scan profile
        all_links = fetch_all_media_links(profile_url)

        if not all_links:
            print("\n[!] No links found or the profile is private/restricted.")
            if choice in ["2", "4"]:  # X or Instagram
                print("[!] Reminder: X and Instagram require a valid 'cookies.txt' file in /sdcard/Download/")
            input("\nPress Enter to try again...")
            continue

        # Step 2: Classify and summarize
        video_links, picture_links = classify_links(all_links)

        clear_screen()
        print_banner()
        print(f"--- EXTRACTION REPORT FOR @{username} ({platform_name}) ---")
        print(f" 🎬 Estimated Video Links Found  : {len(video_links)}")
        print(f" 🖼️  Estimated Picture Links Found: {len(picture_links)}")
        print(f" 📦 Total Combined Links Found   : {len(all_links)}")
        print("---------------------------------------------------------")
        print(" Choose an action:")
        print("  1. Automate download for ALL links (10s safe delay)")
        print("  2. Automate download for VIDEOS only (Video + Audio combined)")
        print("  3. Automate download for PICTURES only")
        print("  4. Export link list to a .txt file (Copy/Paste manually)")
        print("  0. Back to main menu")
        print("---------------------------------------------------------")

        action = input("Select option [0-4]: ").strip()

        target_dir = os.path.join(BASE_DOWNLOAD_DIR, platform_name, username)

        if action == "1":
            start_safe_download(all_links, target_dir, delay_seconds=10)
        elif action == "2":
            start_safe_download(video_links, target_dir, delay_seconds=10)
        elif action == "3":
            start_safe_download(picture_links, target_dir, delay_seconds=10)
        elif action == "4":
            export_links_to_file(all_links, platform_name, username)

        input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

