import json
import re
import urllib.request
import urllib.parse
from pathlib import Path
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://localhost:9222"
RESUME_PATH = (ROOT / "data/resumes/resume-general.pdf").resolve()

# Complete Custom Answer Mapping per Company/Role
ANSWERS_MAP = {
    "kraken": {
        "Why are you interested in working at Kraken?": "Having evaluated and structured digital asset trading models and capital platforms at D. E. Shaw and McKinsey, I admire Kraken's uncompromising focus on security, client trust, and institutional liquidity. I want to leverage my experience in closing major mandates ($500M institutional mandate at D. E. Shaw; $50M capital redeployment thesis at Rakuten) to drive high-impact strategic M&A and venture partnerships as Kraken accelerates global crypto infrastructure expansion.",
        "Have you used a Kraken product in the last six months?": "Yes",
        "What is your favorite aspect of our platform?": "Deep order book liquidity, institutional-grade compliance standards, and seamless API infrastructure that bridge traditional capital markets with low-latency crypto execution.",
        "From which country will you work?": "United States",
        "Will you now or in the future need sponsorship to work in your location?": "No",
        "How many full acquisitions have you personally closed as the acquirer?": "5-10",
        "Are you comfortable performing independent financial modelling and valuation analyses — including DCF, comparable company analysis, and precedent transactions — without support from a dedicated modelling team?": "Yes, I do this independently and regularly"
    },
    "coder": {
        "How did you hear about this job?": "LinkedIn",
        "What interests you in Coder?": "As a CS graduate from IIT who built mission-critical low-latency developer platforms at D. E. Shaw (Rust, Flink, Kafka) and cloud developer tools at AWS and Microsoft, Coder’s vision for cloud development environments (CDEs) represents the future of developer speed and security. I want to bring my background scaling developer-facing infrastructure to expand Coder’s product footprint for global engineering teams.",
        "Will you now, or in the future, require visa sponsorship to work in the country that you are residing in?": "No"
    },
    "openai": {
        "When can you start a new role?": "2 weeks",
        "Are you authorized to work in the country where the job is located?": "Yes",
        "Will you now or in the future require sponsorship for employment visa status in this country?": "No",
        "Are you able to work from our US office three days per week?": "Yes",
        "Additional Information": "At AWS, I led product strategy and execution for an agentic GenAI copilot across 12 workstreams, implementing Amazon Bedrock Guardrails, human-in-the-loop controls, and compliance-as-code reference architectures for regulated banking partners. Prior to AWS, I led confidential computing and Azure AI content safety initiatives at Microsoft. Combining my IIT B.Tech in CSE with hands-on experience deploying AI safety, partner APIs, and enterprise governance, I am eager to advance Codex security controls and enterprise partner interfaces at OpenAI."
    },
    "infisical": {
        "Are you currently located in the US?": "Yes",
        "Please add up to three bullets showing exceptional ability": "• GTM & Pipeline Engine: Built a $12M partner marketing engine at Microsoft using Random Forest propensity scoring and budget traffic-shaping; drove $50M incremental GMV at 4.1x ROI and raised partner conversion 5% -> 24%.\n• Regulated & Enterprise GTM Growth: Architected sovereign-cloud GTM at AWS, translating security/compliance into compliance-as-code reference architectures; unlocked $20M+ commitments, built $122M pipeline, and reduced deployment time from 6 months to 2 hours.\n• Growth & Cohort Analytics: Stress-tested DTC expansion with 10,000 Monte Carlo iterations at Rakuten; executed pivot to B2B2C model that boosted LTV:CAC from 0.8 to 4.5, D30 retention from 34% to 67%, and cut CAC from $42 to $8.50.",
        "How did you hear about us?": "LinkedIn"
    },
    "weave": {
        "How many years of experience do you have in product management?": "10+ years",
        "Have you directly owned a customer-facing messaging, notifications, inbox, or communications product?": "Yes",
        "Approximately how many active users interacted with your primary product?": "More than 1 Million",
        "Will you now or in the future require visa sponsorship (e.g., H-1B visa)?": "No",
        "Are you legally authorized to work in the United States and able to provide valid documentation to complete the Form I-9 employment verification process?": "Yes"
    },
    "qualified": {
        "Are you legally authroized to work in the United States?": "Yes",
        "Will you now or in the future require employer sponsorship to work in the United States?": "No",
        "Are you comfortable traveling to client sites as part of this role?": "Yes"
    },
    "goodparty": {
        "In 300 characters or less, please introduce yourself!": "Product leader with an IIT CS degree & Ross MBA. At AWS, I led agentic AI solutions used by millions; at D. E. Shaw & McKinsey, I scaled data platforms. Passionate about applying AI to democratize civic access and voter empowerment.",
        "Why are you interested in GoodParty.org?": "GoodParty.org’s mission to end political duopoly by empowering independent candidates through technology resonates deeply with me. I want to apply my product strategy and AI engineering background to build tools that equalize campaign access and activate grassroots movements.",
        "How frequently do you use AI tools or techniques in your work?": "Daily",
        "Describe a problem you solved using AI. What was the challenge, how did you approach it, what tool(s) did you use, and what outcome did you achieve?": "Challenge: High hallucination rates (8%+) and slow session depth in conversational shopping assistant across 12 workstreams at AWS.\nApproach: Fine-tuned prompt chains on Amazon Bedrock, integrated RAG over catalog embeddings, deployed Bedrock Guardrails, and introduced human-in-the-loop evaluation loops.\nOutcome: Reduced hallucinations to 2.8%, increased adoption by 25%, achieved 70% brand favorability, and expanded session depth by +15%."
    },
    "audiohook": {
        "Tell us about a specific time you improved customer activation or time-to-value. What signals told you there was a problem, what did you ship, and what was the actual measured result?": "At AWS, enterprise banking partners faced 6-month deployment cycles for regulated cloud services due to complex security and compliance reviews. I translated regulatory constraints into pre-packaged compliance-as-code reference architectures and localized GTM toolkits. This reduced partner deployment speed-to-value from 6 months to under 2 hours, unlocked $20M+ immediate commitments, and built a $122M GTM pipeline.",
        "Describe a positioning or messaging shift you led. What was the old narrative, what made you reposition, and how did you validate the new direction with customers and the sales team?": "At Rakuten, our consumer DTC app faced high CAC ($42) and poor D30 retention (34%). Through cohort economics and Monte Carlo analysis, I shifted our positioning from a burn-heavy B2C super-app to a B2B2C corporate partnership platform. By re-framing the value proposition around enterprise partner rewards and cross-border settlement, we improved LTV:CAC from 0.8 to 4.5, boosted D30 retention to 67%, and cut CAC to $8.50.",
        "Walk us through a product launch you owned end-to-end. What is the single decision you're least proud of in hindsight, and what would you do differently?": "Launching AWS's GenAI shopping copilot, I initially prioritized broad model choices across multiple foundational models over strict guardrail testing to meet an aggressive holiday milestone. In hindsight, early hallucination spikes required reactive guardrail tuning post-launch. What I would do differently is mandate automated Bedrock Guardrails and benchmark evals as blocking launch gates prior to customer preview.",
        "Tell us about a time customer or win/loss research changed your mind about something — positioning, a feature, a segment, anything. What did you hear, and what did you do about it?": "At McKinsey during an APAC financial platform modernization, initial feedback suggested client CFOs prioritized raw transaction speed. However, win/loss interviews with compliance officers revealed that regulatory localization (Vietnam Decree 53 & Indonesia OJK constraints) was the true deal blocker. We pivoted product strategy to lead with automated regulatory compliance modules, which unlocked a $1.1B APAC market expansion.",
        "How do you use AI tools in your product marketing work today? Give us a specific example where AI changed your output — and a specific example where it produced something you had to throw out or significantly rework.": "Output Transformed: I use Claude/Gemini to run synthetic messaging tests across customer ICP buyer personas (e.g., contrasting CFO risk focus vs. CTO API integration speed), compressing messaging validation from 3 weeks to 2 days.\nOutput Reworked: AI-generated competitive matrix summaries often produce generic surface-level comparisons without capturing technical moat nuances (e.g., confusing basic TLS encryption with Azure Confidential Computing enclave latencies). I threw out the LLM draft and rebuilt the technical teardown manually.",
        "Please share your desired salary:": "$120,000–$160,000"
    },
    "moonshot": {
        "Why Moonshot?": "Moonshot is pioneering next-generation global financial rails. Having managed capital efficiency, liquidity flywheels, and payment infrastructure at D. E. Shaw, Rakuten, and AWS, I am excited to apply data-driven lifecycle marketing and retention loops to accelerate user adoption for Moonshot.",
        "What is your experience working at a startup?": "6+ years of agile startup and high-growth scale-up experience. At Rakuten, I operated with lean startup autonomy to pivot portfolio strategy from DTC burn to B2B2C growth; at AWS and Microsoft, I led incubator 0-to-1 product pods operating like internal startups.",
        "Do you require work authorization to work in the USA or Canada — now or in the future?": "No"
    },
    "linear": {
        "Cover letter": "Linear has set the gold standard for software craft, execution speed, and product design. As a Computer Science engineer (IIT) turned tech product manager (AWS, D. E. Shaw, McKinsey), I admire Linear’s obsession with focus and quality. I want to bring my experience positioning complex technical products and building developer momentum to help Linear craft narrative-driven product launches that resonate with modern software teams worldwide.",
        "Share an example of writing that reflects your product marketing taste.": "Product Launch Positioning: Pivoting Enterprise Cloud Security from Hype to Code\nAudience: Enterprise CISOs, Cloud Architects, and Engineering Directors.\nProduct Truth: Enterprise security teams don't want generic 'bank-grade security' marketing claims; they need zero-trust isolation and deterministic compliance proofs.\nRevision / Refinement: Replaced boilerplate messaging with technical precision: 'Azure Confidential Computing cuts cryptographic memory overhead while guaranteeing enclave isolation down to 220ms latency.' This shifted narrative from fear-based risk avoidance to competitive speed advantage.",
        "Tell us about a technically complex product or feature you helped bring to market.": "At D. E. Shaw, I led the launch of a ~$10M real-time risk platform using Rust, Apache Kafka, Apache Flink, and FPGA hardware acceleration under Basel III constraints. I became fluent by working embedded alongside quant traders and low-latency systems engineers, identifying that packet-drop bottlenecks during high-volatility events were the primary user pain. I shaped the narrative around zero-dropped-packets under market crash conditions, reducing risk latency from 90ms to 4.2ms and unlocking $85M in regulatory capital."
    },
    "confluent": {
        "Current Company": "Amazon Web Services",
        "Are you legally authorized to work in the United States?": "Yes",
        "Do you now, or will you in the future, require sponsorship for employment visa status in the United States?": "No",
        "LinkedIn Profile URL": "https://linkedin.com/in/beastofbayarea",
        "GitHub Profile URL": "https://github.com/beastofbayarea",
        "Portfolio URL": "https://www.researchgate.net/profile/Shivam-Singh-188"
    },
    "runway": {
        "If located in the US, are you currently authorized to work in the US?": "Yes",
        "So we can pronounce it correctly, what is the phonetic spelling of your name? (e.g. Kristina would be chris-teen-uh)": "Shih-vum Sing",
        "What are your preferred pronouns?": "they/them",
        "Linkedin Profile": "https://linkedin.com/in/beastofbayarea"
    },
    "hims": {
        "Do you have at least 3 years of experience owning consumer mobile products at meaningful scale? If so, please provide how many total years you have of this experience, and at what companies.": "Yes, 8+ years of total experience across Amazon Web Services and Rakuten International. At AWS, I led the strategy and deployment of an agentic GenAI mobile shopping copilot reaching millions of active users, scaling user adoption by 25% and driving +15% session depth. At Rakuten, I managed consumer engagement and cross-border digital app models, utilizing cohort analytics and A/B testing to double D30 user retention from 34% to 67%.",
        "Are you legally authorized to work in the U.S. without restriction for any employer?": "Yes",
        "Will you now or in the future require immigration sponsorship by Hims & Hers in order to work for Hims & Hers in the U.S.?": "No",
        "Have you previously worked for hims & hers as an employee or contractor/consultant?": "No"
    },
    "tapcart": {
        "In 3-5 sentences, walk us through a demand gen program you built or owned. What was the channel mix, what did it produce in pipeline, and what would you do differently?": "At Microsoft, I designed and owned a $12M partner marketing and demand generation engine leveraging Random Forest propensity models and live budget traffic-shaping across co-sell channels. The program generated $50M in incremental pipeline/GMV at a 4.1x ROI, raising funded-partner conversion from 5% to 24% and shortening sales cycles to 85 days. In hindsight, I would have integrated real-time partner API feedback loops earlier to eliminate manual MDF allocation approvals.",
        "Describe a workflow or system you've built using AI tools. What problem did it solve, what tools did you use, and how did it actually work?": "I built an automated lead enrichment and intent-scoring agent pipeline using LangChain, OpenAI/Bedrock APIs, and vector databases. The system ingested target account website updates, hiring signals, and tech stack telemetry, automatically tagging high-intent leads and generating tailored email opener copy for sales reps. This reduced manual SDR research time by 75% and increased cold outbound response rates by 2.4x.",
        "Are you legally authorized to work in the United States?": "Yes"
    },
    "airwallex": {
        "Salary Expectations": "$120,000–$160,000 USD",
        "What is your notice period?": "2 weeks",
        "Where did you find this job posting?": "LinkedIn",
        "Please share the GPA you graduated your Bachelors Degree with.": "First Class Honors (3.8 equivalent, B.Tech CSE at IIT)",
        "At Airwallex, we recognize the benefits AI brings to professional environments... Please indicate your understanding and agreement with this approach by selecting 'Yes' below.": "Yes"
    },
    "virtuous": {
        "What is your desired salary?": "$120,000–$160,000",
        "Are you ok working a hybrid work schedule (3 days in office)?": "Yes - Phoenix, AZ",
        "Will you now or in the future require sponsorship to work in the U.S.?": "No",
        "This role sits at the intersection of Support, CX, Product, and Engineering, turning raw customer signal into clear, actionable work. Tell us about a time you built structure or a process where none existed before, what was the starting point, and what did you build?": "At AWS, product feedback across 12 workstreams, engineering pods, and enterprise sales was highly fragmented. I built a unified Product Operations feedback ingestion system using automated tagging and severity triage rules. This created a single source of truth connecting customer friction signals directly to sprint backlogs, reducing release bug resolution time by 40% and aligning product roadmaps directly with ARR impact.",
        "Have you built or shipped AI-enabled workflows yourself (prompts, agents, tagging/clustering, etc.)? Walk us through a specific example, including what the workflow did and the impact it had.": "At AWS, I designed and deployed Bedrock Guardrails, automated evaluation pipelines, and human-in-the-loop tagging workflows for an agentic GenAI copilot. The workflow continuously evaluated model completions against brand safety and accuracy rubrics, auto-flagging hallucinated outputs for prompt re-tuning. This reduced hallucination rates from 8% to 2.8% and drove 70% brand favorability.",
        "Tell us about your experience working in a SaaS, multi-product environment, ideally including some startup exposure. How did you handle ambiguity or a lack of existing process in that setting?": "Across Microsoft, D. E. Shaw, and McKinsey, I have consistently thrived in ambiguous, multi-product SaaS ecosystem environments. At Microsoft, I managed partner co-sell programs spanning multiple Azure cloud products, establishing clear API governance and MDF metrics where processes were unstandardized. I handle ambiguity by breaking complex problems into hypothesis-driven experiments, validating early with data, and building lightweight repeatable frameworks."
    }
}

STANDARD_VALUES = {
    "name": "Shivam Singh",
    "first_name": "Shivam",
    "last_name": "Singh",
    "preferred_name": "Shiv",
    "email": "shiv-ai-pm@umich.edu",
    "phone": "6502833478",
    "location": "San Francisco, California, United States",
    "linkedin": "https://linkedin.com/in/beastofbayarea",
    "github": "https://github.com/beastofbayarea",
    "twitter": "https://x.com/BeastofBayArea",
    "portfolio": "https://www.researchgate.net/profile/Shivam-Singh-188"
}

def get_open_cdp_targets():
    req = urllib.request.Request(ENDPOINT + "/json/list")
    with urllib.request.urlopen(req) as resp:
        targets = json.load(resp)
    ashby_targets = []
    for t in targets:
        url = t.get("url", "")
        if "jobs.ashbyhq.com" in url:
            ashby_targets.append(t)
    return ashby_targets

def fill_cdp_target(target, custom_answers):
    ws_url = target["webSocketDebuggerUrl"]
    target_id = target["id"]
    title = target.get("title", "")
    url = target.get("url", "")
    
    print(f"Connecting to tab: {title} ({target_id})...")
    ws = connect(ws_url, open_timeout=5, close_timeout=1)
    
    def call(method, params=None):
        nonlocal ws
        msg_id = 1
        ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        return json.loads(ws.recv(timeout=5)).get("result", {})

    call("Runtime.enable")
    call("Page.enable")
    call("DOM.enable")
    
    payload = json.dumps({"values": STANDARD_VALUES, "answers": custom_answers})
    
    fill_script = """
    ((payload) => {
        const normalize = value => (value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
        const setValue = (element, value) => {
            const descriptor = Object.getOwnPropertyDescriptor(
                Object.getPrototypeOf(element), 'value'
            );
            if (descriptor && descriptor.set) descriptor.set.call(element, value);
            else element.value = value;
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
        };
        
        const answers = new Map(Object.entries(payload.answers).map(([k, v]) => [normalize(k), v]));
        const aliases = [
            [['name', 'full name', 'your name', 'legal name', 'preferred full name', 'legal full name'], payload.values.name],
            [['first name'], payload.values.first_name],
            [['last name', 'last name / surname', 'surname'], payload.values.last_name],
            [['preferred name'], payload.values.preferred_name],
            [['email', 'email address'], payload.values.email],
            [['phone', 'phone number', 'mobile phone', 'mobile'], payload.values.phone],
            [['location', 'current location', 'city', 'country', 'where are you located?', 'location - city, state', 'location - zip code'], payload.values.location],
            [['linkedin', 'linkedin profile', 'linkedin url', 'linkedin link'], payload.values.linkedin],
            [['github', 'github profile url', 'website / portfolio / github url', 'links to your github, portfolio, website, linkedin, etc.'], payload.values.github],
            [['twitter', 'twitter handle', 'x profile'], payload.values.twitter],
            [['salary expectations', 'what is your desired salary?', 'desired salary', 'please share your desired salary:'], '$120,000–$160,000'],
            [['what is your notice period?', 'notice period'], '2 weeks']
        ];
        
        const filled = {};
        
        // 1. Text & Textarea inputs
        for (const container of document.querySelectorAll(
            '.ashby-application-form-field-entry, fieldset, [role="group"], div[class*="_formField_"]'
        )) {
            const heading = container.querySelector(
                '.ashby-application-form-question-title, label, legend, h3, p'
            );
            const label = (heading?.textContent || container.innerText?.split('\\n')[0] || '').trim();
            const key = normalize(label);
            
            const control = container.querySelector(
                'input:not([type=file]):not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea'
            );
            if (!control || control.disabled || control.readOnly) continue;
            
            let val = answers.get(key);
            if (!val) {
                for (const [keyWords, cand] of aliases) {
                    if (cand && keyWords.some(kw => key === kw || key.includes(kw))) {
                        val = cand;
                        break;
                    }
                }
            }
            
            if (val) {
                setValue(control, val);
                filled[label] = control.value;
            }
        }
        
        // 2. Radio, Checkbox, Dropdowns
        for (const container of document.querySelectorAll(
            '.ashby-application-form-field-entry, fieldset, [role="group"], div[class*="_formField_"]'
        )) {
            const heading = container.querySelector(
                '.ashby-application-form-question-title, label, legend, h3, p'
            );
            const label = (heading?.textContent || container.innerText?.split('\\n')[0] || '').trim();
            const key = normalize(label);
            const answer = answers.get(key);
            
            if (answer) {
                const wanted = normalize(answer);
                const options = [...container.querySelectorAll(
                    'label, button, [role="option"], [role="radio"], [role="checkbox"], input[type="radio"], input[type="checkbox"]'
                )];
                const option = options.find(el => normalize(el.textContent).includes(wanted) || normalize(el.value) === wanted);
                if (option) {
                    option.click();
                    filled[label] = answer;
                }
            }
        }
        
        return filled;
    })(""" + payload + ")"
    
    ws.send(json.dumps({
        "id": 2,
        "method": "Runtime.evaluate",
        "params": {"expression": fill_script, "returnByValue": True, "awaitPromise": True}
    }))
    res = json.loads(ws.recv(timeout=5))
    filled_summary = res.get("result", {}).get("result", {}).get("value", {})
    print(f"Filled in {title}: {len(filled_summary)} fields!")

    # Attach file if missing
    try:
        document = call("DOM.getDocument", {"depth": -1, "pierce": True})
        root_id = document["root"]["nodeId"]
        query_res = call("DOM.querySelector", {"nodeId": root_id, "selector": "input[type=file]"})
        node_id = query_res.get("nodeId")
        if node_id:
            call("DOM.setFileInputFiles", {"files": [str(RESUME_PATH)], "nodeId": node_id})
            print(f"Attached resume to {title}")
    except Exception as e:
        print("Resume attach note:", e)
        
    ws.close()

def main():
    targets = get_open_cdp_targets()
    print(f"Found {len(targets)} open Ashby tabs in Chrome.")
    
    for t in targets:
        url = t.get("url", "").lower()
        title = t.get("title", "").lower()
        
        # Match company
        matched_answers = {}
        for comp_key, ans in ANSWERS_MAP.items():
            if comp_key in url or comp_key in title:
                matched_answers = ans
                break
                
        fill_cdp_target(t, matched_answers)

if __name__ == "__main__":
    main()
