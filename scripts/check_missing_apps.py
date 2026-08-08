import json
from playwright.sync_api import sync_playwright

apps = [
    {"id": 1, "company": "Kraken", "role": "Deal Lead, Corporate Development", "url": "https://jobs.ashbyhq.com/kraken.com/37abda0c-ef4d-4bbe-9fb4-e6cb64c1acbe/application"},
    {"id": 2, "company": "Coder", "role": "Senior Product Manager", "url": "https://jobs.ashbyhq.com/Coder/0dade34e-3141-4c69-bef8-7ebfdc72bf72/application"},
    {"id": 3, "company": "OpenAI", "role": "Product Manager, Codex Security Controls & Partner Interfaces", "url": "https://jobs.ashbyhq.com/OpenAI/97681dd5-65ad-4eb5-b692-e6d192871c38/application"},
    {"id": 4, "company": "Infisical", "role": "Growth Marketing Manager", "url": "https://jobs.ashbyhq.com/infisical/96f136de-3cab-4e38-942e-0f079f4b0e02/application"},
    {"id": 8, "company": "HavocAI", "role": "Technical Program Manager", "url": "https://jobs.ashbyhq.com/havocai/d159a734-8200-8bfb-6df43f498e6f/application"},
]

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from extract_all_ashby_fields import extract_fields_from_page

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    for app in apps:
        print(f"=== [{app['id']}] {app['company']} — {app['role']} ===")
        try:
            page.goto(app['url'], wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(3000)
            fields = extract_fields_from_page(page)
            print(f"  Fields count: {len(fields)}")
            for f in fields:
                req = " *" if f.get('required') else ""
                print(f"   - {f.get('label')}{req} [{f.get('type')}]")
        except Exception as e:
            print("  ERROR:", e)
    browser.close()
