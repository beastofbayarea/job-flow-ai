import json
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

QUEUE_PATH = Path("data/application-queues/ashby-job-search-2026-08-08.json")
OUT_PATH = Path("data/aug08_full_job_descriptions.json")

def run():
    jobs = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        for idx, j in enumerate(jobs, 1):
            company = j.get("company")
            title = j.get("title")
            raw_url = j.get("url").rstrip("/").replace("/application", "")
            
            print(f"[{idx}/24] Fetching full JD for {company} — {title}...")
            
            try:
                page.goto(raw_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(1.0)
                jd_text = page.inner_text("body")
                
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": raw_url,
                    "text_length": len(jd_text),
                    "full_jd": jd_text[:8000]
                }
            except Exception as e:
                print(f"  Error on {company}: {e}")
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": raw_url,
                    "error": str(e),
                    "full_jd": ""
                }
                
        browser.close()
        
    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved full JDs to {OUT_PATH}")

if __name__ == "__main__":
    run()
