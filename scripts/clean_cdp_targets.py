import json
import urllib.request
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

CDP_URL = "http://localhost:9222"


def run():
    try:
        req = urllib.request.urlopen(f"{CDP_URL}/json/list")
        targets = json.loads(req.read().decode("utf-8"))
        print(f"Total CDP Targets before cleanup: {len(targets)}")

        closed = 0
        for t in targets:
            t_type = t.get("type", "")
            t_url = t.get("url", "")
            t_id = t.get("id")

            # Close recaptcha workers, iframes, and omnibox popups
            if t_type in ["iframe", "worker", "other", "browser_ui"] or "recaptcha" in t_url:
                try:
                    urllib.request.urlopen(f"{CDP_URL}/json/close/{t_id}")
                    closed += 1
                except Exception:
                    pass

        print(f"Closed {closed} background subtargets!")

        # Verify remaining targets
        req2 = urllib.request.urlopen(f"{CDP_URL}/json/list")
        targets2 = json.loads(req2.read().decode("utf-8"))
        print(f"Remaining CDP Targets: {len(targets2)}")
        for idx, t in enumerate(targets2, 1):
            print(
                f"  {idx}. [{t.get('type')}] {t.get('title', '')[:40]} -> {t.get('url', '')[:60]}"
            )
    except Exception as e:
        print(f"Error during target cleanup: {e}")


if __name__ == "__main__":
    run()
