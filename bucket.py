import os
import time
import re
import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_context=ctx,
                                       **pool_kwargs)

session = requests.Session()
session.mount("https://", SSLAdapter())
import pyperclip
import logging
import threading

# Setup logging
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(filename='logs/monitor_clipboard.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Global lists to track downloaded files
downloaded_files = []          # List of filenames for console display
downloaded_filenames = set()   # Set of filenames to avoid duplicates

def update_console_file():
    """Write the current downloaded files list to a text file for console display."""
    with open("downloaded_files.txt", "w") as f:
        for fname in downloaded_files:
            f.write(fname + "\n")

def update_failed_urls(url, action="add"):
    file_path = "failed_urls.txt"
    # Read current failed URLs from file
    failed_urls = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            failed_urls = [line.strip() for line in f if line.strip()]
    if action == "add":
        if url not in failed_urls:
            failed_urls.append(url)
    elif action == "remove":
        if url in failed_urls:
            failed_urls.remove(url)
    with open(file_path, 'w') as f:
        for u in failed_urls:
            f.write(u + "\n")

def download_pdf(url, folder):
    # Extract the file name from the URL; default to "downloaded.pdf" if not found
    filename = url.split("/")[-1] or "downloaded.pdf"
    filepath = os.path.join(folder, filename)
    try:
        response = session.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print(f"Downloaded: {url} to {filepath}")
        logging.info(f"Downloaded: {url} to {filepath}")
        return True, filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        logging.error(f"Failed to download {url}: {e}")
        update_failed_urls(url, action="add")
        return False, filename

def launch_console():
    """
    Launch a separate console window that displays the downloaded files in a text-based interface.
    This uses a separate Python script (console_display.py) to continuously show the list.
    """
    # Check if console_display.py exists; if not, create it.
    console_display_path = "console_display.py"
    if not os.path.exists(console_display_path):
        with open(console_display_path, "w") as f:
            f.write("import time, os\\n")
            f.write("from pathlib import Path\\n\\n")
            f.write("while True:\\n")
            f.write("    os.system('cls')\\n")
            f.write("    f = Path('downloaded_files.txt')\\n")
            f.write("    if f.exists():\\n")
            f.write("        print('Downloaded Files:')\\n")
            f.write("        print(f.read_text())\\n")
            f.write("    else:\\n")
            f.write("        print('No downloads yet.')\\n")
            f.write("    time.sleep(1)\\n")
    # Launch a new console window running the console_display.py script
    os.system("start cmd /k python console_display.py")

def process_failed_downloads(folder):
    file_path = "failed_urls.txt"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        if urls:
            print("Processing failed downloads...")
            logging.info("Processing failed downloads...")
            remaining = []
            for url in urls:
                fname = url.split("/")[-1] or "downloaded.pdf"
                # Skip if the file was already downloaded by filename
                if fname in downloaded_filenames:
                    print(f"Skipping previously downloaded file {fname} from failed list.")
                    logging.info(f"Skipping previously downloaded file {fname} from failed list.")
                    continue
                success, filename = download_pdf(url, folder)
                if success:
                    downloaded_files.append(filename)
                    downloaded_filenames.add(filename)
                    update_console_file()
                    update_failed_urls(url, action="remove")
                else:
                    remaining.append(url)
            # Overwrite failed_urls.txt with remaining failures
            with open(file_path, 'w') as f:
                for u in remaining:
                    f.write(u + "\n")

def main():
    # Create the folder if it does not exist
    folder = "downloads"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Launch the text-based console display in a new window (PowerShell/CMD style)
    console_thread = threading.Thread(target=launch_console, daemon=True)
    console_thread.start()

    # Process failed downloads first
    process_failed_downloads(folder)

    # Keep track of processed URLs in this session
    processed_urls = set()

    print("Monitoring clipboard. Press Ctrl+C to exit.")
    try:
        while True:
            clip = pyperclip.paste()
            # Log clipboard content if there's any PDF URL
            if re.search(r'https?://\S+\.pdf', clip, re.IGNORECASE):
                logging.info(f"Clipboard changed: {clip}")
            if clip:
                links = re.findall(r'(https?://\S+\.pdf)', clip, re.IGNORECASE)
                for link in links:
                    filename = link.split("/")[-1] or "downloaded.pdf"
                    # Skip download if this filename has been downloaded before
                    if filename in downloaded_filenames:
                        print(f"Skipping duplicate file: {filename}")
                        logging.info(f"Skipping duplicate file: {filename}")
                        continue
                    if link not in processed_urls:
                        success, fname = download_pdf(link, folder)
                        processed_urls.add(link)
                        if success:
                            downloaded_files.append(fname)
                            downloaded_filenames.add(fname)
                            update_console_file()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        logging.info("Exiting monitor.")

if __name__ == '__main__':
    main()
