import json
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

QUEUE_PATH = Path("data/application-queues/ashby-job-search-2026-08-08.json")
OUT_PATH = Path("data/aug08_job_salaries.json")

def job_posting_url(url: str) -> str:
    url = url.rstrip("/")
    if url.endswith("/application"):
        url = url[:-len("/application")]
    return url

def extract_salary_from_text(text: str) -> str:
    # Match patterns like $150,000 - $200,000 or $120k - $160k or $140,000 to $180,000
    patterns = [
        r"\$\d{2,3}(?:,\d{3})*(?:\s*(?:-|to|—)\s*\$\d{2,3}(?:,\d{3})*)?\s*(?:USD|CAD|EUR|GBP)?(?:\s*/\s*(?:yr|year|annually))?",
        r"\$\d{2,3}k(?:\s*(?:-|to|—)\s*\$\d{2,3}k)?",
        r"\d{2,3}(?:,\d{3})*\s*(?:-|to|—)\s*\d{2,3}(?:,\d{3})*\s*(?:USD|CAD|EUR|GBP)"
    ]
    
    found = []
    for p in patterns:
        matches = re.findall(p, text, flags=re.IGNORECASE)
        for m in matches:
            if "$" in m or "USD" in m or "EUR" in m or "GBP" in m:
                found.append(m.strip())
                
    if found:
        # Filter for typical annual base salary range
        for f in found:
            if any(num in f for num in ["100", "110", "120", "130", "140", "150", "160", "170", "180", "190", "200", "210", "220", "230", "240", "250"]):
                return f
        return found[0]
        
    return "$120,000–$160,000 USD (Candidate Target)"

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
            raw_url = j.get("url")
            post_url = job_posting_url(raw_url)
            
            print(f"[{idx}/{len(jobs)}] Fetching salary for {company} — {title}...")
            
            try:
                page.goto(post_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(1.0)
                body_text = page.inner_text("body")
                
                salary_found = extract_salary_from_text(body_text)
                print(f"  -> Salary detected: {salary_found}")
                
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "posting_url": post_url,
                    "extracted_salary": salary_found
                }
            except Exception as e:
                print(f"  Error on {company}: {e}")
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "posting_url": post_url,
                    "extracted_salary": "$120,000–$160,000 USD (Default Target)"
                }
                
        browser.close()
        
    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSalary extraction complete! Saved to {OUT_PATH}")

if __name__ == "__main__":
    run()
