import json
import re
import sys
import time
import urllib.request
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

MD_PATH = Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\ashby_master_answers.md")
CDP_URL = "http://localhost:9222"


def ensure_chrome_debugging():
    try:
        req = urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=2)
        print("Chrome Remote Debugging is already running on port 9222.")
        return True
    except Exception:
        print(
            "Chrome Remote Debugging port 9222 not responding. Launching Chrome with remote debugging..."
        )
        # Common Chrome paths on Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        exe = None
        for p in chrome_paths:
            if os.path.exists(p):
                exe = p
                break

        if not exe:
            print("Could not find chrome.exe path automatically.")
            return False

        subprocess.Popen([exe, "--remote-debugging-port=9222"])
        time.sleep(3)
        return True


def create_cdp_tab(target_url):
    # Call CDP HTTP endpoint /json/new?url
    encoded_url = urllib.parse.quote(target_url, safe="")
    req_url = f"{CDP_URL}/json/new?{encoded_url}"
    try:
        req = urllib.request.Request(req_url, method="PUT")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("id")
    except Exception as e:
        # Fallback to GET
        try:
            with urllib.request.urlopen(f"{CDP_URL}/json/new?{encoded_url}") as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("id")
        except Exception as ex:
            print(f"Error opening tab for {target_url}: {ex}")
            return None


def run():
    if not ensure_chrome_debugging():
        print("Failed to ensure Chrome debugging session.")
        return

    text = MD_PATH.read_text(encoding="utf-8")

    # Extract all Ashby application URLs
    raw_urls = re.findall(r"\*+\s*URL\*+:\s*`([^`]+)`", text)

    urls = []
    for u in raw_urls:
        u_clean = u.strip().rstrip("/")
        if "ashbyhq.com" in u_clean and not u_clean.endswith("/application"):
            u_clean += "/application"
        urls.append(u_clean)

    # Deduplicate while preserving order
    unique_urls = []
    seen = set()
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    print(f"Found {len(unique_urls)} unique Ashby application URLs to open in Chrome debug:")

    opened_tabs = []
    for idx, u in enumerate(unique_urls, 1):
        print(f"[{idx}/{len(unique_urls)}] Opening tab for: {u}")
        tab_id = create_cdp_tab(u)
        if tab_id:
            opened_tabs.append((u, tab_id))
        time.sleep(0.5)

    print(
        f"\nSuccessfully opened {len(opened_tabs)} Ashby application tabs in Chrome debug session!"
    )


if __name__ == "__main__":
    import os, urllib.parse

    run()
