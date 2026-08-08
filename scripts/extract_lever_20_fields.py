import json
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

QUEUE_PATH = Path("data/application-queues/lever-job-search-2026-08-04.json")
OUT_FIELDS_PATH = Path("data/lever_20_extracted_fields.json")

def extract_lever_fields(page):
    return page.evaluate("""() => {
        const results = [];
        // Lever forms use .application-field, input, textarea, select, or text headings
        const fields = Array.from(document.querySelectorAll('input, textarea, select, .application-question'));
        
        const labels = Array.from(document.querySelectorAll('label, .application-label, h4, h3, .section-header'));
        labels.forEach((label, idx) => {
            const txt = label.innerText ? label.innerText.trim() : '';
            if (!txt || txt.length < 2 || txt.length > 250) return;
            const isReq = txt.includes('*') || label.innerHTML.includes('required') || label.parentElement.innerHTML.includes('*');
            const cleanLabel = txt.replace(/\\*$/, '').trim();
            
            results.push({
                id: idx + 1,
                label: cleanLabel,
                required: isReq
            });
        });
        
        // Deduplicate
        const unique = [];
        const seen = new Set();
        results.forEach(r => {
            const k = r.label.toLowerCase().replace(/[^a-z0-9]/g, '');
            if (k && !seen.has(k)) {
                seen.add(k);
                unique.push(r);
            }
        });
        
        return unique;
    }""")

def run():
    all_jobs = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    first_20 = all_jobs[:20]
    
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        for idx, j in enumerate(first_20, 1):
            company = j.get("company")
            title = j.get("title")
            raw_url = j.get("url")
            # For Lever, add /apply if not present
            apply_url = raw_url.rstrip("/")
            if not apply_url.endswith("/apply"):
                apply_url += "/apply"
                
            print(f"[{idx}/20] Fetching Lever job: {company} — {title}...")
            
            try:
                page.goto(apply_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(1.2)
                body_text = page.inner_text("body")
                fields = extract_lever_fields(page)
                
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": apply_url,
                    "field_count": len(fields),
                    "fields": fields,
                    "full_jd": body_text[:6000]
                }
            except Exception as e:
                print(f"  Error on {company}: {e}")
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": apply_url,
                    "error": str(e),
                    "fields": [],
                    "full_jd": ""
                }
                
        browser.close()
        
    OUT_FIELDS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nLever extraction finished! Saved to {OUT_FIELDS_PATH}")

if __name__ == "__main__":
    run()
