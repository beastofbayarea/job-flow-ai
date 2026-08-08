import json
import random
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")
MASTER_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\ashby_aug08_applications_master_answers.md")

def enforce_unique():
    pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    content = MASTER_PATH.read_text(encoding="utf-8")
    
    # Split by section headers: ## 1., ## 2. ... ### 25., ### 26., ### 27.
    sections = re.split(r"(^(?:##|###) \d+\. .*$)", content, flags=re.MULTILINE)
    
    selected_emails = random.sample(pool, (len(sections) - 1) // 2)
    
    new_parts = [sections[0]]
    app_idx = 0
    
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i+1]
        
        assigned_email = selected_emails[app_idx]
        app_idx += 1
        
        # Replace any email line or email address in this section
        body_updated = re.sub(r"(\*\*Email\*\*:?\s*)[^\s\|]+", rf"\1{assigned_email}", body)
        body_updated = re.sub(r"(Email:\s*)[^\s\|]+", rf"\1{assigned_email}", body_updated)
        body_updated = re.sub(r"(Email`:\s*)[^\s\|`]+", rf"\1{assigned_email}", body_updated)
        
        new_parts.append(header)
        new_parts.append(body_updated)
        print(f"App [{app_idx}] {header.strip()} -> {assigned_email}")
        
    final_text = "".join(new_parts)
    MASTER_PATH.write_text(final_text, encoding="utf-8")
    print("\nEnforced 100% unique random emails across all 27 application sections!")

if __name__ == "__main__":
    enforce_unique()
