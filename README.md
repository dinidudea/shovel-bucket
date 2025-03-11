# Shovel+Bucket
Shovel is a Google Chrome Extension that copies all URLs from your current page into the clipboard. Bucket is a simple tool that monitors your clipboard and downloads all PDF files from it. Together, you can use Shovel and Bucket to scrape websites.

## Installing Shovel

1.  **Download the extension files:**
2.  **Open Chrome's Extensions page:**
    * Open Google Chrome.
    * In the address bar, type `chrome://extensions/` and press Enter.
3.  **Enable Developer mode:**
    * In the top right corner of the Extensions page, toggle the "Developer mode" switch to the "on" position.
4.  **Click "Load unpacked":**
    * Click the "Load unpacked" button in the top left corner of the Extensions page.
5.  **Select the extension folder:**
    * Navigate to the folder containing the extension files and select it.
    * Click "Select Folder" or "Open".
6.  *Make sure "Pin to toolbar is enabled."

## Installing Bucket

1. **Ensure Python 3 is installed** on your system.

2. **(Optional) Set up a virtual environment:**

   - **Windows:**
     ```
     python -m venv env
     env\Scripts\activate
     ```
   - **macOS/Linux:**
     ```
     python3 -m venv env
     source env/bin/activate
     ```

3. **Install required packages:**
   ```
   pip install requests pyperclip
   ```

3. **Run the script:**
   ```
   python bucket.py
   ```

   A separate text-based console window will open, which will continuously display the list of downloaded filenames.

## Logging

- All clipboard URLs, successful downloads, and failures are logged in `logs/monitor_clipboard.log`.
- Failed downloads are recorded in `failed_urls.txt` and automatically reprocessed on startup.

Go forth and scrape (but responsibly).
