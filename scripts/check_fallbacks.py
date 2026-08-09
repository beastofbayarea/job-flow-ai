import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\output")

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
    q4 = json.loads(Path("data/application-queues/lever-job-search-2026-08-04.json").read_text(encoding="utf-8"))
    q8 = json.loads(Path("data/application-queues/lever-job-search-2026-08-08.json").read_text(encoding="utf-8"))
    all_jobs = q4 + q8
    
    pdfs = list(OUTPUT_DIR.glob("*.pdf"))
    
    fallbacks = []
    
    for idx, j in enumerate(all_jobs, 1):
        comp = j.get("company", "")
        title = j.get("title", "")
        
        best_score = -1
        best_pdf = None
        for p in pdfs:
            s = score_resume_match(p.name, comp, title)
            if s > best_score:
                best_score = s
                best_pdf = p
                
        if not best_pdf or best_score < 15:
            fallbacks.append((idx, comp, title, best_score))
            
    print(f"Total Lever Jobs Analyzed: {len(all_jobs)}")
    print(f"Total Fallback Occurrences (Score < 15): {len(fallbacks)}")
    
    if fallbacks:
        print("\nFallback Roles List:")
        for idx, comp, title, s in fallbacks:
            print(f" - #{idx}: {comp} — {title} (Highest Score: {s})")
    else:
        print("\nZERO fallbacks! Every single one of the 96 Lever roles matched a relevant domain resume with a score >= 15.")

if __name__ == "__main__":
    run()
