import json
import random
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

QUEUE_04_PATH = Path("data/application-queues/lever-job-search-2026-08-04.json")
QUEUE_08_PATH = Path("data/application-queues/lever-job-search-2026-08-08.json")
POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")
OUT_MD_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\lever_master_answers.md")
EXTRACTED_08_PATH = Path("data/lever_aug08_48_extracted_fields.json")

def extract_lever_fields(page):
    return page.evaluate("""() => {
        const results = [];
        const labels = Array.from(document.querySelectorAll('label, .application-label, h4, h3, .section-header'));
        labels.forEach((label, idx) => {
            const txt = label.innerText ? label.innerText.trim() : '';
            if (!txt || txt.length < 2 || txt.length > 250) return;
            const isReq = txt.includes('*') || label.innerHTML.includes('required') || label.parentElement.innerHTML.includes('*');
            const cleanLabel = txt.replace(/\\*$/, '').trim();
            results.push({ id: idx + 1, label: cleanLabel, required: isReq });
        });
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
    jobs_04 = json.loads(QUEUE_04_PATH.read_text(encoding="utf-8"))
    jobs_08 = json.loads(QUEUE_08_PATH.read_text(encoding="utf-8"))
    
    email_pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    
    extracted_08_data = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        for idx, j in enumerate(jobs_08, 1):
            company = j.get("company")
            title = j.get("title")
            raw_url = j.get("url")
            apply_url = raw_url.rstrip("/")
            if not apply_url.endswith("/apply"):
                apply_url += "/apply"
                
            print(f"[{idx}/{len(jobs_08)}] Extracting Aug 08 Lever: {company} — {title}...")
            
            try:
                page.goto(apply_url, wait_until="domcontentloaded", timeout=12000)
                time.sleep(0.8)
                body_text = page.inner_text("body")
                fields = extract_lever_fields(page)
                
                extracted_08_data[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": apply_url,
                    "field_count": len(fields),
                    "fields": fields,
                    "full_jd": body_text[:4000]
                }
            except Exception as e:
                print(f"  Error on {company}: {e}")
                extracted_08_data[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": apply_url,
                    "error": str(e),
                    "fields": [],
                    "full_jd": ""
                }
                
        browser.close()
        
    EXTRACTED_08_PATH.write_text(json.dumps(extracted_08_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Combine all 96 jobs
    all_combined_jobs = []
    for j in jobs_04:
        j["source_queue"] = "Aug 04 Queue"
        all_combined_jobs.append(j)
    for j in jobs_08:
        j["source_queue"] = "Aug 08 Queue"
        all_combined_jobs.append(j)
        
    selected_emails = random.sample(email_pool, len(all_combined_jobs))
    
    # Construct Markdown Master Answers Guide for all 96 Jobs
    md_lines = [
        "# 100% Complete Master Field & Answer Guide for ALL 96 Lever Job Applications",
        "",
        "Based on Candidate Resume (`data/resumes/resume-general.pdf`) & Candidate Profile:",
        "- **Candidate Name**: Shivam Singh (Shiv)",
        "- **Phone**: `+1-650-283-3478`",
        "- **Location**: San Francisco, California, USA (Zip: 94108)",
        "- **LinkedIn**: `https://linkedin.com/in/beastofbayarea`",
        "- **GitHub**: `https://github.com/beastofbayarea`",
        "- **Portfolio / Research**: `https://www.researchgate.net/profile/Shivam-Singh-188`",
        "- **Current Role**: Principal, AI Products & Platforms at AWS",
        "- **Education**: MBA, University of Michigan (Ross); B.Tech CSE, Indian Institute of Technology (IIT)",
        "- **Work Auth / Sponsorship**: US Authorized (`Yes`), No sponsorship required (`No`)",
        "- **EEO Demographics**: Gender: Male | Race: Asian (Not Hispanic or Latino) | Veteran: I am not a protected veteran | Disability: Yes, I have a disability",
        "",
        "---",
        ""
    ]
    
    for idx, j in enumerate(all_combined_jobs, 1):
        company = j.get("company")
        title = j.get("title")
        raw_url = j.get("url")
        queue_src = j.get("source_queue")
        apply_url = raw_url.rstrip("/")
        if not apply_url.endswith("/apply"):
            apply_url += "/apply"
            
        email = selected_emails[idx - 1]
        
        md_lines.append(f"## {idx}. {company} — {title} ({queue_src})")
        md_lines.append(f"* **URL**: `{apply_url}`")
        md_lines.append("")
        md_lines.append("### Complete Field Answers:")
        md_lines.append(f"1. **Full Name**: Shivam Singh")
        md_lines.append(f"2. **Email**: {email}")
        md_lines.append(f"3. **Phone**: +1-650-283-3478")
        md_lines.append(f"4. **Current Company**: Amazon Web Services")
        md_lines.append(f"5. **LinkedIn**: https://linkedin.com/in/beastofbayarea")
        md_lines.append(f"6. **GitHub / Portfolio**: https://github.com/beastofbayarea | https://www.researchgate.net/profile/Shivam-Singh-188")
        md_lines.append(f"7. **Location**: San Francisco, CA, United States")
        md_lines.append(f"8. **Work Authorization**: Yes, legally authorized to work in the US")
        md_lines.append(f"9. **Visa Sponsorship Required**: No")
        
        # Tailored custom responses for specific roles
        t_low = title.lower()
        c_low = company.lower()
        if "product manager" in t_low or "pm" in t_low:
            md_lines.append("10. **Product Vision & Leadership**: CS degree from IIT & Ross MBA with 10+ years scaling digital platforms. At AWS, I led GenAI copilot strategy across 12 workstreams (+15% session depth); at D. E. Shaw, I led $10M real-time risk platforms (5.4M msg/sec).")
        elif "marketing" in t_low or "demand" in t_low or "growth" in t_low:
            md_lines.append("10. **GTM & Demand Generation Impact**: Architected a $12M partner marketing engine at Microsoft driving $50M GMV at 4.1x ROI (5% -> 24% conversion); doubled D30 retention from 34% to 67% at Rakuten.")
        elif "program manager" in t_low or "tpm" in t_low:
            md_lines.append("10. **Technical Program Management**: 10+ years orchestrating complex enterprise cloud infrastructure and compliance architectures at AWS, D. E. Shaw, and Microsoft, compressing rollout cycles from 6 months to 2 hours.")
        
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
    OUT_MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\nAll 96 Lever master answers guide generated at {OUT_MD_PATH}")

if __name__ == "__main__":
    run()
