import json
import time
import sys
import urllib.request
from websockets.sync.client import connect

sys.stdout.reconfigure(encoding='utf-8')
ENDPOINT = "http://localhost:9222"

# Master tailored answers mapping for open tabs
ANSWERS_MAP = {
    "weave": {
        "Name": "Shivam Singh",
        "Email": "shiv-ai-pm@umich.edu",
        "Phone Number": "6502833478",
        "LinkedIn Profile:": "https://linkedin.com/in/beastofbayarea",
        "Preferred name": "Shiv",
        "Which messaging channels have you owned": "SMS, Push Notifications, In-App Messaging, Email, Chat",
        "How many active users were on the product": "Millions of daily active users",
        "Which product area best describes the primary product": "Messaging / Communications"
    },
    "openai": {
        "Legal Name": "Shivam Singh",
        "Preferred Name": "Shiv",
        "Email": "shiv-ai-pm@umich.edu",
        "Phone Number": "6502833478",
        "When can you start a new role?": "2 weeks",
        "Able to work from US office 3 days per week": "Yes"
    },
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
        "Preferred name (if applicable)": "Shiv",
        "Email": "shiv-ai-pm@umich.edu",
        "Links to your GitHub, portfolio, website, Linkedin, etc.": "https://github.com/beastofbayarea | https://linkedin.com/in/beastofbayarea",
        "How did you hear about this job?": "LinkedIn",
        "What interests you in Coder?": "As a CS graduate from IIT who built mission-critical developer platforms at D. E. Shaw (Rust, Flink, Kafka) and cloud developer tools at AWS and Microsoft, Coder’s vision for cloud development environments (CDEs) represents the future of developer speed and security."
    },
    "moonshot": {
        "Name": "Shivam Singh",
        "Email": "shiv-ai-pm@umich.edu",
        "Why Moonshot?": "Moonshot is pioneering next-generation global financial rails. Having managed capital efficiency, liquidity flywheels, and payment infrastructure at D. E. Shaw, Rakuten, and AWS, I am excited to apply data-driven lifecycle marketing and retention loops to accelerate user adoption for Moonshot.",
        "What is your experience working at a startup?": "6+ years of agile startup and high-growth scale-up experience. At Rakuten, I operated with lean startup autonomy to pivot portfolio strategy from DTC burn to B2B2C growth; at AWS and Microsoft, I led incubator 0-to-1 product pods operating like internal startups."
    }
}

def refill_open_tabs():
    req = urllib.request.Request(ENDPOINT + "/json/list")
    with urllib.request.urlopen(req) as resp:
        targets = json.load(resp)
        
    ashby_targets = [t for t in targets if "jobs.ashbyhq.com" in t.get("url", "")]
    print(f"Found {len(ashby_targets)} open Ashby tabs in Chrome debug.\n")
    
    for t in ashby_targets:
        t_id = t.get("id")
        t_url = t.get("url", "").lower()
        t_title = t.get("title", "")
        ws_url = t.get("webSocketDebuggerUrl")
        
        if not ws_url:
            continue
            
        print(f"Refilling open tab: {t_title} ({t_url})...")
        try:
            act_req = urllib.request.Request(f"{ENDPOINT}/json/activate/{t_id}")
            with urllib.request.urlopen(act_req) as ar:
                ar.read()
        except Exception:
            pass
            
        time.sleep(0.5)
        
        # Find matched company key
        matched_answers = {}
        for comp_key, ans in ANSWERS_MAP.items():
            if comp_key in t_url or comp_key in t_title.lower():
                matched_answers = ans
                break
                
        if not matched_answers:
            # General fallback profile
            matched_answers = {
                "Name": "Shivam Singh",
                "Full Name": "Shivam Singh",
                "Legal Name": "Shivam Singh",
                "Email": "shiv-ai-pm@umich.edu",
                "Phone": "6502833478",
                "LinkedIn": "https://linkedin.com/in/beastofbayarea",
                "GitHub": "https://github.com/beastofbayarea",
                "Location": "San Francisco, CA"
            }
            
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
            payload = json.dumps(matched_answers)
            
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
                    
                    // Fill text / textarea
                    const control = container.querySelector(
                        'input:not([type=file]):not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea'
                    );
                    if (control && !control.disabled && !control.readOnly) {
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
                        continue;
                    }
                    
                    // Fill checkboxes / radios for work auth
                    if (key.includes('work') || key.includes('authorized') || key.includes('sponsorship')) {
                        const radios = container.querySelectorAll('input[type=radio], input[type=checkbox]');
                        radios.forEach(r => {
                            const rLabel = (r.labels?.[0]?.textContent || r.parentElement?.textContent || '').toLowerCase();
                            if (key.includes('sponsorship')) {
                                if (rLabel.includes('no')) { r.click(); filled.push(label + ' (No)'); }
                            } else {
                                if (rLabel.includes('yes')) { r.click(); filled.push(label + ' (Yes)'); }
                            }
                        });
                    }
                }
                
                return filled;
            })(""" + payload + ")"
            
            eval_res = send_cdp("Runtime.evaluate", {"expression": fill_script, "returnByValue": True, "awaitPromise": True})
            filled_list = eval_res.get("result", {}).get("value", [])
            print(f"  -> Filled fields (skipped resume upload): {filled_list}")
            
            ws.close()
        except Exception as e:
            print(f"  Error on {t_title}: {e}")

if __name__ == "__main__":
    refill_open_tabs()
