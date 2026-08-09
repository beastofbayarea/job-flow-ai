import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding="utf-8")


def run():
    try:
        req = urllib.request.urlopen("http://localhost:9222/json/list")
        tabs = json.loads(req.read().decode("utf-8"))
        print(f"Total open tabs in Chrome: {len(tabs)}")
        for idx, t in enumerate(tabs, 1):
            title = t.get("title", "")[:50]
            url = t.get("url", "")[:80]
            print(f"  {idx}. [{t.get('type')}] {title} -> {url}")
    except Exception as e:
        print(f"Error fetching CDP tab list: {e}")


if __name__ == "__main__":
    run()
