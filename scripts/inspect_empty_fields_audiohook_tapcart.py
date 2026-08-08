import json
import time
import sys
import urllib.request
from websockets.sync.client import connect

sys.stdout.reconfigure(encoding='utf-8')
ENDPOINT = "http://localhost:9222"

def inspect_audiohook_tapcart():
    req = urllib.request.Request(ENDPOINT + "/json/list")
    with urllib.request.urlopen(req) as resp:
        targets = json.load(resp)
        
    target_urls = [
        "jobs.ashbyhq.com/audiohook/5d8e16bb-6bc9-4294-9762-37419ad319fa",
        "jobs.ashbyhq.com/tapcart/a0c241a5-d1b4-421d-98a2-685497984662"
    ]
    
    selected_targets = [t for t in targets if any(u in t.get("url", "").lower() for u in target_urls)]
    print(f"Inspecting {len(selected_targets)} target tabs...\n")
    
    for t in selected_targets:
        t_id = t.get("id")
        t_url = t.get("url", "")
        t_title = t.get("title", "")
        ws_url = t.get("webSocketDebuggerUrl")
        
        if not ws_url:
            continue
            
        print(f"=== [TAB] {t_title} ({t_url}) ===")
        try:
            act_req = urllib.request.Request(f"{ENDPOINT}/json/activate/{t_id}")
            with urllib.request.urlopen(act_req) as ar:
                ar.read()
        except Exception:
            pass
            
        time.sleep(0.5)
        
        try:
            ws = connect(ws_url, open_timeout=5, close_timeout=1)
            msg_id = 0
            
            def send_cdp(method, params=None):
                nonlocal msg_id
                msg_id += 1
                req_id = msg_id
                ws.send(json.dumps({"id": req_id, "method": method, "params": params or {}}))
                deadline = time.monotonic() + 5.0
                while time.monotonic() < deadline:
                    raw = ws.recv(timeout=max(0.1, deadline - time.monotonic()))
                    msg = json.loads(raw)
                    if msg.get("id") == req_id:
                        return msg.get("result", {})
                return {}

            send_cdp("Runtime.enable")
            
            extract_script = """
            (() => {
                const fields = [];
                const containers = document.querySelectorAll(
                    '.ashby-application-form-field-entry, fieldset, [role="group"], div[class*="_formField_"], form > div'
                );
                
                containers.forEach((container, idx) => {
                    const heading = container.querySelector(
                        '.ashby-application-form-question-title, label, legend, h3, p'
                    );
                    const label = (heading?.textContent || container.innerText?.split('\\n')[0] || '').trim();
                    const cleanLabel = label.replace(/\\*$/, '').trim();
                    if (!cleanLabel) return;
                    
                    const textEl = container.querySelector(
                        'input:not([type=file]):not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea'
                    );
                    let currentVal = textEl ? textEl.value : '';
                    
                    const isFile = container.querySelector('input[type=file]') !== null;
                    const hasRadioOrCheck = container.querySelectorAll('input[type=radio], input[type=checkbox]').length > 0;
                    
                    fields.push({
                        id: idx + 1,
                        label: cleanLabel,
                        currentVal: currentVal,
                        isEmpty: !currentVal || !currentVal.trim(),
                        isFile: isFile,
                        hasOptions: hasRadioOrCheck
                    });
                });
                
                return fields;
            })()
            """
            
            eval_res = send_cdp("Runtime.evaluate", {"expression": extract_script, "returnByValue": True, "awaitPromise": True})
            all_fields = eval_res.get("result", {}).get("value", [])
            
            for f in all_fields:
                status = "EMPTY ❌" if f["isEmpty"] and not f["isFile"] and not f["hasOptions"] else "FILLED ✅"
                val_str = f" => '{f['currentVal'][:40]}...'" if f['currentVal'] else ""
                print(f"   [{f['id']}] {f['label']} [{status}]{val_str}")
                
            ws.close()
        except Exception as e:
            print(f"Error inspecting {t_title}: {e}")
        print()

if __name__ == "__main__":
    inspect_audiohook_tapcart()
