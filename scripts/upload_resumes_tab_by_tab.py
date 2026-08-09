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


def parse_ashby_master_resumes():
    text = MD_PATH.read_text(encoding="utf-8")

    sections = re.split(r"(^## \d+\. .*$)", text, flags=re.MULTILINE)
    url_to_resume = {}

    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i + 1]

        m_url = re.search(r"\*+\s*URL\*+:\s*`([^`]+)`", body)
        m_res = re.search(r"Resume\*+:?\s*`([^`]+)`", body)

        if m_url and m_res:
            u_clean = m_url.group(1).strip().rstrip("/")
            if "ashbyhq.com" in u_clean and not u_clean.endswith("/application"):
                u_clean += "/application"
            res_path = m_res.group(1).strip()
            url_to_resume[u_clean.lower()] = res_path

    return url_to_resume


def get_open_tabs():
    req = urllib.request.urlopen(f"{CDP_URL}/json/list")
    data = json.loads(req.read().decode("utf-8"))
    return [t for t in data if t.get("type") == "page"]


def activate_tab(target_id):
    try:
        urllib.request.urlopen(f"{CDP_URL}/json/activate/{target_id}")
        time.sleep(0.3)
    except Exception as e:
        print(f"Error activating tab {target_id}: {e}")


def run():
    url_to_resume = parse_ashby_master_resumes()
    print(f"Loaded {len(url_to_resume)} resume mappings.")

    tabs = get_open_tabs()
    ashby_tabs = [t for t in tabs if "ashbyhq.com" in t.get("url", "").lower()]
    print(f"Found {len(ashby_tabs)} open Ashby tabs in Chrome debug.")

    uploaded_count = 0
    skipped_count = 0

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        page_map = {page.url.lower().rstrip("/"): page for page in browser.contexts[0].pages}

        for idx, tab in enumerate(ashby_tabs, 1):
            tab_id = tab.get("id")
            tab_url = tab.get("url", "").lower().rstrip("/")
            if not tab_url.endswith("/application"):
                tab_url += "/application"

            print(f"\n[{idx}/{len(ashby_tabs)}] Processing tab: {tab_url}")

            # Activate tab
            activate_tab(tab_id)

            matched_resume = None
            for target_url, res_path in url_to_resume.items():
                job_id = target_url.split("ashbyhq.com/")[-1].split("/application")[0]
                if job_id in tab_url:
                    matched_resume = res_path
                    break

            if not matched_resume:
                matched_resume = (
                    r"C:\Users\Nagarro\Downloads\job-flow-ai\data\resumes\resume-general.pdf"
                )

            resume_file = Path(matched_resume)
            if not resume_file.exists():
                resume_file = Path(
                    r"C:\Users\Nagarro\Downloads\job-flow-ai\data\resumes\resume-general.pdf"
                )

            print(f"  Matched Resume File: {resume_file.name}")

            # Find matching page in Playwright
            page = None
            for p_url, p_obj in page_map.items():
                if tab_id in p_url or (
                    len(p_url) > 10
                    and p_url.split("ashbyhq.com/")[-1].split("/application")[0] in tab_url
                ):
                    page = p_obj
                    break

            if not page and browser.contexts[0].pages:
                page = browser.contexts[0].pages[0]

            if not page:
                print(f"  WARNING: Page object not found for tab {tab_url}")
                skipped_count += 1
                continue

            try:
                page.bring_to_front()
                time.sleep(0.4)

                # Query all file inputs
                file_inputs = page.query_selector_all("input[type='file']")
                print(f"  Found {len(file_inputs)} file input(s).")

                target_inp = None
                for inp in file_inputs:
                    parent_text = inp.evaluate(
                        "el => el.closest('div, section, fieldset')?.innerText || ''"
                    ).lower()
                    inp_attr = inp.evaluate(
                        "el => (el.name + ' ' + el.id + ' ' + el.getAttribute('aria-label') + ' ' + el.getAttribute('data-qa') + ' ' + el.getAttribute('accept')).toLowerCase()"
                    )

                    if (
                        "autofill" in parent_text
                        or "autofill" in inp_attr
                        or "parse" in inp_attr
                        or "import" in parent_text
                    ):
                        print("    [Skip] Autofill resume input detected.")
                        continue

                    target_inp = inp
                    break

                if not target_inp and file_inputs:
                    target_inp = file_inputs[-1]

                if target_inp:
                    target_inp.set_input_files(str(resume_file))
                    print(f"  SUCCESS: Uploaded {resume_file.name} to tab!")
                    uploaded_count += 1
                else:
                    print(f"  WARNING: No explicit resume file input found.")
                    skipped_count += 1
            except Exception as ex:
                print(f"  ERROR on tab {tab_url}: {ex}")
                skipped_count += 1

    print(f"\nFinished uploading resumes!")
    print(f"Uploaded: {uploaded_count} tabs | Skipped/Failed: {skipped_count} tabs")


if __name__ == "__main__":
    run()
