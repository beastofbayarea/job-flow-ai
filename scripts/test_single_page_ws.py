import json
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")


def run():
    tabs = json.loads(
        urllib.request.urlopen("http://localhost:9222/json/list").read().decode("utf-8")
    )
    ashby_pages = [
        t for t in tabs if t.get("type") == "page" and "ashbyhq.com" in t.get("url", "").lower()
    ]

    print(f"Found {len(ashby_pages)} Ashby page targets.")
    if not ashby_pages:
        return

    first = ashby_pages[0]
    ws_url = first["webSocketDebuggerUrl"]
    print(f"Testing WS URL: {ws_url} for tab: {first.get('url')}")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]

        print("Checking context pages...")
        time.sleep(1)
        pages = context.pages
        print(f"Pages count: {len(pages)}")

        if not pages:
            # Try getting pages via new_page or attaching
            print("Context pages empty, checking targets/browser...")
            p_test = context.new_page()
            print(f"New page created/attached: {p_test.url}")
        else:
            print(f"Existing page URL: {pages[0].url}")

        browser.close()


if __name__ == "__main__":
    run()
