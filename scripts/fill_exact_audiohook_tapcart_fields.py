import json
import time
import sys
import urllib.request
from websockets.sync.client import connect

sys.stdout.reconfigure(encoding='utf-8')
ENDPOINT = "http://localhost:9222"

TAPCART_ANSWERS = {
    "In 3-5 sentences, walk us through a demand gen program": "At Microsoft, I architected a $12M partner marketing and demand generation engine that shifted allocation from static co-marketing grants to real-time, propensity-scored budget shaping using Random Forest models. The channel mix spanned paid search, programmatic display, and partner co-sell programs, generating $50M in incremental GMV at a 4.1x ROI, boosting partner conversion from 5% to 24%, and compressing sales cycles to 85 days. In hindsight, I would have integrated automated CRM intent triggers earlier to accelerate partner lead routing even further.",
    "Describe a workflow or system you've built using AI tools": "Challenge: High hallucination rates (8%+) and slow session depth in conversational shopping assistants across 12 workstreams at AWS.\nSystem Built: I fine-tuned prompt chains on Amazon Bedrock, integrated retrieval-augmented generation (RAG) over catalog embeddings, deployed Bedrock Guardrails for safety mitigation, and automated synthetic evaluation loops.\nHow it Worked & Outcome: The system dynamically routed customer queries to specialized prompt sub-agents while filtering toxic/out-of-domain queries, reducing model hallucinations to 2.8%, increasing adoption by 25%, and expanding session depth by +15%."
}

AUDIOHOOK_ANSWERS = {
    "improved customer activation or time-to-value": "At AWS, enterprise banking clients faced 6-month onboardings due to complex compliance reviews. I identified activation bottlenecks through funnel telemetry and shipped pre-packaged compliance-as-code reference architectures and localized security toolkits. This reduced client onboarding time from 6 months to 2 hours, unlocked $20M+ immediate commitments, and built a $122M pipeline.",
    "positioning or messaging shift": "At Rakuten, our consumer app positioning focused on DTC discount shoppers, leading to high CAC ($42) and poor D30 retention (34%). Through cohort analytics and customer interviews, I led a repositioning shift from consumer DTC rewards to B2B2C corporate employee perks. I validated the direction through pilot sales decks and joint beta testing with enterprise partners, improving LTV:CAC from 0.8 to 4.5, boosting D30 retention from 34% to 67%, and dropping CAC to $8.50.",
    "product launch you owned end-to-end": "I owned the end-to-end launch of our GenAI shopping assistant copilot at AWS across 12 workstreams. In hindsight, the decision I am least proud of was launching with a broad multi-category prompt template rather than segmenting prompts by product vertical on day 1. This caused initial domain hallucinations in specialized categories. We quickly pivoted by deploying vertical-specific RAG embeddings and Bedrock Guardrails, which reduced hallucinations from 8% to 2.8%.",
    "customer or win/loss research changed your mind": "During win/loss research for our cloud developer platform at Microsoft, we assumed enterprise buyers prioritized advanced feature breadth over setup speed. Customer interviews revealed that dev leads were churning during initial proof-of-concept because environment configuration took over 3 days. Hearing this feedback firsthand, I re-prioritized 1-click cloud development environment templates on our roadmap, reducing dev setup to under 15 minutes and increasing trial conversion by 38%.",
    "How do you use AI tools in your product marketing work today": "I use GenAI tools daily for market positioning research, drafting messaging variants, and automating competitive intelligence. In one instance, using Claude/Bedrock prompt chains to analyze 500+ customer feedback transcripts helped us isolate key value propositions in hours, accelerating our messaging framework launch. Conversely, when attempting to use AI to generate complete customer case study narratives, the output lacked authentic customer nuance and required a complete manual rewrite to restore human credibility.",
    "desired salary": "$120,000–$160,000 USD"
}

def fill_remaining():
    req = urllib.request.Request(ENDPOINT + "/json/list")
    with urllib.request.urlopen(req) as resp:
        targets = json.load(resp)
        
    for t in targets:
        url = t.get("url", "").lower()
        title = t.get("title", "")
        t_id = t.get("id")
        ws_url = t.get("webSocketDebuggerUrl")
        
        if not ws_url:
            continue
            
        answers_to_use = None
        if "tapcart" in url or "tapcart" in title.lower():
            answers_to_use = TAPCART_ANSWERS
        elif "audiohook" in url or "audiohook" in title.lower():
            answers_to_use = AUDIOHOOK_ANSWERS
            
        if not answers_to_use:
            continue
            
        print(f"Targeting: {title}...")
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
            payload = json.dumps(answers_to_use)
            
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
                        if (key.includes(ansKey) || ansKey.includes(key)) {
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
            print(f"[{title}] Filled remaining fields: {eval_res.get('result', {}).get('value')}")
            ws.close()
        except Exception as e:
            print(f"Error filling {title}: {e}")

if __name__ == "__main__":
    fill_remaining()
