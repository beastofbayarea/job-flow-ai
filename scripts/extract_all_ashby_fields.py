import json
import time
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

APPLICATIONS = [
    {"id": 1, "company": "Kraken", "role": "Deal Lead, Corporate Development", "url": "https://jobs.ashbyhq.com/kraken.com/37abda0c-ef4d-4bbe-9fb4-e6cb64c1acbe/application"},
    {"id": 2, "company": "Coder", "role": "Senior Product Manager", "url": "https://jobs.ashbyhq.com/Coder/0dade34e-3141-4c69-bef8-7ebfdc72bf72/application"},
    {"id": 3, "company": "OpenAI", "role": "Product Manager, Codex Security Controls & Partner Interfaces", "url": "https://jobs.ashbyhq.com/OpenAI/97681dd5-65ad-4eb5-b692-e6d192871c38/application"},
    {"id": 4, "company": "Infisical", "role": "Growth Marketing Manager", "url": "https://jobs.ashbyhq.com/infisical/96f136de-3cab-4e38-942e-0f079f4b0e02/application"},
    {"id": 5, "company": "Weave", "role": "Senior Product Manager, Messaging", "url": "https://jobs.ashbyhq.com/Weave/a0e04228-7490-4716-9a92-f637e2110f7c/application"},
    {"id": 6, "company": "Qualified Health", "role": "Product Strategy & Operations Lead", "url": "https://jobs.ashbyhq.com/qualified-health-pbc/67e8e929-9506-423c-9462-28b766b18683/application"},
    {"id": 7, "company": "Planera", "role": "Sr Product Marketing Manager", "url": "https://jobs.ashbyhq.com/planera/5e4c93db-3d84-4cf8-a914-8574499927e8/application"},
    {"id": 8, "company": "HavocAI", "role": "Technical Program Manager", "url": "https://jobs.ashbyhq.com/havocai/d159a734-8200-8bfb-6df43f498e6f/application"},
    {"id": 9, "company": "GoodParty.org", "role": "Staff Product Manager", "url": "https://jobs.ashbyhq.com/goodparty/e3a16838-9b9b-4318-893a-898b062f4c38/application"},
    {"id": 10, "company": "Common Room", "role": "Integrations Product Manager", "url": "https://jobs.ashbyhq.com/commonroom/ff0cfae6-aeec-4fe1-8185-58ef7e1d8d7c/application"},
    {"id": 11, "company": "Audiohook", "role": "Product Marketing Manager", "url": "https://jobs.ashbyhq.com/audiohook/5d8e16bb-6bc9-4294-9762-37419ad319fa/application"},
    {"id": 12, "company": "Moonshot", "role": "Lifecycle Marketing Manager", "url": "https://jobs.ashbyhq.com/moonshot/37de5c6f-f600-49c9-a6f2-8ea03fd32955/application"},
    {"id": 13, "company": "Linear", "role": "Product Marketing Manager", "url": "https://jobs.ashbyhq.com/Linear/b3346acf-44be-4565-b1c0-10d482d3ad4e/application"},
    {"id": 14, "company": "Confluent", "role": "Principal Product Manager", "url": "https://jobs.ashbyhq.com/Confluent/f7356433-e9cd-437b-9048-587b11333bb1/application"},
    {"id": 15, "company": "Yendo", "role": "Principal Product Manager", "url": "https://jobs.ashbyhq.com/yendo/44f1a080-2a6b-4843-aee4-dc30eb44b857/application"},
    {"id": 16, "company": "Runway", "role": "Product Lead, Self Serve", "url": "https://jobs.ashbyhq.com/runway-ml/a010aa47-9150-4602-af69-f89f95186460/application"},
    {"id": 17, "company": "Hims & Hers", "role": "Lead Product Manager, Consumer Apps", "url": "https://jobs.ashbyhq.com/hims-and-hers/e809a108-e72b-45c1-b2c4-aad645a00772/application"},
    {"id": 18, "company": "Kestra", "role": "Product Manager, AI", "url": "https://jobs.ashbyhq.com/kestra/51b67438-6b1a-494a-acea-b3f25bc62070/application"},
    {"id": 19, "company": "Tapcart", "role": "Demand Gen Director", "url": "https://jobs.ashbyhq.com/tapcart/a0c241a5-d1b4-421d-98a2-685497984662/application"},
    {"id": 20, "company": "Airwallex", "role": "Staff Product Manager, Lending", "url": "https://jobs.ashbyhq.com/Airwallex/162fc14c-66ef-4eb6-8894-b1030f567ce5/application"},
    {"id": 21, "company": "Virtuous", "role": "Product Operations Manager", "url": "https://jobs.ashbyhq.com/virtuous/08d80945-0a86-4078-8c38-18c3df00055b/application"}
]

def extract_fields_from_page(page):
    # Ashby structure: fields are grouped inside form containers, labels, inputs, selects, textareas
    fields = []
    
    # Execute JS on page to extract structured form fields
    extracted = page.evaluate("""() => {
        const results = [];
        // Find form entries or field containers
        const containers = document.querySelectorAll('form fieldset, form > div, div._container_1, .ashby-application-form-field-entry, [class*="_formField_"], [class*="_field_"]');
        
        // Alternative: gather all label elements and their associated inputs
        const labels = Array.from(document.querySelectorAll('label'));
        
        labels.forEach((label, idx) => {
            const labelText = label.innerText ? label.innerText.trim() : '';
            if (!labelText) return;
            
            // Check if required
            const isRequired = labelText.includes('*') || label.querySelector('[class*="asterisk"]') !== null || label.parentElement.innerHTML.includes('*');
            const cleanLabel = labelText.replace(/\\*$/, '').trim();
            
            // Find input/textarea/select associated
            let targetId = label.getAttribute('for');
            let inputEl = targetId ? document.getElementById(targetId) : null;
            if (!inputEl) {
                // look inside label or next sibling
                inputEl = label.querySelector('input, textarea, select, [role="aria-autocomplete"], [role="combobox"]') || 
                          label.parentElement.querySelector('input, textarea, select, [role="combobox"], [role="listbox"]');
            }
            
            let fieldType = 'text';
            let options = [];
            
            if (inputEl) {
                const tagName = inputEl.tagName.toLowerCase();
                const inputType = inputEl.getAttribute('type') || '';
                if (tagName === 'textarea') {
                    fieldType = 'textarea';
                } else if (tagName === 'select') {
                    fieldType = 'select';
                    options = Array.from(inputEl.options).map(o => o.text.trim()).filter(Boolean);
                } else if (inputType === 'file') {
                    fieldType = 'file';
                } else if (inputType === 'checkbox' || inputType === 'radio') {
                    fieldType = inputType;
                } else if (inputEl.getAttribute('role') === 'combobox' || inputEl.getAttribute('aria-haspopup') === 'listbox') {
                    fieldType = 'custom-select';
                } else {
                    fieldType = inputType || 'text';
                }
            }
            
            // Look for help text / description nearby
            let description = '';
            const descEl = label.parentElement.querySelector('[class*="_description_"], [class*="_help_"], small, p');
            if (descEl && descEl !== label) {
                description = descEl.innerText.trim();
            }
            
            results.push({
                id: idx + 1,
                label: cleanLabel,
                required: isRequired,
                type: fieldType,
                options: options,
                description: description
            });
        });
        
        // Also capture any standalone textareas or inputs that didn't match a label
        const allTextareas = Array.from(document.querySelectorAll('textarea'));
        allTextareas.forEach(ta => {
            const taId = ta.id || ta.name;
            const alreadyCaptured = results.some(r => r.label.toLowerCase().includes(taId ? taId.toLowerCase() : '___never___'));
            if (!alreadyCaptured) {
                // find parent header or prompt text
                let prompt = '';
                let p = ta.parentElement;
                for (let i = 0; i < 4 && p; i++) {
                    const txt = p.innerText.split('\\n')[0];
                    if (txt && txt.length > 5 && txt.length < 300) {
                        prompt = txt;
                        break;
                    }
                    p = p.parentElement;
                }
                if (prompt) {
                    results.push({
                        id: results.length + 1,
                        label: prompt.replace(/\\*$/, '').trim(),
                        required: prompt.includes('*'),
                        type: 'textarea',
                        options: [],
                        description: ''
                    });
                }
            }
        });
        
        // Deduplicate results by label text
        const unique = [];
        const seen = new Set();
        results.forEach(r => {
            const key = r.label.toLowerCase().replace(/[^a-z0-9]/g, '');
            if (key && !seen.has(key)) {
                seen.add(key);
                unique.push(r);
            }
        });
        
        return unique;
    }""")
    return extracted

def run_extraction():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        for app in APPLICATIONS:
            app_id = app["id"]
            company = app["company"]
            role = app["role"]
            url = app["url"]
            print(f"[{app_id}/21] Extracting fields for {company} - {role}...")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_selector('input, textarea, select, label', timeout=10000)
                time.sleep(2) # Give React time to complete render
                
                # Fetch text content of page title or job title header to confirm load
                title_header = page.locator('h1, h2, [class*="_title_"]').first.text_content() if page.locator('h1, h2, [class*="_title_"]').count() > 0 else ""
                
                fields = extract_fields_from_page(page)
                
                # Check for custom select options by clicking dropdowns if options are empty
                results[f"{app_id}_{company}"] = {
                    "app_id": app_id,
                    "company": company,
                    "role": role,
                    "url": url,
                    "page_header": title_header.strip() if title_header else "",
                    "field_count": len(fields),
                    "fields": fields
                }
            except Exception as e:
                print(f"Error on {company} ({url}): {e}")
                results[f"{app_id}_{company}"] = {
                    "app_id": app_id,
                    "company": company,
                    "role": role,
                    "url": url,
                    "error": str(e),
                    "fields": []
                }
                
        browser.close()
        
    out_path = Path("data/ashby_21_extracted_fields.json")
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Extraction complete! Saved to {out_path}")

if __name__ == "__main__":
    run_extraction()
