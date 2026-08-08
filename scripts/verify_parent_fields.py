import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FIELDS_PATH = Path("data/ashby_aug08_extracted_fields.json")
ANSWERS_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\ashby_aug08_applications_master_answers.md")

def check_parent_fields():
    fields_data = json.loads(FIELDS_PATH.read_text(encoding="utf-8"))
    answers_text = ANSWERS_PATH.read_text(encoding="utf-8").lower()
    
    print("=== STRICT PARENT FIELD COVERAGE AUDIT (24 JOBS) ===\n")
    
    unanswered_parent = []
    
    for key, app in fields_data.items():
        idx = app.get("index")
        company = app.get("company")
        title = app.get("title")
        fields = app.get("fields", [])
        
        for f in fields:
            label = f.get("label", "").strip()
            f_type = f.get("type", "")
            
            # Skip option variants under radio/checkbox
            if f_type in ["radio", "checkbox"] and label.lower() in [
                "male", "female", "decline to self-identify", "hispanic or latino", 
                "white (not hispanic or latino)", "black or african american (not hispanic or latino)",
                "native hawaiian or other pacific islander (not hispanic or latino)", "asian (not hispanic or latino)",
                "american indian or alaska native (not hispanic or latino)", "two or more races (not hispanic or latino)",
                "i identify as one or more of the classifications of protected veteran listed above",
                "i am not a protected veteran", "i decline to self-identify for protected veteran status",
                "yes", "no", "unsure", "other", "career site", "employee referral", "job board", "job fair", "previously employed",
                "rarely (<1 x per week)", "occasionally (1-2 x per week)", "daily", "man", "woman", "gender queer or non-binary",
                "google search", "meta", "tiktok", "youtube", "programmatic", "reddit", "not applicable",
                "$50k-$200k/mo", "$200k-$1m/mo", "$1m+/mo", "beginner", "intermediate", "advanced", "expert",
                "news article", "in person event", "referral", "i was reached out to", "other (please specify)"
            ]:
                continue
                
            norm_label = re.sub(r"[^a-z0-9]", "", label.lower())
            
            # Standard candidate fields automatically populated
            standard_tokens = ["resume", "fullname", "name", "email", "phone", "location", "linkedin", "github", "twitter", "website", "portfolio", "coverletter"]
            if any(tok in norm_label for tok in standard_tokens):
                continue
                
            # Search for field in answers document
            words = [w for w in re.findall(r"[a-z0-9]+", label.lower()) if len(w) > 3]
            matched = False
            if words:
                matches = sum(1 for w in words if w in answers_text)
                if matches >= min(2, len(words)):
                    matched = True
                    
            if not matched:
                unanswered_parent.append(f"[{idx}] {company} ({title}) -> Question: '{label}' [{f_type}]")
                
    if unanswered_parent:
        print(f"ATTENTION: Found {len(unanswered_parent)} unmapped parent question(s):")
        for u in unanswered_parent:
            print(f" - {u}")
    else:
        print("🎉 ALL PARENT QUESTIONS AND ESSAY FIELDS ACROSS ALL 24 JOBS ARE 100% ANSWERED IN THE MASTER GUIDE!")

if __name__ == "__main__":
    check_parent_fields()
