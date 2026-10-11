# Job boards: worth adding to the scraper?

Checked 11 Oct 2026 against our current `jobs.csv` (Jobs without German: keywords + Finance & Legal + People & HR + Project manager).

**Verdict:** only **EnglishJobs.de** is worth wiring in next. The others are the same source we already have, a reprint of it, or too noisy / not English-filtered.

| Rank | Board | Add to scraper? | Score | Why |
| --- | --- | --- | --- | --- |
| 1 | [EnglishJobs.de](https://www.englishjobs.de/) | Yes, later | **7 / 10** | Real extra employers (Deutsche Börse, Amazon, Emerson, State Street, Olympus). Also reprints some of our listings. |
| 2 | [Arbeitnow](https://www.arbeitnow.com/english-speaking-jobs) | Maybe later | **4 / 10** | A few new recruiter roles. Search is noisy and many ads are German or sales. |
| 3 | [Make it in Germany](https://www.make-it-in-germany.com/en/working-in-germany/job/looking-for-job) | No (bookmark only) | **3 / 10** | Official portal, not English-only, bot-walled, hard to scrape. |
| 4 | [English Jobs in Germany](https://www.englishjobsingermany.com/) | No | **2 / 10** | Same ads we already have (and Arbeitnow copies). |
| 5 | [Jobs without German](https://www.jobswithoutgerman.de/) | Already in | **0 / 10 extra** | This is our current source. |

---

## 1. [English Jobs in Germany](https://www.englishjobsingermany.com/) — skip (2 / 10)

Claims dedicated HR & People and Finance & Accounting categories and “verified English-only” roles.

**What the pages actually show**

- About 2,795 “English-only” jobs (our JWG index has about 3,910).
- Search `accounting` (102 hits): first result is **(Senior) Fund Accounting & Reporting Manager, bunch, Berlin** — already row 1 of our old scrape.
- Other accounting hits we already have: YAZIO (Senior) Controller, FINN Lead Group Controller, Isar Aerospace Senior Compensation & HR Controlling.
- Search `hr` (500 hits): first results are **Flix Senior Workday Solution Architect**, **Flix Expert Tech Solution Architect - HR**, **Flix (Senior) HR Tech Business Analyst** — already in our file.
- Job URLs include `arbeitnow-` slugs and the same employer/job IDs JWG uses. The site scrapes ATS boards and Arbeitnow, then relabels them.

**Overlap:** very high. Matches what you saw when you clicked through.

**Add?** No. It would mostly duplicate `jobs.csv`.

---

## 2. [Jobs without German](https://www.jobswithoutgerman.de/) — already added (0 / 10 extra)

This is the site `scrape_jobs.py` already reads (search index + category pages). Adding it again would 100% duplicate the file.

Keep using it as the primary source.

---

## 3. [EnglishJobs.de](https://www.englishjobs.de/) — best next source (7 / 10)

Broad English-speaking search engine. Listings are readable without logging in (`/jobs/accounting`, `/jobs/controller`, `/jobs/recruiter`).

**Already in our file (do not need again)**

- One Mobility — Senior Accountant Consolidation & Reporting
- FINN — Lead Group Controller
- Redcare Pharmacy — Junior Controller
- Zattoo — Financial Controller
- Delivery Hero — Senior Group Controller

**Not in our file (the useful new ones)**

- Deutsche Börse — Business Process Specialist, Finance Transformation
- Emerson — Accounting Manager, Hanover
- Amazon — Senior Financial Analyst (Munich accounting team)
- State Street — Alternative and Bank Loans Accounting
- Société Générale — Financial Controller / Accountant, Frankfurt
- Symrise — Senior Corporate Controller
- Zeiss — Senior Product Controller
- Nexperia — Finance Controller
- suena.energy — Financial Controller
- Olympus — Talent Acquisition Partner EMEA, Hamburg
- LiveEO — Senior Recruiter, Berlin
- Scope — Specialist Recruiting & Development, Frankfurt

**Caveats**

- Many hits are senior, agency (Michael Page / Page Executive), tutoring, or professor roles.
- “Recruiter” search is polluted: the word appears in the apply text of engineer ads (Micron, Asana, Infineon).
- “Controller” search includes Controls Engineer and air-traffic “Surveillance Controller”.
- English is not guaranteed the way JWG labels it. Large German corporates often still want German.

**Add?** Yes, as a second source, using the same title filters we already have. Expect a mix of new corporates and some repeats.

---

## 4. [Arbeitnow](https://www.arbeitnow.com/english-speaking-jobs) — weak (4 / 10)

About 13,000 Germany jobs, plus UK/France/Switzerland. Has an English-speaking filter and a public job API (`/api/job-board-api`).

**Overlap with us**

- n8n Senior Product Manager (Licensing & Billing) — on JWG’s homepage too
- Agile Robots Senior Project Manager — already in our Project manager slice
- Raisin / Lyceum / Enpal names we already track

**Possibly new**

- NetBird — Talent Acquisition (Berlin)
- Constructor — Associate GTM Recruiter (Munich)
- Foodji — Recruiter / Talent Acquisition Manager (Munich)
- Vogel — Senior Manager Accounting & Controlling (Munich; German-style `m/w/d` title, may need German)

**Problems**

- Keyword search (`accountant`, `recruiter`, `finance`) often ignores the query and shows the same “recent jobs” feed (pizza cooks, Werkstudent, sales Account Executives in Paris/London).
- The public API page we pulled (325 jobs) was mostly sales “Account Executive” roles outside Germany once you filter for finance-ish words.
- A lot of ads are German-language or not entry-level HR/finance.

**Add?** Only if we use the English-speaking filter and tight title words (`accountant`, `controller`, `recruiter`, `talent`). Low yield after that. Not the next build.

---

## 5. [Make it in Germany](https://www.make-it-in-germany.com/en/working-in-germany/job/looking-for-job) — bookmark only (3 / 10)

Official government portal. Listings come from the Federal Employment Agency. Employers tick a box saying they welcome applications from abroad.

**What we could check**

- Fetch and browser both hit a Radware bot wall (HTTP 403). No listing table to compare.
- There is no “English only” or “no German required” filter. Business / accounting / administration categories still need a German check per advert.
- Typical BA accounting ads (from other boards that syndicate the same market) ask for C1 German.

**Add?** No, not to the scraper. Keep the link for visa and “working in Germany” info, and for occasional manual searches.

---

## What to do next

1. Keep scraping **Jobs without German** (already done).
2. If we add a second site, add **EnglishJobs.de** only.
3. Leave English Jobs in Germany, Arbeitnow, and Make it in Germany as human bookmarks, not extra scrapers.
