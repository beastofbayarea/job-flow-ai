import json
import random
import re
import shutil
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

Q04_PATH = Path("data/application-queues/workable-job-search-2026-08-04.json")
Q08_PATH = Path("data/application-queues/workable-job-search-2026-08-08.json")
POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")
OUTPUT_DIR = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\output")
GENERAL_RESUME = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\data\resumes\resume-general.pdf")

DATA_MD = Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\workable_master_answers.md")
ARTIFACT_MD = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\workable_master_answers.md")

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def score_resume_match(pdf_name: str, company: str, title: str) -> int:
    score = 0
    pdf_lower = pdf_name.lower()
    comp_lower = company.lower()
    title_lower = title.lower()
    
    if comp_lower in pdf_lower or pdf_lower.startswith(comp_lower):
        score += 100
        
    title_words = [w for w in re.split(r"\W+", title_lower) if len(w) > 2]
    for w in title_words:
        if w in pdf_lower:
            score += 15
            
    if "ai" in title_lower and "ai" in pdf_lower:
        score += 20
    if ("marketing" in title_lower or "pmm" in title_lower) and ("marketing" in pdf_lower or "pmm" in pdf_lower):
        score += 20
    if ("demand" in title_lower or "growth" in title_lower) and ("demand" in pdf_lower or "growth" in pdf_lower):
        score += 20
    if ("program manager" in title_lower or "tpm" in title_lower) and ("program manager" in pdf_lower or "tpm" in pdf_lower):
        score += 20
    if ("security" in title_lower or "grc" in title_lower) and ("security" in pdf_lower or "grc" in pdf_lower):
        score += 20
    if ("crypto" in title_lower or "trading" in title_lower) and ("crypto" in pdf_lower or "trading" in pdf_lower or "fintech" in pdf_lower):
        score += 20
    if ("healthcare" in title_lower or "care" in title_lower) and ("healthcare" in pdf_lower or "health" in pdf_lower):
        score += 20
    if "operations" in title_lower and "operations" in pdf_lower:
        score += 20
        
    return score

def generate_tailored_essay(company, title):
    t = title.lower()
    c = company.lower()
    
    if "product manager" in t or "pm" in t or "product lead" in t:
        if "ai" in t or "model" in t or "agent" in t or "llm" in t:
            return (
                f"Combining a CS engineering degree from IIT and a Ross MBA with hands-on GenAI product leadership at AWS, "
                f"I lead agentic AI copilot strategy across 12 workstreams (+15% session depth, hallucination reduction from 8% to 2.8% using RAG and Bedrock Guardrails). "
                f"At D. E. Shaw, I built real-time data platforms handling 5.4M msg/sec. {company}’s vision in {title} aligns directly with my background deploying secure, high-impact enterprise AI platforms."
            )
        elif "crypto" in c or "trading" in t or "exchange" in t or "web3" in t:
            return (
                f"With 4 years at The D. E. Shaw Group managing $10M real-time risk platforms (5.4M msg/sec) and publishing blockchain research, "
                f"I bring deep quantitative finance and Web3 platform experience. At AWS and Microsoft, I scaled digital platform products to millions of users. "
                f"I am excited to drive product vision and execution for {title} at {company}."
            )
        else:
            return (
                f"Computer Science engineer (IIT B.Tech) and Ross MBA with 10+ years scaling core product platforms across AWS, Microsoft, and D. E. Shaw. "
                f"At Rakuten, I doubled D30 retention from 34% to 67% and optimized LTV:CAC from 0.8 to 4.5; at AWS, I compressed client rollout cycles from 6 months to 2 hours. "
                f"I bring proven product lifecycle execution, customer telemetry analytics, and platform scale to the {title} position at {company}."
            )
    elif "marketing" in t or "demand" in t or "growth" in t or "pmm" in t:
        return (
            f"At Microsoft, I architected a $12M partner marketing and demand generation engine using Random Forest propensity scoring and budget traffic-shaping, "
            f"generating $50M incremental GMV at a 4.1x ROI and increasing partner conversion from 5% to 24%. At Rakuten, I executed a B2B2C GTM repositioning that reduced CAC from $42 to $8.50. "
            f"I am eager to leverage data-driven growth channels, multi-touch attribution, and technical messaging to scale demand for {company}’s {title} role."
        )
    elif "program manager" in t or "tpm" in t or "operations" in t or "security" in t or "grc" in t:
        return (
            f"10+ years leading cross-functional technical program management across AWS, D. E. Shaw, and Microsoft. "
            f"At AWS, I led sovereign-cloud deployment reference architectures reducing enterprise rollout time from 6 months to 2 hours across regulated sectors. "
            f"At D. E. Shaw, I orchestrated high-frequency infrastructure programs handling 5.4M msg/sec. I bring disciplined GRC, hardware/software delivery telemetry, and executive stakeholder alignment to {company}."
        )
    else:
        return (
            f"IIT CS graduate & Ross MBA with 10+ years experience spanning AWS, D. E. Shaw, Microsoft, and McKinsey. "
            f"I combine technical architecture expertise with commercial strategy to drive high-leverage execution. "
            f"Excited to contribute to {company}'s growth in the {title} role."
        )

def run():
    q4 = json.loads(Q04_PATH.read_text(encoding="utf-8"))
    q8 = json.loads(Q08_PATH.read_text(encoding="utf-8"))
    
    all_jobs = []
    for j in q4:
        j["batch"] = "August 04 Queue"
        all_jobs.append(j)
    for j in q8:
        j["batch"] = "August 08 Queue"
        all_jobs.append(j)
        
    email_pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    random.seed(88) # Deterministic selection
    selected_emails = random.sample(email_pool, len(all_jobs))
    
    pdf_files = [f for f in OUTPUT_DIR.glob("*.pdf") if f.is_file()]
    
    lines = [
        "# 100% Comprehensive Master Field & Answer Guide for ALL 59 Workable Job Applications",
        "",
        "Grounding Candidate Credentials (`data/resumes/resume-general.pdf`):",
        "- **Candidate Name**: Shivam Singh (Shiv)",
        "- **Phonetic Spelling**: `Shih-vum Sing` | **Pronouns**: `they/them`",
        "- **Phone**: `+1-650-283-3478`",
        "- **Location**: San Francisco, California, USA (Zip: 94108)",
        "- **LinkedIn**: `https://linkedin.com/in/beastofbayarea`",
        "- **GitHub**: `https://github.com/beastofbayarea`",
        "- **Portfolio / Research**: `https://www.researchgate.net/profile/Shivam-Singh-188`",
        "- **Current Role**: Principal, AI Products & Platforms at AWS",
        "- **Education**: MBA, University of Michigan (Ross); B.Tech CSE, Indian Institute of Technology (IIT)",
        "- **Work Auth / Sponsorship**: US Authorized (`Yes`), No visa sponsorship required (`No`)",
        "- **Notice Period**: `2 weeks`",
        "- **Base Salary Range**: `$120,000–$160,000 USD` (or role-specific listed range)",
        "- **EEO Demographics**: Gender: Male | Race: Asian (Not Hispanic or Latino) | Veteran: I am not a protected veteran | Disability: Yes, I have a disability",
        "",
        "=================================================================================",
        ""
    ]
    
    for idx, j in enumerate(all_jobs, 1):
        company = j.get("company", "Company")
        title = j.get("title", "Role")
        raw_url = j.get("url", "")
        batch = j.get("batch", "")
        
        apply_url = raw_url.rstrip("/")
        if not apply_url.endswith("/apply"):
            apply_url += "/apply"
            
        email = selected_emails[idx - 1]
        
        # Match best fit resume
        best_pdf = None
        best_score = -1
        for pdf in pdf_files:
            s = score_resume_match(pdf.name, company, title)
            if s > best_score:
                best_score = s
                best_pdf = pdf
                
        if not best_pdf or best_score < 15:
            best_pdf = GENERAL_RESUME
            
        clean_company = sanitize_filename(company)
        clean_title = sanitize_filename(title)
        copy_filename = f"Workable - {clean_company} - {clean_title}.pdf"
        target_path = OUTPUT_DIR / copy_filename
        
        if not target_path.exists() or target_path.stat().st_size != best_pdf.stat().st_size:
            shutil.copy(str(best_pdf), str(target_path))
            
        rel_resume_path = f"output/{copy_filename}"
        custom_ans = generate_tailored_essay(company, title)
        
        lines.append(f"## {idx}. {company} — {title} ({batch})")
        lines.append(f"* **Application Form URL**: `{apply_url}`")
        lines.append("")
        lines.append("### Complete Field-by-Field Answers (No Skipped Fields):")
        lines.append(f"1. **Full Name**: Shivam Singh")
        lines.append(f"2. **Preferred Name**: Shiv")
        lines.append(f"3. **Phonetic Spelling**: Shih-vum Sing")
        lines.append(f"4. **Pronouns**: they/them")
        lines.append(f"5. **Email**: {email}")
        lines.append(f"6. **Phone Number**: +1-650-283-3478")
        lines.append(f"7. **Current Location**: San Francisco, California, United States (Zip: 94108)")
        lines.append(f"8. **Current Company**: Amazon Web Services (AWS)")
        lines.append(f"9. **Current Title**: Principal, AI Products & Platforms")
        lines.append(f"10. **LinkedIn Profile**: https://linkedin.com/in/beastofbayarea")
        lines.append(f"11. **GitHub Profile**: https://github.com/beastofbayarea")
        lines.append(f"12. **Portfolio / Research**: https://www.researchgate.net/profile/Shivam-Singh-188")
        lines.append(f"13. **Are you legally authorized to work in the US?**: Yes")
        lines.append(f"14. **Will you now or in the future require visa sponsorship?**: No")
        lines.append(f"15. **Notice Period**: 2 weeks")
        lines.append(f"16. **Desired Base Salary**: $120,000–$160,000 USD")
        lines.append(f"17. **Resume Attachment**: `{rel_resume_path}`")
        lines.append(f"18. **Why are you a fit for {company} & {title}? / Custom Essay Response**:\n    > {custom_ans}")
        lines.append(f"19. **EEO Gender**: Male")
        lines.append(f"20. **EEO Race / Ethnicity**: Asian (Not Hispanic or Latino)")
        lines.append(f"21. **EEO Veteran Status**: I am not a protected veteran")
        lines.append(f"22. **EEO Disability Status**: Yes, I have a disability")
        lines.append("")
        lines.append("---------------------------------------------------------------------------------")
        lines.append("")
        
    content = "\n".join(lines)
    DATA_MD.write_text(content, encoding="utf-8")
    shutil.copy(str(DATA_MD), str(ARTIFACT_MD))
    print(f"Successfully generated 100% complete field answers for ALL {len(all_jobs)} Workable applications!")
    print(f"Saved to:\n - {DATA_MD}\n - {ARTIFACT_MD}")

if __name__ == "__main__":
    run()
