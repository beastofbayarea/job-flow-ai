import json
import re
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

MD_PATH = Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\ashby_master_answers.md")
CDP_URL = "http://localhost:9222"


def parse_ashby_master_resumes():
    text = MD_PATH.read_text(encoding="utf-8")

    # Extract blocks: ## N. Company — Title ... URL ... Resume ...
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


def run():
    url_to_resume = parse_ashby_master_resumes()
    print(f"Loaded {len(url_to_resume)} resume mappings from {MD_PATH}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            print("Connected to Chrome Remote Debugging session at port 9222.")
        except Exception as e:
            print(f"Failed to connect to CDP: {e}")
            return

        contexts = browser.contexts
        if not contexts:
            print("No browser contexts found.")
            return

        page_list = contexts[0].pages
        print(f"Found {len(page_list)} open Chrome tabs.")

        uploaded_count = 0
        skipped_count = 0

        for page in page_list:
            u = page.url.lower().rstrip("/")
            if "ashbyhq.com" not in u:
                continue

            if not u.endswith("/application"):
                u += "/application"

            matched_resume = None
            for target_url, res_path in url_to_resume.items():
                # Match company/job ID in URL
                job_id = target_url.split("ashbyhq.com/")[-1].split("/application")[0]
                if job_id in u:
                    matched_resume = res_path
                    break

            if not matched_resume:
                # Fallback to general resume
                matched_resume = (
                    r"C:\Users\Nagarro\Downloads\job-flow-ai\data\resumes\resume-general.pdf"
                )

            resume_file = Path(matched_resume)
            if not resume_file.exists():
                # Fallback to general resume if custom file not found
                resume_file = Path(
                    r"C:\Users\Nagarro\Downloads\job-flow-ai\data\resumes\resume-general.pdf"
                )

            print(f"\nProcessing tab: {page.url}")
            print(f"  Target resume: {resume_file.name}")

            try:
                page.bring_to_front()
                time.sleep(0.5)

                # Find all file inputs on the page
                file_inputs = page.query_selector_all("input[type='file']")
                print(f"  Found {len(file_inputs)} file input element(s).")

                target_input = None
                for inp in file_inputs:
                    # Check parent/surrounding text or attributes to SKIP "autofill" inputs
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
                        print("    Skipping autofill resume file input...")
                        continue

                    # Choose the resume / document attachment input
                    target_input = inp
                    break

                if not target_input and file_inputs:
                    # If only 1 file input exists, use it if it's for resume
                    target_input = file_inputs[-1]

                if target_input:
                    target_input.set_input_files(str(resume_file))
                    print(f"  SUCCESS: Uploaded {resume_file.name} to tab {page.url}")
                    uploaded_count += 1
                else:
                    print(f"  WARNING: Could not find explicit resume file input in tab {page.url}")
                    skipped_count += 1
            except Exception as ex:
                print(f"  ERROR processing tab {page.url}: {ex}")
                skipped_count += 1

        print(f"\nCompleted resume upload run!")
        print(f"Uploaded: {uploaded_count} tabs | Skipped/Errors: {skipped_count} tabs")


if __name__ == "__main__":
    run()
