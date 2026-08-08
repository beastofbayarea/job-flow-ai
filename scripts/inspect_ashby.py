import urllib.request
import re
import json
import sys

urls = [
    ("Kraken", "Deal Lead, Corporate Development", "https://jobs.ashbyhq.com/kraken.com/37abda0c-ef4d-4bbe-9fb4-e6cb64c1acbe/application"),
    ("Coder", "Senior Product Manager", "https://jobs.ashbyhq.com/Coder/0dade34e-3141-4c69-bef8-7ebfdc72bf72/application"),
    ("OpenAI", "Product Manager, Codex Security Controls & Partner Interfaces", "https://jobs.ashbyhq.com/OpenAI/97681dd5-65ad-4eb5-b692-e6d192871c38/application"),
    ("Infisical", "Growth Marketing Manager", "https://jobs.ashbyhq.com/infisical/96f136de-3cab-4e38-942e-0f079f4b0e02/application"),
    ("Weave", "Senior Product Manager, Messaging", "https://jobs.ashbyhq.com/Weave/a0e04228-7490-4716-9a92-f637e2110f7c/application"),
    ("Qualified Health", "Product Strategy & Operations Lead", "https://jobs.ashbyhq.com/qualified-health-pbc/67e8e929-9506-423c-9462-28b766b18683/application"),
    ("Planera", "Sr Product Marketing Manager", "https://jobs.ashbyhq.com/planera/5e4c93db-3d84-4cf8-a914-8574499927e8/application"),
    ("HavocAI", "Technical Program Manager", "https://jobs.ashbyhq.com/havocai/d159a734-8200-8bfb-6df43f498e6f/application"),
    ("GoodParty.org", "Staff Product Manager", "https://jobs.ashbyhq.com/goodparty/e3a16838-9b9b-4318-893a-898b062f4c38/application"),
    ("Common Room", "Integrations Product Manager", "https://jobs.ashbyhq.com/commonroom/ff0cfae6-aeec-4fe1-8185-58ef7e1d8d7c/application"),
    ("Audiohook", "Product Marketing Manager", "https://jobs.ashbyhq.com/audiohook/5d8e16bb-6bc9-4294-9762-37419ad319fa/application"),
    ("Moonshot", "Lifecycle Marketing Manager", "https://jobs.ashbyhq.com/moonshot/37de5c6f-f600-49c9-a6f2-8ea03fd32955/application"),
    ("Linear", "Product Marketing Manager", "https://jobs.ashbyhq.com/Linear/b3346acf-44be-4565-b1c0-10d482d3ad4e/application"),
    ("Confluent", "Principal Product Manager", "https://jobs.ashbyhq.com/Confluent/f7356433-e9cd-437b-9048-587b11333bb1/application"),
    ("Yendo", "Principal Product Manager", "https://jobs.ashbyhq.com/yendo/44f1a080-2a6b-4843-aee4-dc30eb44b857/application"),
    ("Runway", "Product Lead, Self Serve", "https://jobs.ashbyhq.com/runway-ml/a010aa47-9150-4602-af69-f89f95186460/application"),
    ("Hims & Hers", "Lead Product Manager, Consumer Apps", "https://jobs.ashbyhq.com/hims-and-hers/e809a108-e72b-45c1-b2c4-aad645a00772/application"),
    ("Kestra", "Product Manager, AI", "https://jobs.ashbyhq.com/kestra/51b67438-6b1a-494a-acea-b3f25bc62070/application"),
    ("Tapcart", "Demand Gen Director", "https://jobs.ashbyhq.com/tapcart/a0c241a5-d1b4-421d-98a2-685497984662/application"),
    ("Airwallex", "Staff Product Manager, Lending", "https://jobs.ashbyhq.com/Airwallex/162fc14c-66ef-4eb6-8894-b1030f567ce5/application"),
    ("Virtuous", "Product Operations Manager", "https://jobs.ashbyhq.com/virtuous/08d80945-0a86-4078-8c38-18c3df00055b/application"),
]

def fetch_app_fields(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8')
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if m:
            data = json.loads(m.group(1))
            return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

if __name__ == "__main__":
    sample_data = fetch_app_fields(urls[0][2])
    print("Keys in pageProps:", sample_data['props']['pageProps'].keys() if sample_data and 'props' in sample_data else "None")
    # Write sample to json to examine structure
    with open("data/sample_ashby_app.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2)
    print("Saved sample to data/sample_ashby_app.json")
