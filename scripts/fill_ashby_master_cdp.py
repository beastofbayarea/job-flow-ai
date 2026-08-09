"""Fill Ashby tabs from ashby_master_answers.md without submitting them."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout.reconfigure(encoding="utf-8")

from job_application_automation.engines.ashby_raw_cdp import fill_ashby_target

MASTER = ROOT / "data" / "ashby_master_answers.md"
ENDPOINT = "http://localhost:9222"
OUTPUT_DIR = ROOT / "output"


def normalize(value: str) -> str:
    value = value.casefold().replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def clean_value(value: str) -> str:
    lines: list[str] = []
    for raw in value.splitlines():
        line = raw.strip()
        line = re.sub(r"^(?:>|[-*])\s*", "", line)
        line = re.sub(r"^\d+\.\s*", "", line)
        line = line.strip(" `")
        if line and line != "---":
            lines.append(line)
    return "\n".join(lines).strip()


def parse_fields(body: str) -> dict[str, str]:
    pattern = re.compile(
        r"\*\*(?P<label>[^*\n]+)\*\*:\s*(?P<value>.*?)"
        r"(?=(?:\s*\|\s*)?\*\*[^*\n]+\*\*:|^\s*(?:\d+\.\s+)?\*\*|^---\s*$|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    fields: dict[str, str] = {}
    for match in pattern.finditer(body):
        label = match.group("label").strip()
        value = clean_value(match.group("value"))
        if value:
            fields[label] = value
    return fields


def parse_apps() -> list[dict[str, object]]:
    text = MASTER.read_text(encoding="utf-8")
    headings = list(
        re.finditer(r"^#{2,4}\s+(\d+)\.\s+(.+?)\s+[—-]\s+(.+?)\s*$", text, re.MULTILINE)
    )
    apps: list[dict[str, object]] = []
    for index, heading in enumerate(headings):
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end() : body_end]
        url_match = re.search(r"https://jobs\.ashbyhq\.com/[^`\s]+", body)
        if not url_match:
            continue
        url = url_match.group(0).rstrip("/")
        if not url.endswith("/application"):
            url += "/application"
        fields = parse_fields(body)
        exceptional = ["GTM & Pipeline Engine", "Regulated & Enterprise GTM Growth", "Growth & Cohort Analytics"]
        if all(label in fields for label in exceptional):
            fields["3 Bullets showing exceptional ability"] = "\n".join(
                f"• {label}: {fields[label]}" for label in exceptional
            )
        apps.append(
            {
                "number": int(heading.group(1)),
                "company": heading.group(2).strip(),
                "title": heading.group(3).strip(),
                "url": url,
                "fields": fields,
            }
        )
    return apps


def resume_for(app: dict[str, object]) -> Path:
    fields = app["fields"]
    assert isinstance(fields, dict)
    listed = fields.get("Resume") or fields.get("Resume Upload")
    if listed:
        direct = Path(str(listed))
        if direct.exists():
            return direct.resolve()

    raw_wanted = normalize(f"{app['company']} {app['title']}")
    exact_candidates = []
    for pdf in OUTPUT_DIR.glob("*.pdf"):
        candidate = normalize(re.sub(r"\bpersonalized resume\b", "", pdf.stem, flags=re.IGNORECASE))
        if candidate == raw_wanted or candidate.replace(" ", "") == raw_wanted.replace(" ", ""):
            exact_candidates.append(pdf)
    if exact_candidates:
        return sorted(exact_candidates, key=lambda path: ("(" in path.name, len(path.name), path.name.casefold()))[0].resolve()

    ignored = {"personalized", "resume", "senior", "lead", "manager", "director", "and", "the"}
    wanted = set(raw_wanted.split()) - ignored
    candidates: list[tuple[int, int, Path]] = []
    for pdf in OUTPUT_DIR.glob("*.pdf"):
        tokens = set(normalize(pdf.stem).split()) - ignored
        overlap = len(wanted & tokens)
        missing = len(wanted - tokens)
        candidates.append((overlap, -missing, pdf))
    candidates.sort(key=lambda item: (item[0], item[1], str(item[2]).casefold()), reverse=True)
    if not candidates or candidates[0][0] < max(2, len(wanted) // 2):
        raise FileNotFoundError(f"No role-specific resume match for {app['company']} - {app['title']}")
    return candidates[0][2].resolve()


def target_map() -> dict[str, dict[str, object]]:
    with urllib.request.urlopen(f"{ENDPOINT}/json/list", timeout=10) as response:
        targets = json.load(response)
    mapped: dict[str, dict[str, object]] = {}
    for target in targets:
        url = str(target.get("url", ""))
        if target.get("type") == "page" and "jobs.ashbyhq.com" in url.casefold():
            mapped.setdefault(url.rstrip("/").casefold(), target)
    return mapped


def open_fresh_target(url: str) -> dict[str, object]:
    encoded = urllib.parse.quote(url, safe="")
    request = urllib.request.Request(f"{ENDPOINT}/json/new?{encoded}", method="PUT")
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def close_duplicate_targets(url: str, keep_id: str) -> None:
    with urllib.request.urlopen(f"{ENDPOINT}/json/list", timeout=10) as response:
        targets = json.load(response)
    wanted = url.rstrip("/").casefold()
    for target in targets:
        if str(target.get("id")) == keep_id:
            continue
        if str(target.get("url", "")).rstrip("/").casefold() != wanted:
            continue
        try:
            urllib.request.urlopen(f"{ENDPOINT}/json/close/{target['id']}", timeout=5).read()
        except Exception:
            pass


def activate_target(target_id: str) -> None:
    urllib.request.urlopen(f"{ENDPOINT}/json/activate/{target_id}", timeout=5).read()


def split_values(fields: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    canonical = {
        "name": "name", "full name": "name", "legal name": "name", "your name": "name",
        "email": "email", "phone": "phone", "phone number": "phone",
        "location": "location", "linkedin": "linkedin", "linkedin profile": "linkedin",
        "preferred name": "preferred_name",
    }
    values = {
        "name": "Shivam Singh", "first_name": "Shivam", "last_name": "Singh",
        "preferred_name": "Shiv", "email": "", "phone": "+1-650-283-3478",
        "location": "San Francisco, California, United States",
        "linkedin": "https://linkedin.com/in/beastofbayarea",
        "github": "https://github.com/beastofbayarea",
        "twitter": "https://x.com/BeastofBayArea",
        "portfolio": "https://www.researchgate.net/profile/Shivam-Singh-188",
    }
    answers: dict[str, str] = {}
    for label, value in fields.items():
        key = normalize(label)
        if key in {"resume", "resume upload", "url"}:
            continue
        if key in canonical:
            values[canonical[key]] = value
        else:
            answers[label] = value
    semantic_aliases = {
        "location": [
            "What state are you located in? (If not in the U.S., what country are you located in?)",
            "What is your current location?",
            "What location do you plan to work from?",
            "Where are you currently located?",
        ],
        "us work authorization": [
            "If located in the US, are you currently authorized to work in the US?",
            "Are you legally authorized to work in the United States?",
            "Are you authorized to work in the country where the job is located?",
        ],
        "work authorization": [
            "Are you legally authorized to work in the United States?",
            "Are you authorized to work in the country where the job is located?",
            "Do you currently have legal work authorization (or right to work) in the country you are planning to live and work?",
            "Are you legally authorized to work where the job is being offered?",
        ],
        "work auth": [
            "Are you legally authorized to work in the United States?",
            "Are you authorized to work in Australia?",
        ],
        "pronouns": ["What are your preferred pronouns?", "What are your pronouns?"],
        "preferred name": ["Preferred name (if applicable)"],
        "links": ["Links to your GitHub, portfolio, website, Linkedin, etc."],
        "links github portfolio website linkedin": ["Links to your GitHub, portfolio, website, Linkedin, etc."],
        "phonetic spelling": [
            "So we can pronounce it correctly, what is the phonetic spelling of your name? (e.g., Kristina would be chris-teen-uh)",
        ],
        "desired salary": ["Salary Expectations", "Please share your desired salary:", "What is your desired salary?"],
        "please share your desired salary": ["Please share your desired salary:"],
        "salary": ["What are your salary expectations for this role?"],
        "notice period": ["What is your notice period?"],
        "linkedin": ["Your LinkedIn profile"],
        "why are you a good fit": ["Why are you a good fit for this role?"],
        "introduce yourself 300 chars": ["In 300 characters or less, please introduce yourself!"],
        "why goodparty org": ["Why are you interested in GoodParty.org?"],
        "ai problem solved": [
            "Describe a problem you solved using AI. What was the challenge, how did you approach it, what tool(s) did you use, and what outcome did you achieve?",
        ],
        "where are you working ai first today": ["Where are you already working AI-first today?"],
        "why are you interested in help scout and this role": [
            "Why are you interested in joining Help Scout? Why are you interested in this role?",
        ],
        "proficiency": ["How would you rate your financial modeling and forecasting skills?"],
        "customer facing enterprise ai tpm experience": [
            "Do you have years of experience as an Engineering or Technical Program Manager, with at least 2 years in customer-facing technical delivery and operations focused on enterprise-grade AI software/solutions? Please explain.",
        ],
        "transforming sales team to consultative culture": [
            "Describe how you have built or transformed a sales team from a transactional, quota-first culture to a consultative one. What did you change, how did you develop individual sellers, and what resistance did you encounter? How did you measure whether the shift was working?",
        ],
        "sales process built or redesigned": [
            "Walk us through a sales process you built or significantly redesigned. What problem were you solving, what did you put in place, and how did you drive adoption across your team? What would you build differently at Audiohook given what you know about our model?",
        ],
        "forecasting approach in complex sales": [
            "Forecasting in a consultative, complex-sale environment is notoriously difficult. Describe your approach to building forecast accuracy across a team. What systems, disciplines, or practices did you put in place, and how did you handle sellers who consistently over- or under-forecast?",
        ],
        "sales to client success implementation handoff": [
            "The transition from signed agreement to successful campaign launch is where many sales organizations lose deals they've already won. Describe how you have managed or redesigned the handoff between Sales and implementation or client success teams. What broke, what did you fix, and how did you measure improvement?",
        ],
        "handling pressure for poor fit clients": [
            "Audiohook's model depends on bringing in the right clients not just more clients. Describe a time when you faced real pressure to close deals that you believed were not good fits. How did you handle it, how did you communicate upward, and what was the outcome? In retrospect, were you right?",
        ],
        "tell us about a specific time you improved customer activation or time to value": [
            "Tell us about a specific time you improved customer activation or time-to-value. What signals told you there was a problem, what did you ship, and what was the actual measured result?",
        ],
        "describe a positioning or messaging shift you led": [
            "Describe a positioning or messaging shift you led. What was the old narrative, what made you reposition, and how did you validate the new direction with customers and the sales team?",
        ],
        "walk us through a product launch you owned end to end what is the single decision you re least proud of in hindsight": [
            "Walk us through a product launch you owned end-to-end. What is the single decision you're least proud of in hindsight, and what would you do differently?",
        ],
        "tell us about a time customer or win loss research changed your mind about something": [
            "Tell us about a time customer or win/loss research changed your mind about something — positioning, a feature, a segment, anything. What did you hear, and what did you do about it?",
        ],
        "how do you use ai tools in your product marketing work today": [
            "How do you use AI tools in your product marketing work today? Give us a specific example where AI changed your output — and a specific example where it produced something you had to throw out or significantly rework.",
        ],
        "in 3 5 sentences walk us through a demand gen program you built or owned": [
            "In 3-5 sentences, walk us through a demand gen program you built or owned. What was the channel mix, what did it produce in pipeline, and what would you do differently?",
        ],
        "describe a workflow or system you ve built using ai tools": [
            "Describe a workflow or system you've built using AI tools. What problem did it solve, what tools did you use, and how did it actually work?",
        ],
        "3 bullets showing exceptional ability": ["Please add up to three bullets showing exceptional ability"],
        "company": ["Current Company"],
        "zip": ["Location - Zip Code"],
        "excited to work full time in an office": [
            "Are you able, willing, and excited to work full-time in an office?",
        ],
        "years of experience": ["How many years of relevant experience do you have?"],
        "university": ["Where did you go to University?"],
        "start date": ["When can you start a new role?"],
        "infrastrucutre datacenter tpm experience": ["Additional Information"],
        "saas growth experience": ["Do you have experience leading Growth for a SaaS company?"],
        "plg experience": ["Do you have experience with PLG?"],
        "ai policy": ["AI Application Policy - Please indicate ‘Yes’ if you have read and agree."],
        "sponsorship": [
            "Will you now or in the future require sponsorship for employment visa status in this country?",
            "Will you now, or in the future, require visa sponsorship to work in the country that you are residing in?",
            "Will you, now or in the future, require Weaviate's support to maintain that authorization?",
            "Will you require sponsorship in the future?",
        ],
        "visa sponsorship": [
            "Will you now, or in the future, require visa sponsorship to work in the country that you are residing in?",
        ],
    }
    for source, labels in semantic_aliases.items():
        source_value = next((value for label, value in fields.items() if normalize(label) == source), None)
        if source_value:
            for label in labels:
                answers.setdefault(label, source_value)
    answers.setdefault("How did you hear about us?", "LinkedIn")
    answers.setdefault("How did you hear about Help Scout?", "LinkedIn")
    answers.setdefault("Where did you hear about this vacancy?", "LinkedIn")
    answers.setdefault("Github Profile", values["github"])
    answers.setdefault("GitHub", values["github"])
    answers.setdefault("Website", values["portfolio"])
    answers.setdefault("Website / Portfolio / Github URL", values["github"])
    answers.setdefault("Legal FULL Name", values["name"])
    answers.setdefault("Mobile Phone", values["phone"])
    answers.setdefault("GitHub Profile URL", values["github"])
    answers.setdefault("Portfolio URL", values["portfolio"])
    answers.setdefault("Please type out the city and state/province/country you live in.", values["location"])
    answers.setdefault("What country do you live in?", "United States")
    answers.setdefault("What location do you plan to work from?", values["location"])
    return values, answers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--activate", action="store_true")
    parser.add_argument("--command-timeout", type=float, default=8)
    parser.add_argument("--render-timeout", type=float, default=12)
    parser.add_argument("--reuse-loaded", action="store_true")
    args = parser.parse_args()

    apps = [app for app in parse_apps() if int(app["number"]) >= args.start][: args.count]
    targets = target_map()
    results: list[dict[str, object]] = []
    for app in apps:
        resume = resume_for(app)
        target = open_fresh_target(str(app["url"])) if args.fresh and not args.dry_run else targets.get(str(app["url"]).rstrip("/").casefold())
        summary = {"number": app["number"], "company": app["company"], "title": app["title"], "resume": str(resume)}
        if args.dry_run:
            summary["target_id"] = target.get("id") if target else None
            summary["field_count"] = len(app["fields"])
            results.append(summary)
            continue
        if not target:
            summary.update({"success": False, "status": "TARGET_MISSING"})
            results.append(summary)
            continue
        if args.activate:
            activate_target(str(target["id"]))
            time.sleep(1)
        values, answers = split_values(app["fields"])
        result = fill_ashby_target(
            endpoint=ENDPOINT, target_id=str(target["id"]), url=str(app["url"]),
            resume=resume, values=values, answers=answers,
            command_timeout=args.command_timeout, render_timeout=args.render_timeout,
            navigate=not args.reuse_loaded,
        )
        summary.update(asdict(result))
        results.append(summary)
        if result.success and args.fresh:
            close_duplicate_targets(str(app["url"]), str(target["id"]))
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if all(item.get("target_id") and (args.dry_run or item.get("success")) for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
