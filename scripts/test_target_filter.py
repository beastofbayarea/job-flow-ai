import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")


def run():
    print("Testing Playwright connect_over_cdp with target_filter...")
    with sync_playwright() as p:
        try:
            # Filter ONLY actual Ashby application page targets (ignore 50+ recaptcha iframes & webworkers!)
            browser = p.chromium.connect_over_cdp(
                "http://localhost:9222",
                target_filter=lambda t: t.type == "page" and "ashbyhq.com" in t.url.lower(),
                timeout=10000,
            )
            print("INSTANT CONNECTION SUCCESS!")
            context = browser.contexts[0]
            pages = context.pages
            print(f"Connected to {len(pages)} Ashby pages in <1 second!")
            for idx, pg in enumerate(pages, 1):
                print(f"  {idx}. {pg.title()} -> {pg.url[:70]}")
            browser.close()
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    run()
