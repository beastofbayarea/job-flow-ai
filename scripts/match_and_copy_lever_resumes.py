import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\output")
DATA_MD = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\data\lever_master_answers.md")
ARTIFACT_MD = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\lever_master_answers.md")
GENERAL_RESUME = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\data\resumes\resume-general.pdf")

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def score_resume_match(pdf_name: str, company: str, title: str) -> int:
    score = 0
    pdf_lower = pdf_name.lower()
    comp_lower = company.lower()
    title_lower = title.lower()
    
    # Direct company match
    if comp_lower in pdf_lower or pdf_lower.startswith(comp_lower):
        score += 100
        
    # Title words match
    title_words = [w for w in re.split(r"\W+", title_lower) if len(w) > 2]
    for w in title_words:
        if w in pdf_lower:
            score += 15
            
    # Key domain matches
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

def run():
    pdf_files = [f for f in OUTPUT_DIR.glob("*.pdf") if f.is_file()]
    print(f"Loaded {len(pdf_files)} candidate resumes from {OUTPUT_DIR}")
    
    md_content = DATA_MD.read_text(encoding="utf-8")
    
    # Regex to match each application section
    # ## N. Company — Role Title (Queue Label)
    app_blocks = re.split(r"(^## \d+\. .*$)", md_content, flags=re.MULTILINE)
    
    new_parts = [app_blocks[0]]
    matched_count = 0
    
    for i in range(1, len(app_blocks), 2):
        header = app_blocks[i]
        body = app_blocks[i+1]
        
        m_head = re.match(r"^## \d+\.\s*(.*?)\s*—\s*(.*?)(?:\s*\((.*?)\))?$", header.strip())
        if m_head:
            company = m_head.group(1).strip()
            title = m_head.group(2).strip()
        else:
            company = "Company"
            title = "Role"
            
        # Find best resume match
        best_pdf = None
        best_score = -1
        
        for pdf in pdf_files:
            s = score_resume_match(pdf.name, company, title)
            if s > best_score:
                best_score = s
                best_pdf = pdf
                
        if not best_pdf or best_score < 15:
            best_pdf = GENERAL_RESUME
            
        # Create a dedicated standardized copy in OUTPUT_DIR
        clean_company = sanitize_filename(company)
        clean_title = sanitize_filename(title)
        copy_filename = f"Lever - {clean_company} - {clean_title}.pdf"
        target_path = OUTPUT_DIR / copy_filename
        
        # Copy source PDF to target_path
        if not target_path.exists() or target_path.stat().st_size != best_pdf.stat().st_size:
            shutil.copy(str(best_pdf), str(target_path))
            
        rel_path = f"output/{copy_filename}"
        matched_count += 1
        
        # Replace line 17 in body: 17. **Resume Attachment**: ...
        updated_body = re.sub(
            r"17\.\s*\*\*Resume Attachment\*\*:.*",
            f"17. **Resume Attachment**: `{rel_path}`",
            body
        )
        
        new_parts.append(header)
        new_parts.append(updated_body)
        print(f"[{matched_count}/96] {company} — {title} -> {copy_filename} (Source: {best_pdf.name}, Score: {best_score})")
        
    final_md = "".join(new_parts)
    DATA_MD.write_text(final_md, encoding="utf-8")
    shutil.copy(str(DATA_MD), str(ARTIFACT_MD))
    print(f"\nCompleted matching! Updated all {matched_count} application resume attachments in master answers guide.")

if __name__ == "__main__":
    run()
