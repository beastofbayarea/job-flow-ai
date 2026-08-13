# Candidate Profile Configuration

**Refactor notes**

- Source values are preserved; this file changes organization and presentation, not meaning.
- Canonical candidate information appears before application-policy defaults.
- Matcher rules are grouped by function instead of kept as one long flat map.

**Skipped application-question topics**

- internal mobility
- internal candidate
- internal transfer
- high school performance
- mathematics at high school
- native language at high school
- security clearance

## 2. Candidate Profile

### Identity

| Field | Value |
|---|---|
| `first_name` | Shivam |
| `middle_name` |  |
| `last_name` | Singh |
| `preferred_name` | Shiv |
| `phonetic_name` | Shih-vum Sing |

### Current Employment

| Field | Value |
|---|---|
| `current_company` | Amazon Web Services |
| `current_job_title` | Principal, Generative AI |
| `currently_employed` | Yes |
| `start_month` | June |
| `start_year` | 2022 |
| `end_month` | Present |
| `end_year` | Present |

### Contact & Public Profiles

| Field | Value |
|---|---|
| `fallback_email` | shiv-ai-pm@umich.edu |
| `phone` | 6502833478 |
| `portfolio` | https://www.researchgate.net/profile/Shivam-Singh-188; https://goodreads.com/beastofbayarea; https://github.com/beastofbayarea |
| `publications` | https://www.researchgate.net/profile/Shivam-Singh-188 |
| `linkedin` | https://linkedin.com/in/beastofbayarea |
| `twitter` | https://x.com/BeastofBayArea |
| `goodreads_book` | https://www.goodreads.com/book/show/60591386-in-crypto-we-trust |
| `researchgate` | https://www.researchgate.net/profile/Shivam-Singh-188 |
| `sciencedirect` | https://www.sciencedirect.com/science/article/abs/pii/S0959652623023867 |
| `website` | https://goodreads.com/beastofbayarea |
| `github` | https://github.com/beastofbayarea |

### Availability & Compensation

| Field | Value |
|---|---|
| `pronouns` | they/them |
| `lgbtq` | Yes |
| `birthday` | 1995-11-27 |
| `start_date_offset_days` | 14 |
| `available_start_date` | 2 weeks |

### Address

| Field | Value |
|---|---|
| `location` | San Francisco, California, United States |
| `street_address` | 447 Sutter Street |
| `address_2` | ste 506 |
| `city` | San Francisco |
| `state` | California |
| `zip_code` | 94108 |
| `country` | United States |

### Education

**Highest degree:** Master's Degree

#### Education Record 1

| Field | Value |
|---|---|
| `school` | University of Michigan |
| `degree` | MBA |
| `field_of_study` | Business |
| `start_month` | August |
| `start_year` | 2022 |
| `end_month` | May |
| `end_year` | 2024 |
| `still_student` | false |

### Demographics & Languages

| Field | Value |
|---|---|
| `country_of_birth` | India |
| `nationality` | Indian |
| `citizenship` | Indian |
| `gender` | Man |
| `race` | South Asian |
| `age` | 30-39 |
| `veteran` | I am not a protected veteran |
| `transgender` | No |
| `orientation` | Bisexual |
| `disability` | Yes |

**Languages**

- English
- French
- Hindi

**Communities**

- Person with disability
- Neurodiverse

## 3. Application Policy & Answer Defaults

### Explicit Prompt Answers

Exact or near-exact prompt-to-answer mappings used for recurring application questions.

| Prompt / Key | Answer |
|---|---|
| availability to join us | 2 weeks |
| if you answered yes to the reasonable adjustments question | N/A |
| non-disclosure agreement | I Agree |
| phonetic spelling | Shih-vum Sing |
| email me about future job openings | Yes |
| reasonable adjustments | No |
| have you built | Yes |
| have you partnered | Yes |
| have you led | Yes |
| have you previously worked at | No |
| where have you learned about | LinkedIn |
| notice period | 2 weeks |
| where are you currently employed | Amazon Web Services |
| where were you last employed | Amazon Web Services |
| current or most recent employer | Amazon Web Services |
| are you crypto-native | Yes |
| singapore/hong kong citizen, permanent resident | Yes |
| non-compete | No restrictions |
| how did you hear about | LinkedIn |
| how did you learn about | LinkedIn |
| work eligibility status | Eligible |
| status that allows you to work and live | Eligible |
| in what cities are you available to work | __FIRST_OPTION__ |
| uk right to work status | Yes |
| right to work in the uk | Yes |
| will you require relocation support | No |
| relocation assistance | No |
| additional countries of which you are a lawful permanent resident | USA |
| export controls | No |
| what country and time zone are you based in | USA, ET |
| experience with earnings call transcripts | Yes |
| financial content/data products | Yes |
| work for or with a dealer, partner or supplier | No |
| notice at collection for california job applicants | Acknowledge |
| self-identification data to be processed | Consent |
| legally eligible to work | Yes |
| ai policy for interviewers | Acknowledge |
| by submitting your application you confirm you've read our | Acknowledge / Confirm |
| by submitting your application you confirm you’ve read our | Acknowledge / Confirm |
| are you a us citizen | No |
| what is your work authorization | I am authorized to work in this country for any employer |
| do you reside within ny, nj, ct, md, va, pa, ma, ri or washington, dc | No |
| a final step in the hiring process is for you to arrange reference calls with former managers, direct reports (for managerial roles), and others | I acknowledge this. |
| i acknowledge that for remote-based us roles, depending upon where the remote work is performed, income could be subject to nys tax withholdings | Yes, I acknowledge this. |
| upon hire, can you provide verification of your identity and legal right to work | Yes |
| how frequently do you use ai tools or techniques in your work | Daily |
| are you based in a us or eu equivalent timezone | Yes |
| passport country | India |
| country of residence | United States |
| how many years of relevant experience do you have | 10 |
| where did you go to university | University of Michigan (Ross MBA) / Indian Institute of Technology (B.Tech CSE) |

### General Answer Defaults

Canonical fallback/default values used by application logic.

| Prompt / Key | Answer |
|---|---|
| visa_sponsorship | No |
| visa_type_not_applicable | N/A |
| permit_status | Yes |
| security_clearance | No |
| government_relationship | No |
| conflict_of_interest | No |
| outside_activities | No |
| hourly_rate | $50/hour |
| referral_default | N/A |
| consent_default | Yes |
| age_over_18 | Yes |
| background_check_consent | Yes |
| sms_consent | Yes |
| requires_accommodation | No |
| can_perform_essential_functions | Yes |
| previous_application | No |
| employee_relationship | No |
| right_to_work_status | No sponsorship required |
| bachelors_degree | Yes |
| salary_expectation | Negotiable |
| application_certification | Yes |
| target_country_work_authorization | Yes |
| target_country_residence | Yes |
| based_in_target_country | Yes |
| international_travel | Yes |
| led_product_implementation | Yes |
| regional_experience | Yes |
| work_authorization | Yes |
| employment_restrictions | No |
| previous_employment | No |
| are_you_comfortable_with | Yes |
| experience_level_selection | max_value |
| rating_selection | max_value |
| interest_checkbox_selection | all |
| source_channel | LinkedIn |
| relocation | Yes |
| relocation_support | No |
| additional_permanent_residencies | N/A |
| export_control_eligibility | No |
| work_country_timezone | USA, ET |
| city_availability_selection | first_option |
| financial_content_experience | Yes |
| current_salary | Prefer not to disclose |
| notice_period | 2 weeks |
| flexible | Yes |
| language_fluency | Yes |
| current_employee | No |
| privacy_consent | Acknowledge |
| experience_requirement | Yes |
| tool_proficiency | Yes |
| language_proficiency | C1–C2 or native (Advanced) |

**`work_authorization_countries`**

- Australia
- Belgium
- France
- India
- Ireland
- Italy
- Japan
- Luxembourg
- Malaysia
- New Zealand
- Portugal
- Singapore
- Spain
- Sweden
- Switzerland
- The Netherlands
- United Arab Emirates
- United Kingdom
- United States

**`language_answers`**

| Option | Value |
|---|---|
| Arabic | Yes |
| Bahasa Malaysia | No |
| Bengali | Yes |
| Cantonese | No |
| Czech | No |
| Dutch | No |
| English | Yes |
| French | Yes |
| German | No |
| Greek | No |
| Hebrew | No |
| Hindi | Yes |
| Hungarian | No |
| Indonesian | No |
| Italian | No |
| Japanese | Yes |
| Korean | No |
| Mandarin Chinese | No |
| Norwegian | No |
| Other | No |
| Persian (Farsi) | Yes |
| Polish | No |
| Portuguese | No |
| Romanian | No |
| Russian | No |
| Spanish | Yes |
| Swedish | No |
| Thai | No |
| Turkish | No |
| Ukrainian | No |
| Vietnamese | No |

### EEO Defaults

| Field | Value |
|---|---|
| `gender` | Man |
| `hispanic_latino` | No |
| `race` | South Asian |
| `veteran_status` | I am not a protected veteran |
| `disability_status` | Yes, I have a disability, or have a history/record of having a disability |
| `lgbtq_status` | Yes |
| `transgender_status` | No |

## 4. Matcher Rules

Matchers map normalized configuration fields to phrases that may appear in application forms.

### Identity & Personal Information

**`first_name`**

- first name
- given name

**`middle_name`**

- middle name
- middle initial

**`last_name`**

- last name
- preferred last name
- family name
- surname

**`preferred_name`**

- preferred name
- nickname
- alias

**`legal_name`**

- legal name
- full legal name

**`age_over_18`**

- 18+ years of age
- 18 years of age
- at least 18

**`phonetic_name`**

- phonetic spelling
- how do you pronounce

**`pronouns`**

- pronoun

### Contact & Online Profiles

**`email`**

- email
- email address

**`phone`**

- phone
- mobile
- contact number

**`linkedin`**

- linkedin
- linkedin profile
- linkedin url

**`portfolio`**

- portfolio
- website
- personal website

**`public_username`**

- public username

### Location & Geography

**`location`**

- location
- city
- cities are you available to work
- where are you based
- physically based
- current location

**`country`**

- country in which you are located
- country of residence
- what country are you based in
- currently located? please state the country
- currently located please state the country

**`country_of_birth`**

- country of birth
- birth country

**`zip_code`**

- zip code
- postal code

**`intended_work_location`**

- from where do you intend to work
- where do you intend to work

**`based_in_target_country`**

- currently based in
- based in
- currently located in

**`target_office`**

- which proton office
- which office are you applying

### Employment & Work History

**`current_company`**

- current company
- current employer
- most recent company
- current (or most recent) company

**`current_title`**

- current title
- current job title

**`previous_employment`**

- previously worked
- have you previously
- previously employed
- ever been employed
- currently work for
- currently employed by
- history with
- employed, or otherwise engaged
- consulted for

**`current_employee`**

- currently an employee
- current employee

**`employment_restrictions`**

- employment agreement
- post-employment restriction
- bound by any agreements
- restrict your ability to work

**`employee_relationship`**

- know anyone or are you related to anyone who works
- referred to this role by a current employee
- referred to this role by a current

### Work Authorization, Sponsorship & Compliance

**`citizenship`**

- citizenship
- citizen of

**`sponsorship`**

- sponsorship
- require sponsorship
- sponsor an immigration case
- immigration case
- visa sponsorship
- future sponsorship

**`right_to_work_status`**

- right to work status

**`work_auth`**

- authorized
- legally authorized
- legal authorization to work
- work in the united states
- work authorization
- currently eligible to work
- eligible to work in your country of residence

**`target_country_work_auth`**

- authorised to work in
- authorized to work in
- eligible to work in

**`sanctions_residency`**

- citizen or resident of any of the following countries
- cuba, iran, north korea, syria

**`government_entity_details`**

- list the u.s. government entity
- government entity you worked for

**`background_check_consent`**

- background check
- criminal history check

**`application_certification`**

- i certify that the information
- certify that the information
- information i provided in my employment application

**`interview_ai_policy`**

- ai policy for interviewers
- use of ai during the interview

**`privacy_consent`**

- rgpd
- gdpr
- privacy consent
- privacy
- processing of personal data
- personal information retained

### Availability, Mobility & Workplace

**`available_start_date`**

- available start date
- when can you start
- start date

**`international_travel`**

- willing and able to travel
- domestic and international sites
- international travel

**`comfortable`**

- comfortable
- are you comfortable
- open to working in person
- working in person
- onsite
- hybrid
- in-office
- offices 4 days per week
- office days per week
- days a week in our
- days a week in our office
- days a week in the office
- work is in office
- working from office
- work from office
- working in the office
- requires working from one of our offices
- requires working from our office
- come into the office
- commute to our office
- attend the office
- able to work from our office

**`relocation`**

- relocate
- relocating
- relocation

**`flexible`**

- are you flexible
- would you be flexible

**`notice_period`**

- notice period
- availability to start
- available to start

### Experience & Qualifications

**`api_product_experience`**

- experience building api products
- developer tools, or ai-powered products

**`led_product_implementation`**

- led the implementation of a technology
- led the implementation of a digital product
- implemented a technology or digital product

**`regional_experience`**

- worked in sub-saharan africa
- managed projects based there

**`management_experience_years`**

- years of product/project management experience
- years of product management experience
- years of project management experience

**`experience_requirement`**

- experience
- collaborat

**`tool_proficiency`**

- proficient
- proficiency
- familiar with
- tools
- technology

**`bachelors_degree`**

- bachelor's degree
- bachelors degree
- bachelor degree

**`degree`**

- degree
- highest level of education
- education level

### Compensation

**`salary_expectation`**

- desired base salary
- salary expectation
- salary expectations
- compensation expectation
- compensation expectations
- expected monthly base salary
- expected annual salary
- expected salary
- desired compensation

**`current_salary`**

- current salary
- current monthly salary
- current annual salary
- current monthly base salary
- current compensation

### Language

**`language_proficiency`**

- language proficiency
- language level
- fluency level

**`language_fluency`**

- fluent in
- speak french fluently
- language fluency

### Consent, Accommodation & Capability

**`sms_consent`**

- text message
- sms
- text updates

**`requires_accommodation`**

- require any accommodation
- require accommodations
- need any accommodation
- need accommodations
- request an accommodation

**`can_perform_essential_functions`**

- perform the essential functions
- perform essential functions
- perform the job duties with or without
- able to perform the job duties

### Application History & Source

**`previous_application`**

- have you applied
- previously applied
- applied before
- applied in the past

**`source`**

- how did you hear
- where have you learned about
- where did you first hear
- where did you see or hear
- source

### EEO / Self-Identification

**`hispanic_latino`**

- hispanic
- latino
- identify your ethnicity

**`gender`**

- gender
- identify your sex

**`race`**

- race
- racial
- ethnic

**`veteran`**

- veteran

**`disability`**

- disability

**`transgender`**

- transgender

**`orientation`**

- sexual orientation

### Other

**`human_attestation`**

- which of the following best describes you

## 5. Option Normalization

Acceptable form-option variants that normalize to a canonical configured value.

**Canonical:** `LinkedIn`

- University Career Fair

**Canonical:** `Man`

- Male

**Canonical:** `No`

- No, I have not
- Not Hispanic or Latino
- No proficiency
- None

**Canonical:** `South Asian`

- South Asian
- Asian (Not Hispanic or Latino)
- Asian

**Canonical:** `United States`

- United States of America
- USA
- US

**Canonical:** `Asian or Asian American`

- Asian

**Canonical:** `Yes, I have a disability, or have a history/record of having a disability`

- Yes, I have a disability, or have had one in the past
- Yes

**Canonical:** `I am not a protected veteran`

- not a protected veteran
- I am not a veteran
- No

**Canonical:** `Acknowledge`

- Yes
- Yes, I consent
- I consent
- I agree
- I acknowledge and give my consent
- J'en ai pris connaissance et donne mon consentement

**Canonical:** `C1–C2 or native (Advanced)`

- C2
- C1
- Native
- Advanced