# Job Search Prompt

Search this ATS platform for current, active openings matching the criteria below. Optimize for the maximum number of verified qualifying roles, not raw search-result volume.

ATS Platforms P0: Lever, Smart Recruiters, Greenhouse, Eightfold
ATS Platforms P1: Ashby, Workable, ICIMS, Workday

## Target roles

Search broadly across these job families and include adjacent titles when responsibilities strongly match.

**Product / Program**
Product Manager, Senior/Staff/Principal Product Manager, Technical Product Manager, AI Product Manager, Platform Product Manager, Product Lead, Product Owner, Program Manager, Technical Program Manager, Product Operations, Portfolio Manager.

**Product / GTM Marketing**
Product Marketing Manager/Lead/Director, GTM, Go-to-Market, Commercialization, Solutions Marketing, Technical Marketing, Developer Marketing, Commercial Strategy.

**Growth**
Growth Marketing/Lead, Performance Marketing, Acquisition, Digital Acquisition, Paid Media/Search/Social, Demand Generation, ABM, Lifecycle, CRM, Retention, Marketing Operations, Revenue Marketing, Digital Marketing, SEO, AEO, Website/Conversion, CRO, Partner/Alliance Marketing with GTM ownership.

**Investing / CorpDev**
Corporate Development, M&A, Strategic Finance, Venture Capital/Investing, Investment Associate, Private Equity, Growth Equity, Corporate Strategy, transaction-oriented Strategic Partnerships, Public Equities, Equity Research, Asset Management.

**Consulting / Transformation**
Management Consultant, Strategy Consultant, Engagement Manager, Principal Consultant, Transformation Consultant/Lead, Strategy & Operations, Commercial Strategy, Operating Model, Digital Transformation.

Also include adjacent titles such as **Solutions, Commercialization, Delivery Assurance, Transformation, Partnerships, or Alliances** when duties materially match these functions.

## Search method

Use a **two-pass process**:
1. **Discovery:** Maximize recall using separate searches across target functions, geographies, synonyms, and adjacent titles.
2. **Verification:** Apply every hard filter below before inclusion.

Prioritize **recall during discovery and precision during verification**, with zero tolerance for mandatory filters. Continue expanding query combinations until several consecutive searches produce no materially new qualifying employers. Continue discovery until 3 consecutive query batches yield zero new qualifying companies.

## Freshness

Use a **rolling 14-day window ending today** and state the exact start and end dates.

Each role must be both:
* **Currently active and accepting applications**
* **Posted or credibly republished within the last 14 days**

For every retained role, establish the latest publication date as **YYYY-MM-DD** using:
1. Employer/ATS exact posting date
2. Employer-controlled structured metadata
3. Reputable role-specific third-party date
4. Credible relative-date conversion

A live page alone is not evidence of freshness. If an older requisition was recently republished, it will qualify.

Sort results **newest to oldest by Posting Date**.

## Geography

**Priority 1**
France; USA remote; Noida, India; Oxford, UK; Cyprus.

**Priority 2**
Hong Kong; UAE; Saudi Arabia; UK; Ireland; Netherlands; Luxembourg; Singapore; New Zealand; Australia; Switzerland; USA (any).

Exclude roles requiring spoken proficiency in any language other than English. Exclude if the JD requires any non-English language.

## Hard exclusions

Exclude:
* Defense, healthcare, pharma, oil & gas, and mining companies or roles
* Roles requiring security clearance
* Internships, talent pools, and very junior roles
* Contract, contractor, fixed-term, temporary, or freelance roles
* Jobgether, Palantir, SpaceX, Blue Origin, Shield AI, and Anduril Industries

## Output

Include only **direct-employer, individual requisitions** where the named company is clearly the employer. Reject recruitment/staffing agencies, aggregators, employer-of-record boards, anonymous-client/intermediary listings, generic career-board URLs, and archived, expired, closed, removed, or 404 postings.

Retain at most **3 strongest and meaningfully diverse roles per company**, after validation.

Link directly to the **specific posting**. After validation, canonicalize URLs by removing `/apply` where appropriate, fragments, and tracking parameters such as `utm_*`, `lever-source`, `source`, `ref`, and `gh_src`. Preserve `gh_jid` only when required. Never invent or reconstruct a posting ID.

Return exactly these five columns:
| Posting Date | Company | Title | Location | URL |


## Lever rules

Search only jobs.lever.co and jobs.eu.lever.co.
Verify every candidate through its matching individual Lever API endpoint. Require HTTP 200 and an identical posting ID.
Use canonical URLs in the form https://jobs.lever.co/{board}/{posting-id} or the EU equivalent. Remove /apply, fragments, and all query parameters; this overrides the gh_jid exception in T3.
Include a multi-location posting only when its official Lever locations contain at least one T2-allowed location. Treat US remote as a remote workplace with a US or United States official location.
Use the Lever posting itself as the primary source of truth.

## SmartRecruiters rules

Use the SmartRecruiters canonical URL only. Prefer https://jobs.smartrecruiters.com/<Company>/<posting-id>-<slug> and remove all query parameters.
Deduplicate by SmartRecruiters posting ID first, then by company + normalized title. A repost with a new posting ID should replace an older posting if it is clearly the same job.
Search company career pages as well as generic SmartRecruiters results. Some roles are poorly indexed in external search.

## Eightfold rules

Search employer Eightfold domains directly: Use known *.eightfold.ai, apply.*, and employer careers domains in addition to search engines.
Search both `*.eightfold.ai/careers/job/*` **and employer-branded Eightfold domains** such as `apply.<company>.com/careers/job/*`; do not restrict discovery to `eightfold.ai`.
Eightfold individual requisitions generally follow `/careers/job/<JOB_ID>`; use this URL pattern aggressively in search queries.
When an Eightfold page does not expose a posting date, search the **exact title + exact Eightfold job ID** across the web to recover the most recent defensible date.

## Ashby rules

Explicitly search Ashby boards/API by employer and title synonyms, not just indexed search-engine results.
Every retained role must be verified via Ashby posting/API; discovery sources cannot establish inclusion.
Require isListed=true, full-time/permanent, and accessible canonical posting.

## Workable rules

Include a role only if the individual Workable requisition is live and currently accepting applications at verification time.
Deduplicate first by Workable requisition ID, then by normalized company + title; retain the newest valid repost.

## Workday rules

If no exact employer-controlled posting date exists, estimate from the employer’s Workday relative-age text (“Posted X Days Ago”) using the search date; prefix estimated dates with `~` and exclude if the estimate could fall outside the window.
Search local-language title variants and local Workday sites, especially for France, Switzerland, Luxembourg, Netherlands, Hong Kong, and Singapore. Treat country-wide remote roles as eligible when the posting explicitly permits employment from a target geography.
Deduplicate using Workday requisition ID, not title or URL, before applying the 3-role-per-company cap.

## iCIMS rules

For every identified iCIMS employer tenant, search its native `/jobs/search` endpoint directly and **sort by iCIMS `PostedDateTime`**, e.g. `?mode=redo&o=A&schemaId=$T{Job}.$T{JobPost}.$F{PostedDateTime}`. This often exposes posting chronology that individual `/jobs/{id}/.../job` pages hide.
Paginate the employer’s iCIMS search results (`pr=0`, `pr=1`, etc.) and search tenant-by-tenant rather than relying primarily on Google/Bing `site:icims.com` queries.
Use the individual requisition page for **live/application validation**, but use the tenant’s chronological `/jobs/search` results as an additional iCIMS-native source for determining posting freshness.
