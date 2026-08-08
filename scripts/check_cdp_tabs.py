import urllib.request
import json

try:
    with urllib.request.urlopen("http://localhost:9222/json/list") as resp:
        targets = json.load(resp)
        print("Chrome remote debugging port 9222 is ACTIVE!")
        print(f"Total targets/tabs open: {len(targets)}")
        for t in targets:
            print(f"- ID: {t.get('id')} | Title: {t.get('title')} | URL: {t.get('url')}")
except Exception as e:
    print(f"Could not connect to http://localhost:9222: {e}")
