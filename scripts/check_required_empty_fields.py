import json
import time
import sys
import urllib.request
from websockets.sync.client import connect

sys.stdout.reconfigure(encoding='utf-8')
ENDPOINT = "http://localhost:9222"

def check_open_tabs_required_fields():
    req = urllib.request.Request(ENDPOINT + "/json/list")
    with urllib.request.urlopen(req) as resp:
        targets = json.load(resp)
        
    ashby_targets = [t for t in targets if "jobs.ashbyhq.com" in t.get("url", "")]
    print(f"Checking {len(ashby_targets)} open Ashby tabs for empty required fields...\n")
    
    report = []
    
    for t in ashby_targets:
        t_id = t.get("id")
        t_url = t.get("url", "")
        t_title = t.get("title", "")
        ws_url = t.get("webSocketDebuggerUrl")
        
        if not ws_url:
            continue
            
        try:
            act_req = urllib.request.Request(f"{ENDPOINT}/json/activate/{t_id}")
            with urllib.request.urlopen(act_req) as ar:
                ar.read()
        except Exception:
            pass
            
        time.sleep(0.3)
        
        try:
            ws = connect(ws_url, open_timeout=4, close_timeout=1)
            msg_id = 0
            
            def send_cdp(method, params=None):
                nonlocal msg_id
                msg_id += 1
                req_id = msg_id
                ws.send(json.dumps({"id": req_id, "method": method, "params": params or {}}))
                deadline = time.monotonic() + 4.0
                while time.monotonic() < deadline:
                    raw = ws.recv(timeout=max(0.1, deadline - time.monotonic()))
                    msg = json.loads(raw)
                    if msg.get("id") == req_id:
                        return msg.get("result", {})
                return {}

            send_cdp("Runtime.enable")
            
            check_script = """
            (() => {
                const emptyRequired = [];
                const containers = document.querySelectorAll(
                    '.ashby-application-form-field-entry, fieldset, [role="group"], div[class*="_formField_"], form > div'
                );
                
                for (const container of containers) {
                    const heading = container.querySelector(
                        '.ashby-application-form-question-title, label, legend, h3, p'
                    );
                    const label = (heading?.textContent || container.innerText?.split('\\n')[0] || '').trim();
                    const cleanLabel = label.replace(/\\*$/, '').trim();
                    
                    // Check explicitly marked asterisk or required attribute
                    const isRequired = label.includes('*') || 
                                       container.querySelector('[class*="asterisk"]') !== null ||
                                       container.querySelector('[required]') !== null;
                    
                    if (!isRequired || !cleanLabel) continue;
                    
                    // Check text / textarea inputs
                    const textControl = container.querySelector(
                        'input:not([type=file]):not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea'
                    );
                    if (textControl) {
                        if (!textControl.value || !textControl.value.trim()) {
                            emptyRequired.push({label: cleanLabel, type: textControl.tagName.toLowerCase()});
                        }
                        continue;
                    }
                    
                    // Check file inputs
                    const fileControl = container.querySelector('input[type=file]');
                    if (fileControl) {
                        const hasFile = fileControl.files && fileControl.files.length > 0;
                        const hasUploadedItem = container.querySelector('[class*="_file_"], [class*="_filename_"], [class*="_uploaded_"]') !== null;
                        if (!hasFile && !hasUploadedItem) {
                            emptyRequired.push({label: cleanLabel, type: 'file'});
                        }
                        continue;
                    }
                    
                    // Check radio / checkbox groups
                    const choices = container.querySelectorAll('input[type=radio], input[type=checkbox], [role="radio"], [role="checkbox"]');
                    if (choices.length > 0) {
                        const checked = Array.from(choices).some(c => c.checked || c.getAttribute('aria-checked') === 'true' || c.classList.contains('active'));
                        if (!checked) {
                            emptyRequired.push({label: cleanLabel, type: 'choice_group'});
                        }
                    }
                }
                
                // Deduplicate by label
                const unique = [];
                const seen = new Set();
                for (const item of emptyRequired) {
                    const key = item.label.toLowerCase();
                    if (!seen.has(key)) {
                        seen.add(key);
                        unique.push(item);
                    }
                }
                return unique;
            })()
            """
            
            eval_res = send_cdp("Runtime.evaluate", {"expression": check_script, "returnByValue": True, "awaitPromise": True})
            empty_fields = eval_res.get("result", {}).get("value", [])
            
            report.append({
                "title": t_title,
                "url": t_url,
                "empty_count": len(empty_fields),
                "empty_fields": empty_fields
            })
            
            ws.close()
        except Exception as e:
            print(f"Error checking {t_title}: {e}")

    print("=== REQUIRED FIELDS AUDIT REPORT ===")
    all_clean = True
    for item in report:
        title = item["title"]
        empty_count = item["empty_count"]
        if empty_count == 0:
            print(f"[COMPLETE] {title} -- All required fields filled!")
        else:
            all_clean = False
            print(f"[ATTENTION] {title} -- {empty_count} required empty field(s):")
            for f in item["empty_fields"]:
                print(f"   - {f['label']} [{f['type']}]")
    
    if all_clean:
        print("\nALL OPEN APPLICATIONS HAVE 100% OF THEIR REQUIRED FIELDS FILLED!")

if __name__ == "__main__":
    check_open_tabs_required_fields()
