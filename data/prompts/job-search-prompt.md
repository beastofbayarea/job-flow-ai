# Job Search Prompt

## T1. Roles and recency

Search for current openings on this ATS platform in these job groups:

- Product and Program Management: roles building or steering the roadmap, technical, or AI-focused.
- Marketing: Growth, Performance, Paid Media, Marketing Operations, Demand Generation, Product Marketing, and GTM Marketing.
- VC and Corporate Development.
- Management Consulting.

Replace any role more than 2 weeks old with a more recent relevant role from that company.

## T2. Location and company exclusions

Include only roles based in France, US remote, Hong Kong, UAE (including Abu Dhabi), or Noida, India.

Exclude roles in defense, healthcare, pharma, oil and gas, or mining, and any role requiring a security clearance.

Skip these companies: Jobgether, Palantir, SpaceX, Blue Origin, Shield AI, and Anduril Industries.

## T3. Output format and URLs

Use this five-column format: Posting Date, Company, Title, Location, URL.

- Link directly to the specific posting, never a generic job board.
- Remove all query parameters, including UTM, gh_src, referrals, and error parameters, but retain gh_jid if present.
- Add as many qualifying roles as possible.

## T4. Selection rules

- Retain at most 3 best-fit, diverse roles per company.
- Include only active, individual postings.
- Exclude expired roles, talent pools, internships, and roles with a very low seniority level.
- Exclude contract, contractor, fixed-term, temporary, and freelance roles.
- Include only postings controlled by an identifiable end employer; exclude recruitment agencies, aggregators, employer-of-record boards, and anonymous-client listings.
- Apply the three-role limit to the actual hiring employer, not the board token or a subsidiary name.
- Find each role's latest published or reposted date, searching again when it is missing, and sort newest to oldest by Posting Date.

## T5. Lever-specific rules

- Search only jobs.lever.co and jobs.eu.lever.co.
- Verify every candidate through its matching individual Lever API endpoint. Require HTTP 200 and an identical posting ID.
- Use createdAt as the authoritative posting date. Use the posting page's JSON-LD datePosted only when createdAt is unavailable; never use a search-engine crawl date.
- Use canonical URLs in the form https://jobs.lever.co/{board}/{posting-id} or the EU equivalent. Remove /apply, fragments, and all query parameters; this overrides the gh_jid exception in T3.
- Include a multi-location posting only when its official Lever locations contain at least one T2-allowed location.
- Treat US remote as a remote workplace with a US or United States official location.
