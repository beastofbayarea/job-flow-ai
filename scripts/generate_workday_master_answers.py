#!/usr/bin/env python3
"""Build personalized Workday resumes and a complete master-answer guide."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import json
import re
import secrets
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from job_application_automation.resume.generate import (  # noqa: E402
    JobInfo,
    _build_keyword_set,
    _enforce_candidate_identity,
    _enforce_source_invariants,
    _ensure_min_bullets,
    _generate_fallback_resume_data,
    _normalize_experience,
    _repair_education,
    _repair_experience,
    render_pdf,
)


QUEUE = ROOT / "data/application-queues/workday-job-search-2026-08-08.json"
EMAIL_POOL = ROOT / "config/candidate_email_pool.json"
OUTPUT = ROOT / "output"
MASTER = ROOT / "data/workday_master_answers.md"

FAMILY_KEYWORDS = {
    "product": [
        "Product Strategy", "Roadmaps", "Customer Discovery", "Agile", "APIs",
        "Platform Products", "Experimentation", "Product Analytics", "GTM",
        "Stakeholder Management", "AI/ML", "Cloud Infrastructure",
    ],
    "marketing": [
        "Demand Generation", "Product Marketing", "GTM Strategy", "Positioning",
        "Lifecycle Marketing", "Marketing Operations", "Paid Media", "Attribution",
        "Pipeline Growth", "Sales Enablement", "Experimentation", "Analytics",
    ],
    "program": [
        "Program Management", "Portfolio Governance", "RAID Management", "Agile",
        "Cross-functional Leadership", "Executive Reporting", "Risk Management",
        "Operating Cadence", "Change Management", "Process Optimization",
    ],
    "corporate_development": [
        "Corporate Development", "M&A", "Financial Modeling", "Due Diligence",
        "Market Sizing", "Investment Strategy", "Valuation", "Deal Execution",
        "Executive Communication", "Strategic Partnerships",
    ],
    "consulting": [
        "Management Consulting", "Transformation Strategy", "Operating Models",
        "Business Case Development", "Executive Stakeholders", "Data Analysis",
        "Change Management", "Process Redesign", "Program Delivery",
    ],
}

SUMMARY = {
    "product": (
        "Product and AI platform leader with 10+ years translating customer and market needs "
        "into scalable roadmaps, launches, and measurable adoption. At AWS, leads 12 GenAI "
        "workstreams and built a $122M enterprise pipeline through cross-functional product, "
        "engineering, sales, and partner execution."
    ),
    "marketing": (
        "Growth and product-marketing leader with 10+ years building data-driven GTM, demand, "
        "lifecycle, and enablement programs. Delivered a $12M demand engine producing $50M in "
        "incremental GMV at 4.1x ROI and built a $122M enterprise pipeline at AWS."
    ),
    "program": (
        "Program and transformation leader with 10+ years coordinating complex technology, "
        "business, and GTM portfolios. Leads 12 GenAI workstreams at AWS, aligning executives, "
        "engineering, operations, partners, risks, dependencies, and measurable delivery outcomes."
    ),
    "corporate_development": (
        "Strategy and corporate-development leader with 10+ years across technology, consulting, "
        "financial modeling, partnerships, and executive decision support. Combines an MBA from "
        "Michigan Ross with experience building business cases and a $122M enterprise pipeline."
    ),
    "consulting": (
        "Management-consulting and transformation leader with 10+ years solving complex strategy, "
        "technology, operating-model, and growth problems. Brings McKinsey training, an MBA from "
        "Michigan Ross, and current leadership of 12 enterprise GenAI workstreams at AWS."
    ),
}

ROLE_ALIGNMENT = {
    "product": "AI and platform product leader experienced in customer discovery, roadmap prioritization, technical delivery, GTM, adoption, and measurable enterprise outcomes.",
    "marketing": "Growth and product-marketing leader experienced in positioning, demand generation, lifecycle programs, analytics, sales enablement, and measurable pipeline creation.",
    "program": "Program leader experienced in multi-workstream governance, executive alignment, RAID management, process redesign, technology delivery, and change adoption.",
    "corporate_development": "Strategy and corporate-development leader experienced in market analysis, financial modeling, partnerships, diligence, executive decision support, and value creation.",
    "consulting": "Transformation consultant experienced in structured problem solving, operating models, business cases, executive communication, technology strategy, and implementation governance.",
}

LOCAL_TARGETS = {
    "USD": 120000,
    "GBP": 95000,
    "EUR": 110000,
    "CAD": 150000,
    "AUD": 180000,
    "INR": 10000000,
    "JPY": 18000000,
    "SGD": 160000,
    "CHF": 140000,
    "SEK": 1200000,
    "PLN": 480000,
}


@dataclass
class Posting:
    queue: dict[str, str]
    api_url: str
    info: dict[str, Any]
    text: str
    compensation_text: str
    currency: str
    ideal_compensation: str
    family: str
    keywords: list[str]
    email: str = ""
    resume: Path | None = None
    fetch_error: str = ""


def workday_api_url(url: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    job_index = next(i for i, part in enumerate(parts) if part.casefold() == "job")
    prefix = parts[:job_index]
    if prefix and re.fullmatch(r"[a-z]{2}-[A-Z]{2}", prefix[0], re.I):
        prefix = prefix[1:]
    if not prefix:
        raise ValueError(f"Could not determine Workday career site: {url}")
    tenant = parsed.hostname.split(".")[0]
    site = prefix[0]
    job_path = "/".join(parts[job_index + 1 :])
    return f"https://{parsed.hostname}/wday/cxs/{tenant}/{site}/job/{job_path}"


def html_to_text(value: str) -> str:
    soup = BeautifulSoup(html.unescape(value or ""), "html.parser")
    return html.unescape(re.sub(r"[ \t]+", " ", soup.get_text("\n", strip=True))).strip()


def compensation_excerpt(text: str) -> str:
    chunks = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text))
    money = re.compile(
        r"(?:[$£€]\s*\d|\b(?:USD|CAD|AUD|GBP|EUR|INR|JPY|SGD|CHF|SEK|PLN)\b|"
        r"\b\d[\d,.]*\s*(?:USD|CAD|AUD|GBP|EUR|INR|JPY|SGD|CHF|SEK|PLN)\b)",
        re.I,
    )
    pay = re.compile(r"salary|compensation|base pay|pay range|hourly|per (?:year|hour)", re.I)
    selected = [chunk.strip() for chunk in chunks if money.search(chunk) and pay.search(chunk)]
    return " ".join(selected[:4])[:1600]


def infer_currency(location: str, text: str, excerpt: str) -> str:
    combined = f"{excerpt} {text[:2500]}"
    for code in ("USD", "CAD", "AUD", "GBP", "EUR", "INR", "JPY", "SGD", "CHF", "SEK", "PLN"):
        if re.search(rf"\b{code}\b", combined, re.I):
            return code
    if "£" in excerpt:
        return "GBP"
    if "€" in excerpt:
        return "EUR"
    loc = location.casefold()
    mapping = {
        "united kingdom": "GBP", "london": "GBP", "germany": "EUR", "spain": "EUR",
        "france": "EUR", "italy": "EUR", "ireland": "EUR", "canada": "CAD",
        "australia": "AUD", "india": "INR", "japan": "JPY", "singapore": "SGD",
        "switzerland": "CHF", "sweden": "SEK", "mainz": "EUR", "germany": "EUR",
        "gurgaon": "INR", "bangalore": "INR", "cracow": "PLN", "poland": "PLN",
    }
    for marker, code in mapping.items():
        if marker in loc:
            return code
    return "USD"


def number_value(raw: str, suffix: str) -> float:
    value = float(raw.replace(",", ""))
    return value * 1000 if suffix.casefold() == "k" else value


def format_money(value: float, currency: str, hourly: bool = False) -> str:
    symbols = {"USD": "$", "CAD": "C$", "AUD": "A$", "GBP": "£", "EUR": "€", "INR": "₹", "JPY": "¥", "SGD": "S$", "CHF": "CHF ", "SEK": "SEK ", "PLN": "zł"}
    rounded = round(value, 2) if hourly else round(value / 1000) * 1000
    display = f"{rounded:,.2f}" if hourly else f"{rounded:,.0f}"
    return f"{symbols.get(currency, currency + ' ')}{display} {currency}"


def ideal_compensation(excerpt: str, currency: str) -> str:
    hourly = bool(re.search(r"hourly|per\s+hour|/\s*(?:hour|hr)\b", excerpt, re.I))
    symbol = r"(?:US\$|C\$|A\$|S\$|[$£€₹¥])"
    code = r"(?:USD|CAD|AUD|GBP|EUR|INR|JPY|SGD|CHF|SEK|PLN)"
    number = r"\d[\d,]*(?:\.\d+)?"
    values: list[float] = []
    range_pattern = re.compile(
        rf"(?:(?P<symbol>{symbol})\s*)?"
        rf"(?P<low>{number})\s*(?P<low_suffix>[kK]?)\s*"
        rf"(?:-|–|—|to)\s*(?:(?P<high_symbol>{symbol})\s*)?"
        rf"(?P<high>{number})\s*(?P<high_suffix>[kK]?)"
        rf"(?:\s*(?P<code>{code}))?",
        re.I,
    )
    for match in range_pattern.finditer(excerpt):
        if not (match.group("symbol") or match.group("high_symbol") or match.group("code")):
            continue
        low = number_value(match.group("low"), match.group("low_suffix"))
        high = number_value(match.group("high"), match.group("high_suffix"))
        if hourly and 10 <= low <= high <= 1000:
            values.extend((low, high))
        elif not hourly and 10000 <= low <= high <= 100000000:
            values.extend((low, high))
    if not values:
        single_pattern = re.compile(
            rf"(?:{symbol}\s*(?P<prefix>{number})\s*(?P<prefix_suffix>[kK]?)|"
            rf"(?P<suffix>{number})\s*(?P<suffix_suffix>[kK]?)\s*{code})",
            re.I,
        )
        for match in single_pattern.finditer(excerpt):
            raw = match.group("prefix") or match.group("suffix")
            suffix = match.group("prefix_suffix") or match.group("suffix_suffix") or ""
            value = number_value(raw, suffix)
            if hourly and 10 <= value <= 1000:
                values.append(value)
            elif not hourly and 10000 <= value <= 100000000:
                values.append(value)
    if len(values) >= 2:
        low, high = min(values), max(values)
        target = low + 0.65 * (high - low)
        return (
            f"Posted range: {format_money(low, currency, hourly)}–{format_money(high, currency, hourly)}"
            f"{' per hour' if hourly else ' annually'}. Ideal answer: {format_money(target, currency, hourly)}"
            f"{' per hour' if hourly else ' base annually'}, negotiable within the posted range."
        )
    if len(values) == 1:
        return f"Employer-stated figure: {format_money(values[0], currency, hourly)}. Ideal answer: match that figure and select negotiable."
    target = LOCAL_TARGETS[currency]
    return f"No numeric range found in the posting. Ideal answer if mandatory: {format_money(target, currency)} base annually, negotiable."


def classify(title: str) -> str:
    lowered = title.casefold()
    if any(term in lowered for term in ("corporate development", "investment", "m&a")):
        return "corporate_development"
    if "consult" in lowered or "strategy" in lowered and "marketing" not in lowered:
        return "consulting"
    if any(term in lowered for term in ("marketing", "paid media", "demand generation")):
        return "marketing"
    if "program" in lowered or "project manager" in lowered:
        return "program"
    return "product"


def extract_keywords(title: str, text: str, family: str) -> list[str]:
    candidates = list(FAMILY_KEYWORDS[family])
    phrases = {
        "Salesforce", "JIRA", "SQL", "SaaS", "B2B", "AI/ML", "Generative AI",
        "Machine Learning", "Product Management", "Marketing Automation", "SEO",
        "SEM", "CRM", "Cloud", "APIs", "Financial Modeling", "M&A", "Agile",
        "Program Management", "Change Management", "Data Analytics", "Paid Media",
    }
    lowered = f"{title} {text}".casefold()
    for phrase in sorted(phrases):
        if phrase.casefold() in lowered and phrase not in candidates:
            candidates.append(phrase)
    return candidates[:16]


def fetch_posting(queue_item: dict[str, str]) -> Posting:
    api_url = workday_api_url(queue_item["url"])
    payload: dict[str, Any] = {}
    error = ""
    header_sets = (
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": queue_item["url"],
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.5 Safari/605.1.15",
            "Accept": "application/json",
        },
    )
    for headers in header_sets:
        try:
            request = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.load(response)
            break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            error = f"{type(exc).__name__}: {exc}"
    info = payload.get("jobPostingInfo", {})
    text = html_to_text(info.get("jobDescription", ""))
    excerpt = compensation_excerpt(text)
    actual_location = str(info.get("location") or queue_item.get("location") or "Remote")
    currency = infer_currency(actual_location, text, excerpt)
    family = classify(str(info.get("title") or queue_item["title"]))
    keywords = extract_keywords(queue_item["title"], text, family)
    return Posting(
        queue=queue_item,
        api_url=api_url,
        info=info,
        text=text,
        compensation_text=excerpt,
        currency=currency,
        ideal_compensation=ideal_compensation(excerpt, currency),
        family=family,
        keywords=keywords,
        fetch_error=error if not payload else "",
    )


def safe_name(value: str, limit: int = 90) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9&()+,. -]+", " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:limit].rstrip(" .")


def select_relevant_bullets(data: dict[str, Any], keywords: list[str], limit: int) -> None:
    terms = {
        token.casefold()
        for keyword in keywords
        for token in re.findall(r"[A-Za-z][A-Za-z0-9+/-]{2,}", keyword)
    }
    remaining = limit
    experience = data.get("experience", [])
    for index, entry in enumerate(experience):
        bullets = list(entry.get("bullets", []))
        if not bullets or remaining <= 0:
            entry["bullets"] = []
            continue
        scored = []
        for original_index, bullet in enumerate(bullets):
            words = set(re.findall(r"[A-Za-z][A-Za-z0-9+/-]{2,}", str(bullet).casefold()))
            metric_bonus = 2 if re.search(r"[$%]|\b\d", str(bullet)) else 0
            scored.append((len(words & terms) + metric_bonus, -original_index, bullet))
        quota = min(3 if index < 2 else 2, remaining, len(scored))
        chosen = sorted(scored, reverse=True)[:quota]
        chosen.sort(key=lambda item: -item[1])
        entry["bullets"] = [item[2] for item in chosen]
        remaining -= quota


def tailored_resume(posting: Posting) -> Path:
    company = posting.queue["company"]
    title = posting.queue["title"]
    req_id = safe_name(str(posting.info.get("jobReqId") or posting.queue["url"].rstrip("/").rsplit("/", 1)[-1]), 28)
    url_key = hashlib.sha256(posting.queue["url"].encode("utf-8")).hexdigest()[:8]
    filename = f"Workday - {safe_name(company, 35)} - {safe_name(title, 62)} - {req_id} - {url_key}.pdf"
    output_path = OUTPUT / filename
    job = JobInfo(
        company=company,
        role_title=title,
        keywords=", ".join(posting.keywords),
        jd_overview=posting.text[:12000],
        jd_responsibilities=posting.text[:12000],
        jd_requirements=posting.text[:12000],
        url=posting.queue["url"],
        location=str(posting.info.get("location") or posting.queue["location"]),
        compensation=posting.ideal_compensation,
    )
    data = _generate_fallback_resume_data(job)
    data = _enforce_candidate_identity(data, posting.email)
    data["header_tagline"] = title
    data["professional_summary"] = SUMMARY[posting.family]
    data["skills"] = posting.keywords
    data = _normalize_experience(data)
    data = _repair_experience(data)
    data = _enforce_source_invariants(data)
    data = _repair_education(data)
    source_data = json.loads(json.dumps(data))
    extracted = ""
    for bullet_limit in (13, 11, 9, 7):
        data = json.loads(json.dumps(source_data))
        select_relevant_bullets(data, posting.keywords, bullet_limit)
        if not render_pdf(data, output_path, _build_keyword_set(job)):
            raise RuntimeError(f"PDF rendering failed: {output_path}")
        with fitz.open(output_path) as document:
            extracted = "".join(page.get_text() for page in document)
            if document.page_count == 1:
                break
    else:
        raise RuntimeError(f"Resume is not single-page after compression: {output_path}")
    if len(extracted.strip()) < 900:
        raise RuntimeError(f"Resume has insufficient extractable text: {output_path}")
    if posting.email not in extracted:
        raise RuntimeError(f"Resume email mismatch: {output_path}")
    return output_path.resolve()


def shared_answers() -> str:
    return """## Shared Workday Answer Bank

Use these answers when the exact field appears. Role sections below override email, resume, job title, compensation, and motivation.

1. **First name**: Shivam
2. **Preferred name**: Shiv
3. **Last name**: Singh
4. **Phone country code**: +1
5. **Phone**: 650-283-3478
6. **Address**: 447 Sutter Street, Ste 506
7. **City**: San Francisco
8. **State**: California
9. **Postal code**: 94108
10. **Country of residence**: United States
11. **Current employer**: Amazon Web Services
12. **Current title**: Principal, Generative AI
13. **Currently employed**: Yes
14. **LinkedIn**: https://linkedin.com/in/beastofbayarea
15. **GitHub**: https://github.com/beastofbayarea
16. **Portfolio / publications**: https://www.researchgate.net/profile/Shivam-Singh-188
17. **Highest degree**: Master's degree
18. **School**: University of Michigan
19. **Degree**: MBA
20. **Field of study**: Business
21. **Notice period / earliest start**: 2 weeks after accepting an offer
22. **How did you hear about us?**: LinkedIn
23. **Previously employed by this company?**: No
24. **Previously applied?**: No
25. **Open to relocation?**: Yes
26. **Willing to travel?**: Yes
27. **At least 18 years old?**: Yes
28. **Legally authorized to work in the United States?**: Yes
29. **Require U.S. sponsorship now or in the future?**: No
30. **India work-right question**: Indian citizen; answer the exact citizenship/right-to-work option truthfully.
31. **Other-country work authorization**: Do not infer from U.S. authorization or Indian citizenship; confirm the exact country-specific status.
32. **Background check consent**: Yes
33. **Accuracy certification**: Yes
34. **Privacy notice / data processing consent**: Yes
35. **Electronic signature**: Shivam Singh
36. **Pronouns**: They/them
37. **Gender**: Man / Male, matching the available option
38. **Race / ethnicity (U.S.)**: Asian / Asian American
39. **Veteran status (U.S.)**: I am not a protected veteran
40. **Disability status (U.S.)**: I have a disability, or have had one in the past
41. **Sexual orientation, if voluntarily requested**: Bisexual
42. **Transgender, if voluntarily requested**: No
43. **Languages**: English, French, Hindi
44. **Conflicts, restrictive covenants, criminal history, clearance, government employment, relatives at company, or other legal declarations**: Do not guess; candidate confirmation is required.

---
"""


def render_master(postings: list[Posting]) -> None:
    lines = [
        "# Workday Application Master Answers — 2026-08-08",
        "",
        f"This guide covers all {len(postings)} queue entries in `data/application-queues/workday-job-search-2026-08-08.json`.",
        "Compensation answers preserve employer-stated ranges and use the currency identified from the posting/location.",
        "",
        shared_answers().rstrip(),
        "",
    ]
    for index, posting in enumerate(postings, 1):
        info = posting.info
        location = str(info.get("location") or posting.queue["location"])
        description = re.sub(r"\s+", " ", posting.text)
        overview = description[:700].rsplit(" ", 1)[0] + ("…" if len(description) > 700 else "")
        req = str(info.get("jobReqId") or "Not stated")
        time_type = str(info.get("timeType") or "Not stated")
        posted = str(info.get("postedOn") or posting.queue["posting_date"])
        excerpt = posting.compensation_text or "No numeric compensation range was stated in the public posting."
        authorization = (
            "Yes; no sponsorship required" if posting.currency == "USD"
            else "Use the country-specific rule in the shared answer bank; do not infer eligibility"
        )
        lines.extend(
            [
                f"## {index}. {posting.queue['company']} — {posting.queue['title']}",
                "",
                f"- **URL**: `{posting.queue['url']}`",
                f"- **Queue Posting Date**: {posting.queue['posting_date']}",
                f"- **Workday Requisition ID**: {req}",
                f"- **Workday Location**: {location}",
                f"- **Time Type**: {time_type}",
                f"- **Posting Retrieval**: {'Complete' if not posting.fetch_error else 'Limited — ' + posting.fetch_error}",
                f"- **Email**: {posting.email}",
                f"- **Resume**: `{posting.resume}`",
                f"- **Work Authorization / Sponsorship**: {authorization}",
                f"- **Posting Compensation Evidence**: {excerpt}",
                f"- **Ideal Compensation Answer**: {posting.ideal_compensation}",
                f"- **Role Alignment**: {ROLE_ALIGNMENT[posting.family]}",
                f"- **Why this role**: I am excited to apply my experience in {', '.join(posting.keywords[:4])} to deliver measurable outcomes in this role at {posting.queue['company']}.",
                f"- **ATS Keywords**: {', '.join(posting.keywords)}",
                f"- **Posting Overview**: {overview}",
                "",
                "---",
                "",
            ]
        )
    MASTER.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    jobs = json.loads(QUEUE.read_text(encoding="utf-8"))
    emails = json.loads(EMAIL_POOL.read_text(encoding="utf-8"))
    if len(emails) < len(jobs):
        raise RuntimeError("Email pool is smaller than the Workday queue")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(fetch_posting, job) for job in jobs]
        postings = [future.result() for future in futures]

    unique_urls = list(dict.fromkeys(posting.queue["url"] for posting in postings))
    selected_emails = secrets.SystemRandom().sample(emails, len(unique_urls))
    email_by_url = dict(zip(unique_urls, selected_emails, strict=True))
    for stale in OUTPUT.glob("Workday - *.pdf"):
        stale.unlink()
    for posting in postings:
        posting.email = email_by_url[posting.queue["url"]]
        posting.resume = tailored_resume(posting)

    render_master(postings)
    print(f"Generated {len(postings)} resumes and {MASTER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
