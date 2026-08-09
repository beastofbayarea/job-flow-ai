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


def fill_page(page, app):
    print(f"  Filling form for: {app['company']} — {app['title']} ({app['email']})")
    page.bring_to_front()
    time.sleep(0.5)

    # Text field mappings
    mappings = {
        "name": "Shivam Singh",
        "first name": "Shivam",
        "last name": "Singh",
        "preferred name": "Shiv",
        "email": app["email"],
        "phone": "+1-650-283-3478",
        "location": "San Francisco, California, United States",
        "current company": "Amazon Web Services (AWS)",
        "current title": "Principal, AI Products & Platforms",
        "linkedin": "https://linkedin.com/in/beastofbayarea",
        "github": "https://github.com/beastofbayarea",
        "portfolio": "https://www.researchgate.net/profile/Shivam-Singh-188",
        "notice": "2 weeks",
        "salary": app["salary"],
        "compensation": app["salary"],
    }

    inputs = page.query_selector_all(
        "input[type='text'], input[type='email'], input[type='tel'], input:not([type])"
    )
    for inp in inputs:
        try:
            if not inp.is_visible():
                continue
            lbl = inp.evaluate("el => el.closest('label, div, section')?.innerText || ''").lower()
            name_attr = (inp.get_attribute("name") or "").lower()
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            comb = f"{lbl} {name_attr} {placeholder}"

            filled = False
            for k, v in mappings.items():
                if k in comb:
                    inp.fill(v)
                    filled = True
                    break
            if not filled:
                if "email" in comb:
                    inp.fill(app["email"])
                elif "phone" in comb:
                    inp.fill("+1-650-283-3478")
                elif "linkedin" in comb:
                    inp.fill("https://linkedin.com/in/beastofbayarea")
                elif "github" in comb:
                    inp.fill("https://github.com/beastofbayarea")
                elif "name" in comb and "company" not in comb:
                    inp.fill("Shivam Singh")
        except Exception:
            pass

    # Textareas
    for ta in page.query_selector_all("textarea"):
        try:
            if ta.is_visible():
                ta.fill(app["essay"])
        except Exception:
            pass


def run():
    apps = parse_ashby_answers()
    print(f"Parsed {len(apps)} Ashby applications.")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL, timeout=60000)
        pages = browser.contexts[0].pages
        print(f"Total open Chrome pages: {len(pages)}")

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

            print(f"\n[{idx}/{len(pages)}] Form Filling Page: {page.url}")
            try:
                fill_page(page, matched)
                filled += 1
            except Exception as ex:
                print(f"  Error populating {page.url}: {ex}")

        print(f"\nSuccessfully populated form fields across {filled} open Ashby tabs!")


if __name__ == "__main__":
    run()
