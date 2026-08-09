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


def activate_all_tabs():
    try:
        req = urllib.request.urlopen(f"{CDP_URL}/json/list")
        tabs = json.loads(req.read().decode("utf-8"))
        print(f"Activating {len(tabs)} open tabs via HTTP CDP endpoint...")
        for t in tabs:
            t_id = t.get("id")
            if t_id:
                try:
                    urllib.request.urlopen(f"{CDP_URL}/json/activate/{t_id}")
                    time.sleep(0.05)
                except Exception:
                    pass
        print("All tabs activated successfully!")
    except Exception as e:
        print(f"Error listing/activating tabs: {e}")


def run():
    url_to_resume = parse_ashby_master_resumes()
    print(f"Loaded {len(url_to_resume)} resume mappings from {MD_PATH.name}")

    activate_all_tabs()
    time.sleep(1)

    with sync_playwright() as p:
        print("Connecting to Chrome CDP session on port 9222...")
        browser = p.chromium.connect_over_cdp(CDP_URL, timeout=30000)

        context = browser.contexts[0]
        pages = context.pages
        print(f"Connected! Total open browser pages: {len(pages)}")

        uploaded_count = 0
        skipped_count = 0

        for idx, page in enumerate(pages, 1):
            page_url = page.url.lower().rstrip("/")
            if "ashbyhq.com" not in page_url:
                continue

            if not page_url.endswith("/application"):
                page_url += "/application"

            print(f"\n[{idx}/{len(pages)}] Processing Ashby Page: {page.url}")

            matched_resume = None
            for target_url, res_path in url_to_resume.items():
                job_id = target_url.split("ashbyhq.com/")[-1].split("/application")[0]
                if job_id in page_url:
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

            print(f"  Target Resume: {resume_file.name}")

            try:
                page.bring_to_front()
                time.sleep(0.3)

                file_inputs = page.query_selector_all("input[type='file']")
                print(f"  Found {len(file_inputs)} file input element(s).")

                target_input = None
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
                        print("    [Skip] Autofill resume file input detected.")
                        continue

                    target_input = inp
                    break

                if not target_input and file_inputs:
                    target_input = file_inputs[-1]

                if target_input:
                    target_input.set_input_files(str(resume_file))
                    print(f"  SUCCESS: Uploaded {resume_file.name} into explicit resume field!")
                    uploaded_count += 1
                else:
                    print(f"  WARNING: No explicit resume input found.")
                    skipped_count += 1
            except Exception as ex:
                print(f"  ERROR on page {page.url}: {ex}")
                skipped_count += 1

        print(f"\n==========================================")
        print(f"Resume Upload Summary:")
        print(f" - Successfully Uploaded: {uploaded_count} tabs")
        print(f" - Skipped/Warnings: {skipped_count} tabs")
        print(f"==========================================")


if __name__ == "__main__":
    run()
