import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

MD_PATH = Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\ashby_master_answers.md")
CDP_URL = "http://localhost:9222"


def parse_ashby_answers():
    text = MD_PATH.read_text(encoding="utf-8")
    sections = re.split(r"(^## \d+\. .*$)", text, flags=re.MULTILINE)
    apps_data = []
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i + 1]
        m_comp = re.search(r"## \d+\.\s*(.*?)\s*—\s*(.*?)$", header.strip())
        company = m_comp.group(1).strip() if m_comp else "Company"
        title = m_comp.group(2).strip() if m_comp else "Role"
        m_url = re.search(r"\*+\s*URL\*+:\s*`([^`]+)`", body)
        url = m_url.group(1).strip() if m_url else ""

        email_match = re.search(r"Email\*+:?\s*([^\n]+)", body)
        email = email_match.group(1).strip(" `") if email_match else "shivamsin14@umich.edu"

        salary_match = re.search(r"Salary\*+:?\s*([^\n]+)", body)
        salary = salary_match.group(1).strip(" `") if salary_match else "$120,000–$160,000 USD"

        essay_match = re.search(r">\s*(.*)", body)
        essay = (
            essay_match.group(1).strip()
            if essay_match
            else (
                "IIT CS graduate & Ross MBA with 10+ years experience spanning AWS, D. E. Shaw, and Microsoft."
            )
        )

        apps_data.append(
            {
                "company": company,
                "title": title,
                "url": url,
                "email": email,
                "salary": salary,
                "essay": essay,
            }
        )
    return apps_data


def fill_page_js(page, app):
    print(f"  Filling form: {app['company']} — {app['title']} ({app['email']})")

    js_code = f"""() => {{
        const app = {json.dumps(app)};
        
        function setInputValue(el, val) {{
            if (!el) return;
            el.focus();
            el.value = val;
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
        }}
        
        const textAnswers = {{
            "name": "Shivam Singh",
            "first name": "Shivam",
            "last name": "Singh",
            "preferred name": "Shiv",
            "email": app.email,
            "phone": "+1-650-283-3478",
            "location": "San Francisco, California, United States",
            "current company": "Amazon Web Services (AWS)",
            "current title": "Principal, AI Products & Platforms",
            "linkedin": "https://linkedin.com/in/beastofbayarea",
            "github": "https://github.com/beastofbayarea",
            "portfolio": "https://www.researchgate.net/profile/Shivam-Singh-188",
            "website": "https://github.com/beastofbayarea",
            "twitter": "https://x.com/BeastofBayArea",
            "notice": "2 weeks",
            "salary": app.salary,
            "compensation": app.salary
        }};
        
        const inputs = Array.from(document.querySelectorAll("input[type='text'], input[type='email'], input[type='tel'], input:not([type])"));
        inputs.forEach(inp => {{
            const lbl = (inp.closest('label, div, section')?.innerText || '').toLowerCase();
            const attr = ((inp.name || '') + ' ' + (inp.placeholder || '') + ' ' + (inp.id || '')).toLowerCase();
            const comb = lbl + ' ' + attr;
            
            let filled = false;
            for (const [k, v] of Object.entries(textAnswers)) {{
                if (comb.includes(k)) {{
                    setInputValue(inp, v);
                    filled = true;
                    break;
                }}
            }}
            if (!filled) {{
                if (comb.includes('email')) setInputValue(inp, app.email);
                else if (comb.includes('phone')) setInputValue(inp, '+1-650-283-3478');
                else if (comb.includes('linkedin')) setInputValue(inp, 'https://linkedin.com/in/beastofbayarea');
                else if (comb.includes('github')) setInputValue(inp, 'https://github.com/beastofbayarea');
                else if (comb.includes('name') && !comb.includes('company')) setInputValue(inp, 'Shivam Singh');
            }}
        }});
        
        const textareas = Array.from(document.querySelectorAll('textarea'));
        textareas.forEach(ta => setInputValue(ta, app.essay));
        
        // Work Auth / Sponsorship radio buttons & dropdowns
        const labels = Array.from(document.querySelectorAll('label, div, p, span'));
        labels.forEach(el => {{
            const txt = (el.innerText || '').toLowerCase();
            if (txt.includes('authorized') || txt.includes('work in the us') || txt.includes('legally authorized')) {{
                const yesInput = el.closest('div, section, fieldset')?.querySelector('input[value="Yes"], input[value="yes"]');
                if (yesInput) {{ yesInput.click(); yesInput.checked = true; }}
            }}
            if (txt.includes('sponsorship') || txt.includes('require visa') || txt.includes('future require')) {{
                const noInput = el.closest('div, section, fieldset')?.querySelector('input[value="No"], input[value="no"]');
                if (noInput) {{ noInput.click(); noInput.checked = true; }}
            }}
        }});
        
        return true;
    }}"""

    page.evaluate(js_code)


def run():
    apps = parse_ashby_answers()
    print(f"Parsed {len(apps)} Ashby applications.")

    with sync_playwright() as p:
        print("Connecting to Chrome CDP session...")
        browser = p.chromium.connect_over_cdp(CDP_URL, timeout=15000)
        pages = browser.contexts[0].pages
        print(f"Connected! Total open browser pages: {len(pages)}")

        filled = 0
        for idx, page in enumerate(pages, 1):
            u = page.url.lower()
            if "ashbyhq.com" not in u:
                continue

            matched = None
            for a in apps:
                job_id = a["url"].split("ashbyhq.com/")[-1].split("/application")[0]
                if job_id in u:
                    matched = a
                    break
            if not matched:
                matched = {
                    "company": "Company",
                    "title": "Role",
                    "email": "shivamsin14@umich.edu",
                    "salary": "$120,000–$160,000 USD",
                    "essay": "IIT CS graduate & Ross MBA with 10+ years scaling core product platforms across AWS, D. E. Shaw, and Microsoft.",
                }

            print(f"\n[{idx}/{len(pages)}] Populating fields for: {page.url}")
            try:
                page.bring_to_front()
                time.sleep(0.3)
                fill_page_js(page, matched)
                filled += 1
            except Exception as ex:
                print(f"  Error on page {page.url}: {ex}")

        print(f"\n==========================================")
        print(f"Successfully populated form fields across {filled} open Ashby tabs!")
        print(f"==========================================")


if __name__ == "__main__":
    run()
