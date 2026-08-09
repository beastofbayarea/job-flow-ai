import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FILES = [
    Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\ashby_master_answers.md"),
    Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\lever_master_answers.md"),
    Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\workable_master_answers.md"),
    Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\icims_master_answers.md"),
    Path(r"c:\Users\Nagarro\Downloads\job-flow-ai\data\smartrecruiters_master_answers.md")
]

ARTIFACT_DIR = Path(r"C:\Users\Nagarro\.gemini\antigravity-ide\brain\ffb15041-044d-471d-8f91-40eaee4b2ad7")

def determine_salary_and_currency(company, title, location_str, full_text=""):
    t_low = title.lower()
    c_low = company.lower()
    loc_low = location_str.lower()
    text_low = full_text.lower()
    
    if "tremendous" in c_low:
        return "$225,000–$260,000 USD (Listed Range: $225,000–$300,000 USD)"
        
    # Currency by location
    if "london" in loc_low or "uk" in loc_low or "united kingdom" in loc_low or "gbr" in loc_low:
        return "£85,000–£125,000 GBP"
    elif "canada" in loc_low or "mississauga" in loc_low or "toronto" in loc_low or "vancouver" in loc_low or "cad" in loc_low:
        return "$130,000–$175,000 CAD"
    elif "auckland" in loc_low or "new zealand" in loc_low or "nz" in loc_low:
        return "$140,000–$180,000 NZD"
    elif "india" in loc_low or "bangalore" in loc_low or "noida" in loc_low or "hyderabad" in loc_low:
        return "₹3,500,000–₹5,500,000 INR"
    elif "greece" in loc_low or "paris" in loc_low or "france" in loc_low or "spain" in loc_low or "germany" in loc_low or "milan" in loc_low or "japan" in loc_low or "tokyo" in loc_low or "europe" in loc_low or "eu" in loc_low:
        if "japan" in loc_low or "tokyo" in loc_low:
            return "¥12,000,000–¥16,000,000 JPY"
        return "€85,000–€130,000 EUR"
    elif "korea" in loc_low or "seoul" in loc_low:
        return "₩120,000,000–₩160,000,000 KRW"
    else:
        return "$120,000–$160,000 USD"

def audit_and_fix_file(file_path):
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
        
    text = file_path.read_text(encoding="utf-8")
    
    # Split by headers (## N. Company — Title)
    blocks = re.split(r"(^## \d+\. .*$)", text, flags=re.MULTILINE)
    
    new_parts = [blocks[0]]
    updated_count = 0
    
    for i in range(1, len(blocks), 2):
        header = blocks[i]
        body = blocks[i+1]
        
        m = re.match(r"^## \d+\.\s*(.*?)\s*—\s*(.*?)(?:\s*\((.*?)\))?$", header.strip())
        if m:
            comp = m.group(1).strip()
            title = m.group(2).strip()
            extra = m.group(3).strip() if m.group(3) else ""
        else:
            comp = "Company"
            title = "Role"
            extra = ""
            
        sal_curr = determine_salary_and_currency(comp, title, f"{extra} {title} {comp}", body)
        
        # Replace field 16 or Desired Salary line
        if re.search(r"16\.\s*\*\*Desired Base Salary\*\*:.*", body):
            body = re.sub(
                r"16\.\s*\*\*Desired Base Salary\*\*:.*",
                f"16. **Desired Base Salary**: {sal_curr}",
                body
            )
        elif re.search(r"(\*\*Salary\*\*|\*\*Desired Salary\*\*|\*\*Salary Expectation\*\*):.*", body):
            body = re.sub(
                r"(\*\*Salary\*\*|\*\*Desired Salary\*\*|\*\*Salary Expectation\*\*):.*",
                rf"\1: {sal_curr}",
                body
            )
        else:
            # Append salary answer if missing
            body = body.rstrip() + f"\n- **Desired Salary**: {sal_curr}\n"
            
        new_parts.append(header)
        new_parts.append(body)
        updated_count += 1
        
    final_text = "".join(new_parts)
    file_path.write_text(final_text, encoding="utf-8")
    
    # Copy to artifact
    art_path = ARTIFACT_DIR / file_path.name
    shutil.copy(str(file_path), str(art_path))
    
    print(f"Audited & Updated {updated_count} applications in {file_path.name}")

def run():
    for f in FILES:
        audit_and_fix_file(f)
    print("\nAll ATS master answer files audited and synchronized with location/role specific salary ranges & currencies!")

if __name__ == "__main__":
    run()
