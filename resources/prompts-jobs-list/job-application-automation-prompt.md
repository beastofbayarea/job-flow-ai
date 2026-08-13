# Local Browser Prompt

Run locally/cloud parallel sub-agents, one job/tab each. Leave completed tabs open and continue until the queue is exhausted. Reuse one Chrome debug/cloud browser session, open tabs in the background, skip submitted roles, and never click Submit. On errors/timeouts, clean up only the affected helper; never kill Chrome or close unrelated tabs.

# Answer Generation

Open every URL below in a separate tab and process all live job applications. Close closed or ineligible roles and continue.

For every application: Select and upload the most appropriate attached resume PDF. Use that resume’s email address. Resolve validation errors and verify the correct resume remains attached. Upload the actual PDF in the Resume/CV field. Do not paste resume text into a text field. If the ATS platform creates more than one resume area, ensure the role-specific PDF is attached in the final application section.

Inspect the entire application for required, optional, conditional, hidden, dependent, and validation-sensitive fields. Complete every field that can be answered from the supplied files, including:
   - Contact information
   - Current location and company
   - Work authorization (Yes for all) and sponsorship (Not required for all)
   - Eligibility (Yes for all)
   - Availability and notice period
   - Years and types of experience
   - Salary and compensation (Add the expected salary answer for each role, if not in JD, make best assumption. Match salary expectations to the role’s location, currency, and stated range.)
   - Portfolio and profile links
   - Referral and source
   - Motivation and company-interest questions
   - Screening questions
   - Consents and acknowledgments (Yes for all)
   - Voluntary demographic questions
   
Do not use placeholder language such as “verify,” “claim,” “confidence,” “TBD,” or “to be confirmed.” You have my complete permissions to proceed with all actions.

# Standard candidate details
- Name: Shivam Singh
- Current company: Amazon Web Services
- LinkedIn: [https://linkedin.com/in/beastofbayarea](https://linkedin.com/in/beastofbayarea)
- GitHub: https://github.com/beastofbayarea
- Other website: [https://goodreads.com/beastofbayarea](https://goodreads.com/beastofbayarea)
- US/international phone: +1 202-630-3211
- India phone: +91-9910865758
- India location: Noida, Uttar Pradesh, India
- Default US location when appropriate: San Francisco, California, United States

# Cover letters

Write a short, role-specific cover letter only when requested. Use readable line breaks:
- Greeting
- Brief role/company motivation
- Two concise evidence-based paragraphs
- Short closing
Do not submit a generic repeated letter. If a required cover-letter upload cannot accept text, create or use a clean PDF.

# Lever, Ashby and GreenHouse ATS Location-picker issue

“Current location” field is an autocomplete control. Typing text alone may leave it invalid. For each location field:
1. Type the full location.
2. Wait for the suggestion list.
3. Select the matching suggestion.
4. Confirm the field is no longer invalid before proceeding.

# Compatibility
Headless: Greenhouse, Smart Recruiters
Cloud Browser: Lever (manual Captach required)
Incompatible: Ashby, Workable

To Test: ICIMS, Workday, Eightfold

# Spam Prevention // TODO

Enforce routing at the process or container level. Configure Chromium launch arguments such as --proxy-server to direct all HTTP and HTTPS traffic through external residential proxy endpoints. Alternatively, place the entire cloud container network interface behind a transparent routing gateway to ensure the source IP reflects a consumer ISP rather than a datacenter ASN. Deploy local TLS interception proxies on the host machine. Use the Chrome DevTools Protocol. Pass specific execution flags, such as --disable-blink-features=AutomationControlled, to strip standard automation identifiers. Use CDP commands like Page.addScriptToEvaluateOnNewDocument.

Cloud Browser Limitations: Operate the browser at the exposed interaction layer: open pages, click, type, inspect rendered state, take screenshots, and verify results. The managed interface does not provide control over the host, browser launch configuration, certificate store, network routing, or raw CDP connection.