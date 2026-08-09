import asyncio
import json
import re
import sys
import urllib.request
from pathlib import Path
import websockets

sys.stdout.reconfigure(encoding="utf-8")

MD_PATH = Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\ashby_master_answers.md")
CDP_URL = "http://localhost:9222"


def parse_ashby_answers():
    text = MD_PATH.read_text(encoding="utf-8")
    sections = re.split(r"(^## \d+\. .*$)", text, flags=re.MULTILINE)
    apps_data = []
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i + 1]
        m_comp = re.search(r"## \d+\.\s*(.*?)\s*—\s*(.*?)$", header.strip())
        company = m_comp.group(1).strip() if m_comp else "Company"
        title = m_comp.group(2).strip() if m_comp else "Role"
        m_url = re.search(r"\*+\s*URL\*+:\s*`([^`]+)`", body)
        url = m_url.group(1).strip() if m_url else ""

        email_match = re.search(r"Email\*+:?\s*([^\n]+)", body)
        email = email_match.group(1).strip(" `") if email_match else "shivamsin14@umich.edu"

        salary_match = re.search(r"Salary\*+:?\s*([^\n]+)", body)
        salary = salary_match.group(1).strip(" `") if salary_match else "$120,000–$160,000 USD"

        essay_match = re.search(r">\s*(.*)", body)
        essay = (
            essay_match.group(1).strip()
            if essay_match
            else (
                "IIT CS graduate & Ross MBA with 10+ years experience spanning AWS, D. E. Shaw, and Microsoft."
            )
        )

        apps_data.append(
            {
                "company": company,
                "title": title,
                "url": url,
                "email": email,
                "salary": salary,
                "essay": essay,
            }
        )
    return apps_data


def build_js_fill_script(app):
    return f"""(() => {{
        const app = {json.dumps(app)};
        
        function setVal(el, v) {{
            if (!el) return;
            el.focus();
            el.value = v;
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
        }}
        
        const map = {{
            "name": "Shivam Singh",
            "first name": "Shivam",
            "last name": "Singh",
            "preferred name": "Shiv",
            "email": app.email,
            "phone": "+1-650-283-3478",
            "location": "San Francisco, California, United States",
            "current company": "Amazon Web Services (AWS)",
            "current title": "Principal, AI Products & Platforms",
            "linkedin": "https://linkedin.com/in/beastofbayarea",
            "github": "https://github.com/beastofbayarea",
            "portfolio": "https://www.researchgate.net/profile/Shivam-Singh-188",
            "website": "https://github.com/beastofbayarea",
            "twitter": "https://x.com/BeastofBayArea",
            "notice": "2 weeks",
            "salary": app.salary,
            "compensation": app.salary
        }};
        
        let filledFields = 0;
        
        const inputs = Array.from(document.querySelectorAll("input[type='text'], input[type='email'], input[type='tel'], input:not([type])"));
        inputs.forEach(inp => {{
            const lbl = (inp.closest('label, div, section')?.innerText || '').toLowerCase();
            const attr = ((inp.name || '') + ' ' + (inp.placeholder || '') + ' ' + (inp.id || '')).toLowerCase();
            const comb = lbl + ' ' + attr;
            
            let f = false;
            for (const [k, v] of Object.entries(map)) {{
                if (comb.includes(k)) {{
                    setVal(inp, v);
                    f = true;
                    filledFields++;
                    break;
                }}
            }}
            if (!f) {{
                if (comb.includes('email')) {{ setVal(inp, app.email); filledFields++; }}
                else if (comb.includes('phone')) {{ setVal(inp, '+1-650-283-3478'); filledFields++; }}
                else if (comb.includes('linkedin')) {{ setVal(inp, 'https://linkedin.com/in/beastofbayarea'); filledFields++; }}
                else if (comb.includes('github')) {{ setVal(inp, 'https://github.com/beastofbayarea'); filledFields++; }}
                else if (comb.includes('name') && !comb.includes('company')) {{ setVal(inp, 'Shivam Singh'); filledFields++; }}
            }}
        }});
        
        const textareas = Array.from(document.querySelectorAll('textarea'));
        textareas.forEach(ta => {{ setVal(ta, app.essay); filledFields++; }});
        
        // Work Auth / Sponsorship radio buttons & options
        const labels = Array.from(document.querySelectorAll('label, div, p, span'));
        labels.forEach(el => {{
            const txt = (el.innerText || '').toLowerCase();
            if (txt.includes('authorized') || txt.includes('work in the us') || txt.includes('legally authorized')) {{
                const yesOpt = el.closest('div, section, fieldset')?.querySelector('input[value="Yes"], input[value="yes"]');
                if (yesOpt) {{ yesOpt.click(); yesOpt.checked = true; filledFields++; }}
            }}
            if (txt.includes('sponsorship') || txt.includes('require visa') || txt.includes('future require')) {{
                const noOpt = el.closest('div, section, fieldset')?.querySelector('input[value="No"], input[value="no"]');
                if (noOpt) {{ noOpt.click(); noOpt.checked = true; filledFields++; }}
            }}
        }});
        
        return {{ filled: filledFields, company: app.company, title: app.title }};
    }})()"""


async def populate_tab_via_ws(tab, app):
    ws_url = tab.get("webSocketDebuggerUrl")
    if not ws_url:
        print(f"  [Skip] No WS URL for tab: {tab.get('title')}")
        return False

    js_code = build_js_fill_script(app)

    try:
        # Activate tab via HTTP
        try:
            urllib.request.urlopen(f"{CDP_URL}/json/activate/{tab.get('id')}")
            await asyncio.sleep(0.1)
        except Exception:
            pass

        async with websockets.connect(ws_url, open_timeout=5) as ws:
            cmd = {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {"expression": js_code, "returnByValue": True},
            }
            await ws.send(json.dumps(cmd))
            resp = await ws.recv()
            data = json.loads(resp)
            result = data.get("result", {}).get("result", {}).get("value", {})
            print(
                f"  SUCCESS: Populated form for {app['company']} — {app['title']} ({app['email']}) -> {result.get('filled', 0)} elements updated!"
            )
            return True
    except Exception as ex:
        print(f"  ERROR populating tab {app['company']}: {ex}")
        return False


async def main():
    apps = parse_ashby_answers()
    print(f"Loaded {len(apps)} Ashby applications from master guide.")

    try:
        req = urllib.request.urlopen(f"{CDP_URL}/json/list")
        tabs = json.loads(req.read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to fetch CDP tab list: {e}")
        return

    ashby_tabs = [
        t for t in tabs if t.get("type") == "page" and "ashbyhq.com" in t.get("url", "").lower()
    ]
    print(f"Found {len(ashby_tabs)} open Ashby page tabs in Chrome debug session.")

    success_count = 0
    for idx, tab in enumerate(ashby_tabs, 1):
        t_url = tab.get("url", "").lower()
        matched = None
        for a in apps:
            job_id = a["url"].split("ashbyhq.com/")[-1].split("/application")[0]
            if job_id in t_url:
                matched = a
                break
        if not matched:
            matched = {
                "company": "Company",
                "title": "Role",
                "email": "shivamsin14@umich.edu",
                "salary": "$120,000–$160,000 USD",
                "essay": "IIT CS graduate & Ross MBA with 10+ years experience spanning AWS, D. E. Shaw, and Microsoft.",
            }

        print(f"\n[{idx}/{len(ashby_tabs)}] Tab: {tab.get('title')}")
        ok = await populate_tab_via_ws(tab, matched)
        if ok:
            success_count += 1

    print(f"\n=======================================================")
    print(f"Form Population Summary:")
    print(f" - Successfully Populated: {success_count} / {len(ashby_tabs)} Ashby open tabs!")
    print(f"=======================================================")


if __name__ == "__main__":
    asyncio.run(main())
