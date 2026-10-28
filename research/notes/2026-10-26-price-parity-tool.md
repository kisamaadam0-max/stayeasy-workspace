# Weekly price-parity tool — build and single-call validation

- **Issue:** #6 — https://github.com/kisamaadam0-max/stayeasy-workspace/issues/6
- **Question answered:** Implemented the reusable Part 1 collector and descriptive site-price summary. This is a build/test delivery, not a full weekly check, competitor shop, schedule or pricing recommendation.
- **Sources and dates collected:** Merged `skills/weekly-price-check/SKILL.md` Part 1; issue #6; public SerpApi Google Hotels detail response collected at **2026-10-26T00:22:11Z**, using the existing issue #3 public property token. `source=serpapi_google_hotels` on all observation/ledger/token rows. The five earlier monthly ledger entries are imported from `research/data/2026-10-26-serpapi-google-hotels-pilot-requests.csv`, preserving source and collection timestamps. API field reference: https://serpapi.com/google-hotels-property-details ; terms: https://serpapi.com/legal . No new account/other-engine calls.
- **What was found:**
  - **Exactly 1 live SerpApi request** for this issue, `google_hotels`, saved Riad Thaïs token, 2026-12-10 to 2026-12-12, 2 adults, 0 children, 1 room, MAD. HTTP 200 / Success. Cache status was not explicitly exposed and remains `unknown`; it consumes one conservative budget unit. Tests/dry-runs made **0** API calls.
  - October's shared ledger has **6 reserved attempts**, all for `riad_thais`: **5 imported pilot calls + 1 new test**. Remaining tracked budgets: **14/property and 194/account**. Cached, failed and interrupted attempts count too. The guard uses actual UTC collection month, not the stay date or an overridden run date.
  - The property config contains only the issue-requested Riad Thaïs row. The saved public token was reused; no discovery request was needed for validation. Future new properties require exact unambiguous normalized name matching for initial discovery, then token matching. Unknown/ambiguous identities produce status rows, never substituted property prices.
  - Default dry-run from 2026-10-26 plans check-ins **2026-11-02, 2026-11-16, 2026-12-10, 2027-01-24**, with two-night stays. It prints budget and writes no files. `--dates` overrides check-ins; `--max-requests 1` enforced the smoke-test limit.
  - A shared locked ledger reserves before sending and keeps failed/interrupted reservations. Atomic CSV replacement and separate stable locks protect updates. Existing daily output is never overwritten. Calls are serial, with pauses, no redirects or automatic retries. Output contains only allowlisted property/price fields, without contacts, URLs or review bodies. The key is read only from the environment and is absent from files and captured output.
  - The summary uses returned numeric stay totals (nightly-only amounts form separate groups), Decimal math, all tied sites, a >5% flag and confirmed-official-offer presence. Different properties/runs are rejected; currencies, occupancy, stay dates and explicit tax bases are separated. Missing or conflicting observations remain visible rather than being treated as zero prices. Unknown room/meal/cancellation equivalence prevents treating these descriptive extrema as like-for-like parity proof.
- **Estimates:** None. Budget counts and the summary gap are computed. Synthetic values in unit-test fixtures are clearly labelled test data and are not research observations.
- **Gaps:** No full weekly run or competitor collection; no scheduler or client-folder work. No official-site offer was confirmed. Tax, breakfast and room/rate-plan equivalence remain unverified. Cache yes/no and billed quota usage are unknown. The monthly cap covers this single shared ledger: other scripts, machines or account activity must be reconciled into it before running; it cannot observe external spending. The five known pilot attempts were seeded specifically to avoid resetting usage to zero. Historical pilot scripts must not be used to bypass the shared ledger. Local locks do not coordinate separate machines or checkouts. Reconcile the ledger before each weekly PR. No protected directories were edited.
- **Licence or terms of use:** Uses the authorized SerpApi API, without direct scraping or other engines. The prior pilot's documented terms/reuse uncertainty remains unresolved; implementing a collector does not assert unrestricted data-redistribution rights. No authentication flow, booking or account changes.
- **Data file:** `research/data/parity/2026-10-26-riad_thais.csv` (3 returned site offers, one test date), `research/data/parity/serpapi_ledger.csv` (6 tracked October attempts). Config/token files are in `research/config/`. Scripts and usage are in `tools/price_parity.py`, `tools/parity_summary.py`, `tools/README.md`.

## Validation

Offline unit tests cover the per-property 21st-call and total 201st-call rejections, concurrent reservations, monthly rollover, pre-request persistence, cached/failed/interrupted attempts, secret-safe failure handling, engine restriction, four-date no-key dry-run, a mocked end-to-end run, daily-output protection, summary math/ties/zero denominator, mixed currencies/tax/occupancy, missing prices, and cross-property/run rejection. No network is used by the tests. The live CSV was passed through the summary CLI, and a secret scan plus `git diff --check` completed. The delivery branch remains for Adam to review/merge.

## Live-test summary (computed by tools/parity_summary.py)

# Site-price summary — Riad Thaïs Marrakech

Run: issue-6-smoke-2026-10-26

| Stay | Currency / basis / tax | Guests / rooms | Lowest site(s) | Lowest | Highest site(s) | Highest | Gap % | >5% | Official offer |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | --- | --- |
| 2026-12-10 → 2026-12-12 | MAD / stay / tax_unknown | 2 adults + 0 children / 1 | Booking.com | 1987 | Agoda | 2197 | 10.57 | yes | missing (no confirmed offer) |

Gap = (highest − lowest) / lowest × 100, calculated with Decimal; zero denominator is not computable. Ties are listed. A single offer gives a zero observed gap, not evidence of parity.

Source: serpapi_google_hotels. Collected: 2026-10-26T00:22:11Z.

Unknown tax treatment is not tax-inclusive evidence. Tax bases, stay lengths, currencies and occupancy are kept separate. Room, meal and cancellation equivalence may be unknown; these are observed extrema, not a like-for-like parity conclusion. An absent official flag is not proof that no direct rate exists.
