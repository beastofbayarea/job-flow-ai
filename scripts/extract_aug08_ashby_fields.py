import json
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

QUEUE_PATH = Path("data/application-queues/ashby-job-search-2026-08-08.json")
OUT_PATH = Path("data/ashby_aug08_extracted_fields.json")

def application_url(url: str) -> str:
    url = url.rstrip("/")
    if not url.endswith("/application"):
        url += "/application"
    return url

def extract_fields_from_page(page):
    extracted = page.evaluate("""() => {
        const results = [];
        const labels = Array.from(document.querySelectorAll('label'));
        
        labels.forEach((label, idx) => {
            const labelText = label.innerText ? label.innerText.trim() : '';
            if (!labelText) return;
            
            const isRequired = labelText.includes('*') || label.querySelector('[class*="asterisk"]') !== null || label.parentElement.innerHTML.includes('*');
            const cleanLabel = labelText.replace(/\\*$/, '').trim();
            
            let targetId = label.getAttribute('for');
            let inputEl = targetId ? document.getElementById(targetId) : null;
            if (!inputEl) {
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
        
        const allTextareas = Array.from(document.querySelectorAll('textarea'));
        allTextareas.forEach(ta => {
            const taId = ta.id || ta.name;
            const alreadyCaptured = results.some(r => r.label.toLowerCase().includes(taId ? taId.toLowerCase() : '___never___'));
            if (!alreadyCaptured) {
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

def run():
    jobs = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        for idx, j in enumerate(jobs, 1):
            company = j.get("company")
            title = j.get("title")
            url = application_url(j.get("url"))
            
            print(f"[{idx}/{len(jobs)}] Fetching fields for {company} — {title}...")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_selector('input, textarea, select, label', timeout=10000)
                time.sleep(1.5)
                
                fields = extract_fields_from_page(page)
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": url,
                    "field_count": len(fields),
                    "fields": fields
                }
            except Exception as e:
                print(f"  Error on {company} ({url}): {e}")
                results[f"{idx}_{company}"] = {
                    "index": idx,
                    "company": company,
                    "title": title,
                    "url": url,
                    "error": str(e),
                    "fields": []
                }
                
        browser.close()
        
    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nExtraction finished! Saved to {OUT_PATH}")

if __name__ == "__main__":
    run()
