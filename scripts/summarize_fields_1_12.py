import json

with open('data/ashby_21_extracted_fields.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for key, app in data.items():
    app_id = app.get("app_id")
    if app_id <= 12:
        company = app.get("company")
        role = app.get("role")
        print(f"=== [{app_id}/21] {company} — {role} ===")
        if 'error' in app:
            print("  ERROR:", app['error'])
        else:
            fields = app.get('fields', [])
            print(f"  Total fields: {len(fields)}")
            for field in fields:
                req = " *" if field.get('required') else ""
                opts = f" {field.get('options')}" if field.get('options') else ""
                desc = f" ({field.get('description')})" if field.get('description') else ""
                print(f"   - {field.get('label')}{req} [{field.get('type')}]{opts}{desc}")
        print()
