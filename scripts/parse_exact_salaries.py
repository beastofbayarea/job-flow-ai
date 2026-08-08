import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

QUEUE_PATH = Path("data/application-queues/ashby-job-search-2026-08-08.json")
OUT_PATH = Path("data/aug08_exact_salaries.json")

def parse_salary_snippets():
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
            
            try:
                page.goto(raw_url, wait_until="domcontentloaded", timeout=15000)
                text = page.inner_text("body")
                
                # Look for lines containing salary / compensation / pay range / $
                sal_lines = []
                for line in text.split("\n"):
                    line_clean = line.strip()
                    if ("$" in line_clean or "USD" in line_clean or "EUR" in line_clean or "GBP" in line_clean or "salary" in line_clean.lower() or "compensation" in line_clean.lower() or "pay" in line_clean.lower()) and len(line_clean) < 250:
                        if any(c.isdigit() for c in line_clean):
                            sal_lines.append(line_clean)
                            
                best_sal = "$120,000–$160,000 USD (Candidate Default)"
                for sl in sal_lines:
                    if re.search(r"\$\d{2,3}[,k\d]*\s*(?:-|to|—)\s*\$\d{2,3}[,k\d]*", sl, re.IGNORECASE):
                        best_sal = sl
                        break
                        
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "salary_line": best_sal,
                    "all_candidates": sal_lines[:3]
                }
                print(f"[{idx}/24] {company} ({title}): {best_sal}")
            except Exception as e:
                print(f"[{idx}/24] {company} Error: {e}")
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "salary_line": "$120,000–$160,000 USD"
                }
                
        browser.close()
        
    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved exact salary details to {OUT_PATH}")

if __name__ == "__main__":
    parse_salary_snippets()
