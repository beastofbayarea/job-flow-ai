import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FIELDS_PATH = Path("data/ashby_aug08_extracted_fields.json")
ANSWERS_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\ashby_aug08_applications_master_answers.md")

def audit():
    fields_data = json.loads(FIELDS_PATH.read_text(encoding="utf-8"))
    answers_text = ANSWERS_PATH.read_text(encoding="utf-8")
    
    print("=== AUDITING 24 JOBS IN AUGUST 08 QUEUE FOR MISSING ANSWERS ===\n")
    
    missing_report = []
    
    for key, app in fields_data.items():
        idx = app.get("index")
        company = app.get("company")
        title = app.get("title")
        fields = app.get("fields", [])
        
        # Check section in answers document
        section_heading = f"## {idx}. {company}"
        if section_heading.lower() not in answers_text.lower():
            # Try partial matching company name
            if company.lower() not in answers_text.lower():
                missing_report.append(f"Job [{idx}] {company} - {title}: Entire section missing from answer doc!")
                continue
                
        for f in fields:
            label = f.get("label", "").strip()
            if not label:
                continue
                
            # Filter standard system fields (resume, name, email, phone, linkedin) which are universally defined in header
            norm_label = re.sub(r"[^a-z0-9]", "", label.lower())
            
            # Check if custom question or specific field is mentioned in answers text
            is_found = False
            
            # Common standard fields covered in header profile
            common_tokens = ["resume", "fullname", "name", "email", "phone", "location", "linkedin", "github", "twitter", "website", "portfolio"]
            if any(token in norm_label for token in common_tokens):
                is_found = True
            else:
                # Search for label or clean keywords in answers text
                words = [w for w in re.findall(r"[a-z0-9]+", label.lower()) if len(w) > 3]
                if words:
                    # Match if at least 2 key words appear in text
                    matches = sum(1 for w in words if w in answers_text.lower())
                    if matches >= min(2, len(words)):
                        is_found = True
                        
            if not is_found:
                missing_report.append(f"[{idx}] {company} ({title}) -> Missing Field: '{label}' [{f.get('type')}]")
                
    if missing_report:
        print(f"FOUND {len(missing_report)} UNANSWERED FIELD(S):")
        for m in missing_report:
            print(f" - {m}")
    else:
        print("🎉 ALL QUESTIONS AND FIELDS ACROSS ALL 24 JOBS HAVE 100% COVERED ANSWERS!")

if __name__ == "__main__":
    audit()
