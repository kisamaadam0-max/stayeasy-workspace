# SerpApi Google Hotels pilot — Riad Thaïs

- **Issue:** #3 — https://github.com/kisamaadam0-max/stayeasy-workspace/issues/3
- **Question answered:** SerpApi returned attributed OTA prices for Riad Thaïs on the detailed date. It did not return an official-site offer, so this sample cannot establish OTA versus direct-site parity. Repeatability and broader competitor coverage were not measured.
- **Sources and dates collected:**
  - `https://serpapi.com/search.json`, engine `google_hotels` only; **5 actual requests**, collection starts **2026-10-26T00:08:49Z–2026-10-26T00:09:21Z**. Each row has `source=serpapi_google_hotels`, a UTC request-start `collected_at`, and a request attempt number. The requests and sanitized evidence CSVs provide parameters, search IDs, response creation times and results without the key or request URLs containing it.
  - [Google Hotels documentation](https://serpapi.com/google-hotels-api), [property details documentation](https://serpapi.com/google-hotels-property-details), and [SerpApi legal documents](https://serpapi.com/legal), read 2026-10-26. Legal page states last updated August 27, 2026.
- **What was found:**

## Owner's scope amendment

Adam explicitly changed the scope in chat to **Riad Thaïs only**, excluding **Riad Saba and Riad Alaya**. That supersedes the issue's original broad Medina search, first-four-properties selection and Thaïs exclusion. The amendment is recorded in an issue comment. The actual query was `Riad Thaïs Marrakech`, not `riad Medina Marrakech`. No competitor/client dataset or private client export was used. Only public research results for the authorized property are included.

All calls used `gl=ma`, `hl=en`, `currency=MAD`, 2 adults, 0 children and two-night stays. The four name searches all returned the same property token, `ChkI-tGC66yYwJwzGg0vZy8xMW5iNXFqcTlyEAE`. One additional token-based detail request was made for December 10 only.

## Coverage

| Check-in / check-out | Retained matching property | Aggregate price returned | Per-site price rows in list | Detail performed | Per-site price rows in detail |
| --- | ---: | --- | ---: | --- | ---: |
| 2026-12-10 / 2026-12-12 | 1 | yes | 0 | yes | 3 |
| 2026-12-31 / 2027-01-02 | 1 | no | 0 | no | not measured |
| 2027-02-14 / 2027-02-16 | 1 | yes | 0 | no | not measured |
| 2027-04-08 / 2027-04-10 | 1 | yes | 0 | no | not measured |

These are counts of the named target retained from the response, not counts of all Medina riads. No district field was returned and Medina membership was not independently verified. GPS was **31.615070199999998, -7.977506399999999**. The detail response address was **derb Kaid, Quartier Bab Hmer, N89, Marrakech 40000, Morocco**. Returned type was `hotel`; hotel class was absent. Aggregate rating **5** and review count **15** were returned; review texts and reviewer identities were not retained.

No December 31 price is not proof of sold-out inventory. The other two undetailed stays have unattributed aggregate prices only: February 14 returned **MAD 1,115/night and MAD 2,230/stay**; April 8 returned **MAD 1,136/night and MAD 2,271/stay**. Neither is attributed to an OTA or the direct site. The December 10 list aggregate was MAD 994/night and MAD 1,987/stay, also preserved in evidence.

## Sites and price basis

The December 10 detail response returned these three site-level offers for 2 guests:

| Returned price source | Nightly price (MAD) | Entire two-night stay (MAD) | Official flag | Tax/breakfast fields |
| --- | ---: | ---: | --- | --- |
| Booking.com | 994 | 1,987 | not returned | not returned |
| Agoda | 1,099 | 2,197 | not returned | not returned |
| priceline.com | 1,098 | 2,196 | not returned | not returned |

Expedia was absent from this detail response. **0 of 1 detailed property-date responses** contained an explicitly official offer. An absent `official` boolean is recorded as `not_returned`, not falsely converted to `false`. These are metasearch observations exposed by SerpApi, not direct OTA API quotations or independently verified booking offers. No supplier booking link was followed.

SerpApi's [property details schema](https://serpapi.com/google-hotels-property-details) distinguishes nightly `rate_per_night` from entire-trip `total_rate`. It documents display/lowest amounts separately from explicit `before_taxes_fees` and `after_taxes_fees`; the display basis may depend on search location. Neither explicit tax field was returned here. The CSV preserves the full returned rate dictionaries and records tax/breakfast inclusion as `not_returned`. No inclusion, room equivalence, cancellation equivalence, or parity verdict is inferred. Rounded totals are kept as returned, never recomputed by multiplying rounded nightly prices. MAD is the requested and echoed search currency and the returned amount label; no conversion was performed.

The data CSV has **6 rows**: 3 attributed December offers, 2 explicitly unattributed aggregate observations, and 1 no-price status row. The December aggregate is not duplicated as an extra output offer once site-level details exist. Rows lacking a site are explicit observation/status exceptions to the requested property × date × price-source grain; they do not invent a booking source. The evidence CSV retains the original sanitized observations.

## Request cost, caching and stability

| Step | Actual requests / hard-cap units | Cache yes | Cache no | Cache unknown |
| --- | ---: | ---: | ---: | ---: |
| Four name searches | 4 | 0 | 0 | 4 |
| One property detail | 1 | 0 | 0 | 1 |
| Retries, pagination, other engines, account endpoints | 0 | 0 | 0 | 0 |
| **Total** | **5 of 20** | **0** | **0** | **5** |

All five calls returned HTTP **200**, `search_metadata.status=Success`. Elapsed time was **4.003–4.594 seconds**, median **4.132 seconds** (Python monotonic clock). Calls ran serially with at least a two-second pause between calls; no retries were made. Temporal consistency was not tested.

SerpApi [documents](https://serpapi.com/google-hotels-api) a one-hour exact-parameter cache and says cached searches do not consume monthly searches. These responses did **not** expose an explicit cache boolean or `Cached` status. Therefore a yes/no cache determination and exact billed quota consumption **could not be verified**. The ledger uses `cached=unknown` and `quota_cost=unknown`, conservatively reserving one unit per attempt, including errors, cached responses or interrupted calls. **At most 5 monthly search units** should be budgeted for these five attempts; this is an upper bound, not a verified billing deduction. No account endpoint was queried because only the Google Hotels engine was authorized. We stopped with **15 unused issue-call slots** rather than spend requests to guess cache behavior. The account-wide 200-search balance was not inspected.

- **Estimates:** For weekly monitoring of **4 dates × 6 competitors**, assume one detail request per competitor-date and no cache hits: **24 calls/check × 4 checks = 96 calls/month**, or **24 × 5 = 120** in a five-check month. If list discovery is also repeated for each date: **(24 + 4) × 4 = 112**, or **140** for five checks. An annualized estimate is **24 × 52 / 12 = 104** detail calls/month, or **28 × 52 / 12 ≈ 121.3** including discovery. These are workflow arithmetic estimates, not measured coverage, an account-quota guarantee or pricing advice. Assumptions: stable known tokens, one response per detail, no pagination/retries, all competitors present, weekly checks more than one hour apart. Against the owner's 200/month plan, other clients/tasks consume the same budget; scaling remains subject to response coverage and actual billing. This pilot measured four searches plus one detail, not a six-competitor rate shop.
- **Gaps:** Missing official-site and Expedia offers; no exact billed/cache yes/no evidence; no broad Medina competitor census or independently verified district; no tax, breakfast, room/cancellation comparability fields; no December 31 price; no site breakdown for February/April; no longitudinal reliability test. These limits are not filled with estimates. The remaining call budget was not used because the amended pilot's four-date lookup and December detail were complete.
- **Licence or terms of use:** [SerpApi Terms](https://serpapi.com/legal), section 1: “You may not use our products for any illegal or unauthorized purpose”. Section 2 restricts reproducing, copying, selling/reselling or exploiting the Service/access without written permission. Section 3 disclaims accuracy/completeness/currentness; section 12 also prohibits unlawful use and infringement. No clause expressly granting this specific business-analysis/data-redistribution use was found in the inspected terms. Using the paid API does not by itself resolve third-party rights or establish unrestricted permission to republish hotel results. This is a factual terms summary and an unresolved permission gap, not a legal determination. No direct Google scraping or other engine was used.
- **Data file:** `research/data/2026-10-26-serpapi-google-hotels-pilot.csv`; requests: `research/data/2026-10-26-serpapi-google-hotels-pilot-requests.csv`; sanitized evidence: `research/data/2026-10-26-serpapi-google-hotels-pilot-evidence.csv`.

## Script and replay

`tools/serpapi_google_hotels.py` uses the standard library and reads `SERPAPI_API_KEY` only from the environment. A fixed issue ledger is locked and an attempt reserved on disk **before** any network request. The 21st attempt is rejected even if prior requests were cached or failed. Identical saved parameters are not sent again. Do not delete/reset the ledger to evade the issue budget. Interrupted reservations remain counted and are not automatically retried. Redirects and automatic retries are disabled. Exceptions are logged by class/HTTP status only; key-bearing URLs and raw exception messages are never saved. Responses are reduced to allowlisted nonpersonal fields and target-property results only; URLs, contacts, review bodies, reviewer identities and other properties are omitted.

```bash
# These commands reuse existing parameter reservations and do not repeat them:
python3 tools/serpapi_google_hotels.py lists
python3 tools/serpapi_google_hotels.py detail --token ChkI-tGC66yYwJwzGg0vZy8xMW5iNXFqcTlyEAE
# Transformation only, no API key/network required:
python3 tools/serpapi_google_hotels.py export
```

Validation: offline export replay, explicit 20-attempt boundary, failed-call reservation, duplicate suppression, other-engine rejection, exclusion/redaction, source/date/unique observation checks, and secret scans were performed without additional API calls. Only `research/` and `tools/` changed. Adam merges after review; no recommendations are supplied.
