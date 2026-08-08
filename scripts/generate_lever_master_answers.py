import json
import random
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

LEVER_DATA_PATH = Path("data/lever_20_extracted_fields.json")
POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")
OUT_MD_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\lever_20_applications_master_answers.md")

def generate():
    lever_data = json.loads(LEVER_DATA_PATH.read_text(encoding="utf-8"))
    email_pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    
    # Pick 20 unique random emails
    selected_emails = random.sample(email_pool, 20)
    
    md_lines = [
        "# 100% Complete Master Field & Answer Guide for Lever Queue (First 20 Applications)",
        "",
        "Based on Candidate Resume (`data/resumes/resume-general.pdf`) & Candidate Profile:",
        "- **Candidate Name**: Shivam Singh (Shiv)",
        "- **Phone**: `+1-650-283-3478`",
        "- **Location**: San Francisco, California, USA (Zip: 94108)",
        "- **LinkedIn**: `https://linkedin.com/in/beastofbayarea`",
        "- **GitHub**: `https://github.com/beastofbayarea`",
        "- **Portfolio / Research**: `https://www.researchgate.net/profile/Shivam-Singh-188`",
        "- **Current Role**: Principal, AI Products & Platforms at AWS",
        "- **Education**: MBA, University of Michigan (Ross); B.Tech CSE, Indian Institute of Technology (IIT)",
        "- **Work Auth / Sponsorship**: US Authorized (`Yes`), No sponsorship required (`No`)",
        "- **EEO Demographics**: Gender: Male | Race: Asian (Not Hispanic or Latino) | Veteran: I am not a protected veteran | Disability: Yes, I have a disability",
        "",
        "---",
        ""
    ]
    
    for idx, (key, app) in enumerate(lever_data.items(), 1):
        company = app.get("company")
        title = app.get("title")
        url = app.get("url")
        email = selected_emails[idx - 1]
        fields = app.get("fields", [])
        
        md_lines.append(f"## {idx}. {company} — {title}")
        md_lines.append(f"* **URL**: `{url}`")
        md_lines.append("")
        md_lines.append("### Complete Field Answers:")
        md_lines.append(f"1. **Full Name**: Shivam Singh")
        md_lines.append(f"2. **Email**: {email}")
        md_lines.append(f"3. **Phone**: +1-650-283-3478")
        md_lines.append(f"4. **Current Company**: Amazon Web Services")
        md_lines.append(f"5. **LinkedIn**: https://linkedin.com/in/beastofbayarea")
        md_lines.append(f"6. **GitHub / Portfolio**: https://github.com/beastofbayarea | https://www.researchgate.net/profile/Shivam-Singh-188")
        md_lines.append(f"7. **Location**: San Francisco, CA, United States")
        md_lines.append(f"8. **Work Authorization**: Yes, legally authorized to work in the US")
        md_lines.append(f"9. **Visa Sponsorship Required**: No")
        
        # Tailored custom essay/written answers based on role title & company
        if "Pointclickcare" in company:
            md_lines.append("10. **Why PointClickCare & AI Models?**: Combining a CS degree from IIT and Ross MBA with AI product leadership at AWS, I lead foundational model deployment and RAG architectures across 12 workstreams. PointClickCare’s healthcare AI vision matches my background scaling secure, highly regulated compliance-as-code models.")
        elif "Flex" in company:
            md_lines.append("10. **Product Marketing & Positioning Experience**: At Rakuten and Microsoft, I led GTM positioning shifts for fintech/rewards and enterprise partner programs ($12M budget driving $50M GMV at 4.1x ROI). I excel at translating complex financial tech into clear value propositions.")
        elif "Outreach" in company:
            md_lines.append("10. **Business Systems TPM Background**: 10+ years managing complex enterprise business systems and cloud architecture at AWS, D. E. Shaw, and Microsoft, reducing deployment cycles from 6 months to 2 hours.")
        elif "Crypto" in company:
            md_lines.append("11. **Crypto & Trading Experience**: Managed $10M real-time risk platforms and high-frequency trading infrastructure (5.4M msg/sec) at The D. E. Shaw Group, alongside authoring published crypto research.")
        elif "Novara" in company or "Demand" in title:
            md_lines.append("10. **Demand Generation & ABM Track Record**: Architected a $12M partner marketing engine at Microsoft using Random Forest propensity scoring and budget shaping; drove $50M incremental GMV at 4.1x ROI and raised partner conversion 5% -> 24%.")
        elif "Smarsh" in company:
            md_lines.append("10. **Agentic & Platform PM Vision**: Led multi-agent GenAI shopping copilots at AWS using Amazon Bedrock, RAG embeddings, and Bedrock Guardrails, reducing hallucinations from 8% to 2.8% and driving +15% session depth.")
        elif "Spotify" in company:
            md_lines.append("10. **Creator Platform & GTM Leadership**: Scaled digital consumer engagement loops at Rakuten (doubling D30 retention from 34% to 67%) and led multi-channel partner growth programs at Microsoft.")
        
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
    OUT_MD_PATH.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Lever 20 Master Guide generated successfully at {OUT_MD_PATH}")

if __name__ == "__main__":
    generate()
