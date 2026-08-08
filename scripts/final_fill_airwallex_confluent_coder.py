import json
import time
import sys
import urllib.request
from websockets.sync.client import connect

sys.stdout.reconfigure(encoding='utf-8')
ENDPOINT = "http://localhost:9222"

TARGET_MAP = {
    "airwallex": {
        "First Name": "Shivam",
        "Last Name / Surname": "Singh",
        "Email": "shiv-ai-pm@umich.edu",
        "Phone": "6502833478",
        "Salary Expectations": "$120,000–$160,000 USD",
        "What is your notice period?": "2 weeks",
        "Where did you find this job posting?": "LinkedIn",
        "Please share the GPA you graduated your Bachelors Degree with.": "3.8 equivalent (First Class Honors, B.Tech CSE at IIT)"
    },
    "confluent": {
        "Preferred FULL Name": "Shivam Singh",
        "Legal FULL Name": "Shivam Singh",
        "Email": "shiv-ai-pm@umich.edu",
        "Mobile Phone": "6502833478",
        "Location - Zip Code": "94108",
        "Current Company": "Amazon Web Services",
        "LinkedIn Profile URL": "https://linkedin.com/in/beastofbayarea",
        "GitHub Profile URL": "https://github.com/beastofbayarea",
        "Portfolio URL": "https://www.researchgate.net/profile/Shivam-Singh-188"
    },
    "coder": {
        "Name": "Shivam Singh",
        "Email": "shiv-ai-pm@umich.edu",
        "Links to your GitHub, portfolio, website, Linkedin, etc.": "https://github.com/beastofbayarea | https://linkedin.com/in/beastofbayarea",
        "How did you hear about this job?": "LinkedIn",
        "What interests you in Coder?": "As a CS graduate from IIT who built mission-critical low-latency developer platforms at D. E. Shaw (Rust, Flink, Kafka) and cloud developer tools at AWS and Microsoft, Coder’s vision for cloud development environments (CDEs) represents the future of developer speed and security. I want to bring my background scaling developer-facing infrastructure to expand Coder’s product footprint for global engineering teams."
    }
}

def sweep():
    req = urllib.request.Request(ENDPOINT + "/json/list")
    with urllib.request.urlopen(req) as resp:
        targets = json.load(resp)
        
    for t in targets:
        url = t.get("url", "").lower()
        title = t.get("title", "")
        t_id = t.get("id")
        ws_url = t.get("webSocketDebuggerUrl")
        
        matched_key = None
        for k in TARGET_MAP:
            if k in url or k in title.lower():
                matched_key = k
                break
                
        if not matched_key or not ws_url:
            continue
            
        print(f"Targeting: {title}...")
        try:
            act_req = urllib.request.Request(f"{ENDPOINT}/json/activate/{t_id}")
            with urllib.request.urlopen(act_req) as ar:
                ar.read()
        except Exception:
            pass
            
        time.sleep(1.0)
        
        try:
            ws = connect(ws_url, open_timeout=8, close_timeout=1)
            msg_id = 0
            
            def send_cdp(method, params=None):
                nonlocal msg_id
                msg_id += 1
                req_id = msg_id
                ws.send(json.dumps({"id": req_id, "method": method, "params": params or {}}))
                deadline = time.monotonic() + 8.0
                while time.monotonic() < deadline:
                    raw = ws.recv(timeout=max(0.1, deadline - time.monotonic()))
                    msg = json.loads(raw)
                    if msg.get("id") == req_id:
                        return msg.get("result", {})
                return {}

            send_cdp("Runtime.enable")
            payload = json.dumps(TARGET_MAP[matched_key])
            
            fill_script = """
            ((payload) => {
                const normalize = val => (val || '').replace(/\\s+/g, ' ').trim().toLowerCase();
                const setValue = (el, val) => {
                    const desc = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), 'value');
                    if (desc && desc.set) desc.set.call(el, val);
                    else el.value = val;
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                };
                
                const answers = new Map(Object.entries(payload).map(([k, v]) => [normalize(k), v]));
                const filled = [];
                
                for (const container of document.querySelectorAll(
                    '.ashby-application-form-field-entry, fieldset, [role="group"], div[class*="_formField_"], form > div'
                )) {
                    const heading = container.querySelector(
                        '.ashby-application-form-question-title, label, legend, h3, p'
                    );
                    const label = (heading?.textContent || container.innerText?.split('\\n')[0] || '').trim();
                    const key = normalize(label);
                    
                    const control = container.querySelector(
                        'input:not([type=file]):not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea'
                    );
                    if (!control || control.disabled || control.readOnly) continue;
                    
                    let matchedVal = null;
                    for (const [ansKey, ansVal] of answers.entries()) {
                        if (key === ansKey || key.includes(ansKey) || ansKey.includes(key)) {
                            matchedVal = ansVal;
                            break;
                        }
                    }
                    
                    if (matchedVal && (!control.value || !control.value.trim())) {
                        setValue(control, matchedVal);
                        filled.push(label);
                    }
                }
                
                return filled;
            })(""" + payload + ")"
            
            eval_res = send_cdp("Runtime.evaluate", {"expression": fill_script, "returnByValue": True, "awaitPromise": True})
            print(f"[{title}] Filled: {eval_res.get('result', {}).get('value')}")
            ws.close()
        except Exception as e:
            print(f"Error on {title}: {e}")

if __name__ == "__main__":
    sweep()
