import os
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\output")

def clean_and_standardize_filename(filename: str) -> str:
    # Remove file extension
    name = Path(filename).stem
    
    # Remove leading dots or numbers like .07-, 01-, 02-
    name = re.sub(r"^\.?\d+\s*[-_]\s*", "", name)
    
    # Remove attempt suffixes like .attempt-2
    name = re.sub(r"\.attempt[-_]\d+", "", name, flags=re.IGNORECASE)
    
    # Remove candidate name variations if any
    name = re.sub(r"\bshivam\s*singh\b", "", name, flags=re.IGNORECASE)
    
    # Replace "Personalized Resume" or "Personalized"
    name = re.sub(r"[-_]?\s*personalized\s*resume\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[-_]?\s*personalized\b", "", name, flags=re.IGNORECASE)
    
    # If filename is hyphen-separated lowercase like "aiprise-senior-content-marketing-manager", convert to title case structure
    if "-" in name and " - " not in name and "_" not in name:
        parts = [p.capitalize() for p in name.split("-") if p]
        if len(parts) >= 2:
            # Assume first word is company
            company = parts[0]
            role = " ".join(parts[1:])
            # Clean special company names
            if company.lower() == "tapcart" and len(parts) > 2 and parts[1].lower() == "inc":
                company = "Tapcart Inc"
                role = " ".join(parts[2:])
            elif company.lower() == "pano" and len(parts) > 2 and parts[1].lower() == "ai":
                company = "Pano AI"
                role = " ".join(parts[2:])
            elif company.lower() == "runway" and len(parts) > 2 and parts[1].lower() == "ml":
                company = "Runway ML"
                role = " ".join(parts[2:])
            elif company.lower() == "tribe" and len(parts) > 2 and parts[1].lower() == "ai":
                company = "Tribe AI"
                role = " ".join(parts[2:])
            name = f"{company} - {role}"
            
    # Fix spacing around hyphens
    name = re.sub(r"\s*-\s*", " - ", name)
    
    # Clean up double hyphens or multiple spaces
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"(\s*-\s*){2,}", " - ", name)
    name = name.strip(" -_")
    
    # Title Case cleanup for components
    parts = name.split(" - ")
    cleaned_parts = []
    for p in parts:
        words = p.split()
        title_words = []
        for w in words:
            # Keep acronyms uppercase (AI, HR, PM, PMM, TPM, GRC, M&A, APAC, SMB, USA, AWS, LLM, C2, API, FinTech, EdTech)
            if w.upper() in ["AI", "HR", "PM", "PMM", "TPM", "GRC", "M&A", "APAC", "SMB", "USA", "AWS", "LLM", "C2", "API", "FINTECH", "EDTECH", "IDP", "KYC", "ABM", "GTM", "DTC", "B2B2C", "PLG", "EHR", "RAG"]:
                title_words.append(w.upper())
            elif w.lower() in ["and", "or", "for", "of", "in", "the", "on", "at", "to", "a", "an"] and len(title_words) > 0:
                title_words.append(w.lower())
            else:
                title_words.append(w.capitalize())
        cleaned_parts.append(" ".join(title_words))
        
    final_name = " - ".join(cleaned_parts) + ".pdf"
    return final_name

def run():
    print(f"Scanning {OUTPUT_DIR}...")
    
    # Step 1: Find all PDF files in subdirectories and move them to OUTPUT_DIR
    moved_count = 0
    for root, dirs, files in os.walk(OUTPUT_DIR):
        root_path = Path(root)
        if root_path == OUTPUT_DIR:
            continue
            
        for file in files:
            if file.lower().endswith(".pdf"):
                src = root_path / file
                dest = OUTPUT_DIR / file
                
                # Handle collision before standardization if needed
                if dest.exists() and dest != src:
                    base = dest.stem
                    dest = OUTPUT_DIR / f"{base}_sub.pdf"
                    
                shutil.move(str(src), str(dest))
                moved_count += 1
                print(f"Moved [{src.relative_to(OUTPUT_DIR)}] -> root output/")
                
    # Step 2: Remove empty subdirectories
    for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
        root_path = Path(root)
        if root_path != OUTPUT_DIR:
            try:
                root_path.rmdir()
                print(f"Removed empty directory: {root_path.relative_to(OUTPUT_DIR)}")
            except Exception:
                pass
                
    # Step 3: Standardize all PDF filenames in OUTPUT_DIR
    renamed_count = 0
    pdf_files = [f for f in OUTPUT_DIR.iterdir() if f.is_file() and f.name.lower().endswith(".pdf")]
    
    for f in pdf_files:
        old_name = f.name
        new_name = clean_and_standardize_filename(old_name)
        
        if old_name != new_name:
            new_path = OUTPUT_DIR / new_name
            # If target exists and is different file, resolve collision
            if new_path.exists() and new_path != f:
                stem = new_path.stem
                new_path = OUTPUT_DIR / f"{stem} (2).pdf"
                
            f.rename(new_path)
            renamed_count += 1
            print(f"Renamed: '{old_name}' -> '{new_path.name}'")
            
    print(f"\nCompleted! Moved {moved_count} file(s) to root, renamed {renamed_count} file(s).")
    print(f"Total PDFs in root output/: {len(list(OUTPUT_DIR.glob('*.pdf')))}")

if __name__ == "__main__":
    run()
