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

        # Extract fields
        email_match = re.search(r"Email\*+:?\s*([^\n]+)", body)
        email = email_match.group(1).strip(" `") if email_match else "shivamsin14@umich.edu"

        salary_match = re.search(r"Salary\*+:?\s*([^\n]+)", body)
        salary = salary_match.group(1).strip(" `") if salary_match else "$120,000–$160,000 USD"

        essay_match = re.search(r">\s*(.*)", body)
        essay = (
            essay_match.group(1).strip()
            if essay_match
            else (
                "IIT CS graduate & Ross MBA with 10+ years experience spanning AWS, D. E. Shaw, and Microsoft. "
                "I combine technical architecture with commercial strategy to drive high-leverage execution."
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
                "full_body": body,
            }
        )

    return apps_data


def fill_ashby_page_fields(page, app_info):
    print(f"  Populating fields for: {app_info['company']} — {app_info['title']}")
    print(f"  Assigned Email: {app_info['email']}")

    # Standard text mappings
    text_answers = {
        "name": "Shivam Singh",
        "first name": "Shivam",
        "last name": "Singh",
        "preferred name": "Shiv",
        "email": app_info["email"],
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
        "salary": app_info["salary"],
        "compensation": app_info["salary"],
    }

    # 1. Fill standard text inputs
    inputs = page.query_selector_all(
        "input[type='text'], input[type='email'], input[type='tel'], input:not([type])"
    )
    for inp in inputs:
        try:
            if not inp.is_visible():
                continue
            name_attr = (inp.get_attribute("name") or "").lower()
            id_attr = (inp.get_attribute("id") or "").lower()
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            aria_label = (inp.get_attribute("aria-label") or "").lower()

            # Parent label text
            label_text = inp.evaluate(
                "el => el.closest('label, div, section')?.innerText || ''"
            ).lower()
            combined = f"{name_attr} {id_attr} {placeholder} {aria_label} {label_text}"

            filled = False
            for key, val in text_answers.items():
                if key in combined:
                    inp.fill(val)
                    filled = True
                    break

            if not filled:
                if "name" in combined and "company" not in combined:
                    inp.fill("Shivam Singh")
                elif "email" in combined:
                    inp.fill(app_info["email"])
                elif "phone" in combined:
                    inp.fill("+1-650-283-3478")
                elif "linkedin" in combined:
                    inp.fill("https://linkedin.com/in/beastofbayarea")
                elif "github" in combined:
                    inp.fill("https://github.com/beastofbayarea")
        except Exception:
            pass

    # 2. Fill textareas (essay responses)
    textareas = page.query_selector_all("textarea")
    for ta in textareas:
        try:
            if not ta.is_visible():
                continue
            ta_label = ta.evaluate(
                "el => el.closest('label, div, section')?.innerText || ''"
            ).lower()
            if (
                "why" in ta_label
                or "interest" in ta_label
                or "fit" in ta_label
                or "about" in ta_label
                or "tell" in ta_label
                or "experience" in ta_label
                or "additional" in ta_label
            ):
                ta.fill(app_info["essay"])
            else:
                ta.fill(app_info["essay"])
        except Exception:
            pass

    # 3. Work Auth & Visa Sponsorship Selects/Radios
    # Work Auth -> Yes
    # Visa Sponsorship -> No
    page.evaluate("""() => {
        const labels = Array.from(document.querySelectorAll('label, div, p, span'));
        labels.forEach(el => {
            const txt = el.innerText ? el.innerText.toLowerCase() : '';
            if (txt.includes('authorized') || txt.includes('work in the us') || txt.includes('legally authorized')) {
                const yesOpt = el.closest('div, section')?.querySelector('input[value="Yes"], input[value="yes"], option[value="Yes"]');
                if (yesOpt) {
                    if (yesOpt.tagName === 'INPUT') yesOpt.click();
                    else if (yesOpt.tagName === 'OPTION') yesOpt.selected = true;
                }
            }
            if (txt.includes('sponsorship') || txt.includes('require visa') || txt.includes('future require')) {
                const noOpt = el.closest('div, section')?.querySelector('input[value="No"], input[value="no"], option[value="No"]');
                if (noOpt) {
                    if (noOpt.tagName === 'INPUT') noOpt.click();
                    else if (noOpt.tagName === 'OPTION') noOpt.selected = true;
                }
            }
        });
    }""")


def run():
    apps_data = parse_ashby_answers()
    print(f"Parsed {len(apps_data)} Ashby application answers from master guide.")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            print("Connected to Chrome debug browser on port 9222.")
        except Exception as e:
            print(f"Failed to connect to CDP: {e}")
            return

        pages = browser.contexts[0].pages
        print(f"Total open tabs in Chrome: {len(pages)}")

        filled_count = 0
        for idx, page in enumerate(pages, 1):
            url = page.url.lower()
            if "ashbyhq.com" not in url:
                continue

            matched_app = None
            for app in apps_data:
                job_id = app["url"].split("ashbyhq.com/")[-1].split("/application")[0]
                if job_id in url:
                    matched_app = app
                    break

            if not matched_app:
                matched_app = {
                    "company": "Company",
                    "title": "Role",
                    "email": "shivamsin14@umich.edu",
                    "salary": "$120,000–$160,000 USD",
                    "essay": "IIT CS graduate & Ross MBA with 10+ years scaling core product platforms across AWS, D. E. Shaw, and Microsoft.",
                }

            try:
                page.bring_to_front()
                time.sleep(0.5)
                fill_ashby_page_fields(page, matched_app)
                filled_count += 1
            except Exception as ex:
                print(f"  Error populating fields for {url}: {ex}")

        print(f"\n==========================================")
        print(f"Form Population Summary:")
        print(f" - Successfully Populated: {filled_count} open Ashby tabs")
        print(f"==========================================")


if __name__ == "__main__":
    run()
