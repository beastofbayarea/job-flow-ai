import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/ashby_aug08_extracted_fields.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for key, app in data.items():
    idx = app.get("index")
    company = app.get("company")
    title = app.get("title")
    url = app.get("url")
    fields = app.get("fields", [])
    print(f"=== [{idx}/24] {company} — {title} ===")
    print(f"URL: {url}")
    print(f"Total Fields: {len(fields)}")
    if "error" in app:
        print(f"  ERROR: {app['error']}")
    for f in fields:
        req = " *" if f.get("required") else ""
        desc = f" ({f.get('description')})" if f.get("description") else ""
        opts = f" Options: {f.get('options')}" if f.get("options") else ""
        print(f"   - {f.get('label')}{req} [{f.get('type')}]{opts}{desc}")
    print()
