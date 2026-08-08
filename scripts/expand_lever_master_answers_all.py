import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

EXTRACT_04_PATH = Path("data/lever_all_48_extracted_fields.json")
EXTRACT_08_PATH = Path("data/lever_aug08_48_extracted_fields.json")
CURRENT_MD_PATH = Path("data/lever_master_answers.md")
POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")

def generate_custom_answer(company, title):
    t_low = title.lower()
    c_low = company.lower()
    
    if "product manager" in t_low or "pm" in t_low or "product lead" in t_low:
        if "ai" in t_low or "model" in t_low or "agent" in t_low or "llm" in t_low:
            return (
                f"Combining a CS engineering degree from IIT and a Ross MBA with hands-on GenAI product leadership at AWS, "
                f"I lead agentic AI copilot strategy across 12 workstreams (+15% session depth, hallucination reduction from 8% to 2.8% using RAG and Bedrock Guardrails). "
                f"At D. E. Shaw, I built real-time data platforms handling 5.4M msg/sec. {company}’s vision in {title} aligns directly with my background deploying secure, high-impact enterprise AI platforms."
            )
        elif "crypto" in c_low or "trading" in t_low or "exchange" in t_low:
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
    elif "marketing" in t_low or "demand" in t_low or "growth" in t_low or "pmm" in t_low:
        return (
            f"At Microsoft, I architected a $12M partner marketing and demand generation engine using Random Forest propensity scoring and budget traffic-shaping, "
            f"generating $50M incremental GMV at a 4.1x ROI and increasing partner conversion from 5% to 24%. At Rakuten, I executed a B2B2C GTM repositioning that reduced CAC from $42 to $8.50. "
            f"I am eager to leverage data-driven growth channels, multi-touch attribution, and technical messaging to scale demand for {company}’s {title} role."
        )
    elif "program manager" in t_low or "tpm" in t_low or "operations" in t_low:
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
    e04 = json.loads(EXTRACT_04_PATH.read_text(encoding="utf-8"))
    e08 = json.loads(EXTRACT_08_PATH.read_text(encoding="utf-8"))
    
    email_pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    
    all_jobs = []
    for k, v in e04.items():
        v["queue_label"] = "Aug 04 Queue"
        all_jobs.append(v)
    for k, v in e08.items():
        v["queue_label"] = "Aug 08 Queue"
        all_jobs.append(v)
        
    selected_emails = email_pool[:len(all_jobs)]
    
    md_out = [
        "# 100% Comprehensive Master Field & Answer Guide for ALL 96 Lever Job Applications",
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
        queue_src = j.get("queue_label", "")
        apply_url = raw_url.rstrip("/")
        if not apply_url.endswith("/apply"):
            apply_url += "/apply"
            
        email = selected_emails[idx - 1]
        custom_ans = generate_custom_answer(company, title)
        
        md_out.append(f"## {idx}. {company} — {title} ({queue_src})")
        md_out.append(f"* **Application Form URL**: `{apply_url}`")
        md_out.append("")
        md_out.append("### Complete Field-by-Field Answers (No Skipped Fields):")
        md_out.append(f"1. **Full Name**: Shivam Singh")
        md_out.append(f"2. **Preferred Name**: Shiv")
        md_out.append(f"3. **Phonetic Spelling**: Shih-vum Sing")
        md_out.append(f"4. **Pronouns**: they/them")
        md_out.append(f"5. **Email**: {email}")
        md_out.append(f"6. **Phone Number**: +1-650-283-3478")
        md_out.append(f"7. **Current Location**: San Francisco, California, United States (Zip: 94108)")
        md_out.append(f"8. **Current Company**: Amazon Web Services (AWS)")
        md_out.append(f"9. **Current Title**: Principal, AI Products & Platforms")
        md_out.append(f"10. **LinkedIn Profile**: https://linkedin.com/in/beastofbayarea")
        md_out.append(f"11. **GitHub Profile**: https://github.com/beastofbayarea")
        md_out.append(f"12. **Portfolio / Research**: https://www.researchgate.net/profile/Shivam-Singh-188")
        md_out.append(f"13. **Are you legally authorized to work in the US?**: Yes")
        md_out.append(f"14. **Will you now or in the future require visa sponsorship?**: No")
        md_out.append(f"15. **Notice Period**: 2 weeks")
        md_out.append(f"16. **Desired Base Salary**: $120,000–$160,000 USD")
        md_out.append(f"17. **Resume Attachment**: `data/resumes/resume-general.pdf`")
        md_out.append(f"18. **Why are you a fit for {company} & {title}? / Essay Response**:\n    > {custom_ans}")
        md_out.append(f"19. **EEO Gender**: Male")
        md_out.append(f"20. **EEO Race / Ethnicity**: Asian (Not Hispanic or Latino)")
        md_out.append(f"21. **EEO Veteran Status**: I am not a protected veteran")
        md_out.append(f"22. **EEO Disability Status**: Yes, I have a disability")
        md_out.append("")
        md_out.append("---------------------------------------------------------------------------------")
        md_out.append("")
        
    CURRENT_MD_PATH.write_text("\n".join(md_out), encoding="utf-8")
    print(f"Successfully generated complete field-by-field answers for ALL {len(all_jobs)} Lever applications at {CURRENT_MD_PATH}")

if __name__ == "__main__":
    run()
