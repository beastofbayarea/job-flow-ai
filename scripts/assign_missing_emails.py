import json
import random
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")
MASTER_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\ashby_aug08_applications_master_answers.md")

DEFAULT_EMAIL = "shiv-ai-pm@umich.edu"

def run():
    email_pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    content = MASTER_PATH.read_text(encoding="utf-8")
    
    # Track used emails
    used_emails = set(re.findall(r"[\w\.-]+@umich\.edu", content))
    if DEFAULT_EMAIL in used_emails:
        used_emails.remove(DEFAULT_EMAIL)
        
    available_emails = [e for e in email_pool if e not in used_emails]
    random.shuffle(available_emails)
    
    sections = re.split(r"(^## \d+\. .*$)", content, flags=re.MULTILINE)
    
    new_parts = [sections[0]]
    assigned_count = 0
    
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i+1]
        
        # Check if email is missing or default shiv-ai-pm@umich.edu
        if DEFAULT_EMAIL in body or "Email" not in body:
            new_email = available_emails.pop()
            assigned_count += 1
            
            if DEFAULT_EMAIL in body:
                body = body.replace(DEFAULT_EMAIL, new_email)
            else:
                # Add Email field under Complete Field Answers if missing
                body = re.sub(r"(### Complete Field Answers:\s*)", f"\\1\n1. **Email**: {new_email}\n", body)
                
            print(f"Updated section [{header.strip()}] -> New Email: {new_email}")
            
        new_parts.append(header)
        new_parts.append(body)
        
    final_content = "".join(new_parts)
    MASTER_PATH.write_text(final_content, encoding="utf-8")
    print(f"\nAssigned {assigned_count} random email(s) for missing/default fields.")

if __name__ == "__main__":
    run()
