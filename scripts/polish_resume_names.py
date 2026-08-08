import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path(r"C:\Users\Nagarro\Downloads\job-flow-ai\output")

REPLACEMENTS = {
    "FINTECH": "FinTech",
    "EDTECH": "EdTech",
    "E - Commerce": "E-Commerce",
    "E - commerce": "E-Commerce",
    "Forward - Deployed": "Forward-Deployed",
    "Science - Based": "Science-Based",
    "Us.pdf": "US.pdf",
    " Us.pdf": " US.pdf",
    " Pr ": " PR ",
    " Genai ": " GenAI ",
    " AI & EDTECH ": " AI & EdTech ",
    " Ex - Mbb ": " Ex-MBB ",
    "Openai": "OpenAI",
    "Goodparty": "GoodParty",
    "Helpscout": "HelpScout",
    "Revenuecat": "RevenueCat",
    "Netboxlabs": "NetBox Labs",
    "Nobleai": "NobleAI",
    "Okx": "OKX",
    "Sewerai": "SewerAI",
    "Sandboxaq": "SandboxAQ",
    "Surveymonkey": "SurveyMonkey",
    "Meridianlink": "MeridianLink",
    "Mongodb": "MongoDB",
    "Jazzx": "JazzX",
    "Elevenlabs": "ElevenLabs",
    "Havocai": "HavocAI",
    "Runway Ml": "Runway ML"
}

def run():
    files = list(OUTPUT_DIR.glob("*.pdf"))
    count = 0
    for f in files:
        name = f.name
        new_name = name
        for k, v in REPLACEMENTS.items():
            new_name = new_name.replace(k, v)
            
        if new_name != name:
            target = OUTPUT_DIR / new_name
            if target.exists() and target != f:
                target = OUTPUT_DIR / f"{Path(new_name).stem} (2).pdf"
            f.rename(target)
            count += 1
            print(f"Polished: '{name}' -> '{target.name}'")
            
    print(f"\nPolished {count} resume filename(s)!")

if __name__ == "__main__":
    run()
