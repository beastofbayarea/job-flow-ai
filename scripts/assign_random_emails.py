import json
import random
import re
from pathlib import Path

POOL_PATH = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\config\candidate_email_pool.json")
MASTER_PATH = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7\ashby_aug08_applications_master_answers.md")

def run():
    # Set seed for reproducibility or random sample
    emails = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    
    # Select 24 unique random emails from pool
    selected = random.sample(emails, 24)
    
    content = MASTER_PATH.read_text(encoding="utf-8")
    
    # Split content by H2 headers: ## 1. Linear, ## 2. Runway, etc.
    sections = re.split(r"(^## \d+\. .*$)", content, flags=re.MULTILINE)
    
    new_content_parts = [sections[0]] # Header part before section 1
    
    app_counter = 0
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i+1]
        
        assigned_email = selected[app_counter]
        app_counter += 1
        
        # Replace shiv-ai-pm@umich.edu or any email line in this body
        updated_body = re.sub(
            r"(\*\*Email\*\*:?\s*)[^\s\|]+",
            rf"\1{assigned_email}",
            body
        )
        updated_body = re.sub(
            r"(Email:\s*)[^\s\|]+",
            rf"\1{assigned_email}",
            updated_body
        )
        
        new_content_parts.append(header)
        new_content_parts.append(updated_body)
        
        print(f"App [{app_counter}] -> Assigned Email: {assigned_email}")
        
    final_md = "".join(new_content_parts)
    MASTER_PATH.write_text(final_md, encoding="utf-8")
    print(f"\nSuccessfully assigned 24 unique emails to {MASTER_PATH}")

if __name__ == "__main__":
    run()
