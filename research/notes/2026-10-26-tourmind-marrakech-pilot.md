# TourMind Marrakech price-source pilot

- **Issue:** #1 — https://github.com/kisamaadam0-max/stayeasy-workspace/issues/1
- **Question answered:** Public no-login calls returned structured TourMind supply quotes, but this pilot does **not establish reliable Medina coverage, repeatability over time, or permission for repeated non-booking business collection**. It is research evidence, not a pricing recommendation.
- **Sources and dates collected:**
  - TourMind public POST endpoints at https://api.tourmind.com/skill/toc/: `search_location`, `search_hotels`, `query_room_rates`, `batch_query_room_rates`, `get_hotel_detail`. Recorded collection request starts: **2026-10-25T23:23:39Z–2026-10-25T23:26:56Z**. The accompanying requests CSV contains each payload, HTTP status, elapsed seconds and sanitized response; its `source` is always `tourmind_api`.
  - [SKILL.md v1.0.8](https://github.com/tourmind-com/Hotel-Booking-AI/blob/2f9eae24a1f8ae41ba10ff77caf397879a73be02/SKILL.md), [parameter guide](https://github.com/tourmind-com/Hotel-Booking-AI/blob/2f9eae24a1f8ae41ba10ff77caf397879a73be02/references/parameter_guide.md), [README](https://github.com/tourmind-com/Hotel-Booking-AI/blob/2f9eae24a1f8ae41ba10ff77caf397879a73be02/README.md), and [MIT licence](https://github.com/tourmind-com/Hotel-Booking-AI/blob/2f9eae24a1f8ae41ba10ff77caf397879a73be02/LICENSE), read 2026-10-25. Exact source commit pinned; no update endpoint called or update downloaded.
  - [TourMind Skills](https://tourmind.com/en-US/skills) and [business integration](https://tourmind.com/en-US/skills/booking), inspected 2026-10-25, including the Skills footer's Terms & Conditions control.
- **What was found:**

## Coverage and geographic fidelity

`search_location` resolved **Medina, Marrakech, Marrakech-Safi, Morocco**, neighborhood region **33222**, with **595** in `hotel_count`. This is a catalogue metadata count, not a count of riads or live availability. The same response contains five hotel-name matches, two beginning with “Riad”; these are location-lookup results, not verified stay products or a complete Medina inventory. No Google endpoint was called directly; TourMind itself returns a Google-derived `place`, which was not used for searching.

All rate searches used that region, no budget filter, **2 adults per room, 1 room, 0 children, 2 nights**. The table below is computed from the saved responses and rate CSV; counts are products, not unique room types. No hotel was queried for rates more than once per completed stay collection.

| Check-in | Check-out | Returned candidates | Names containing “riad” | Hotels with live products | Product rows | Empty-status rows |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-12-10 | 2026-12-12 | 1 | 0 | 1 | 143 | 0 |
| 2026-12-31 | 2027-01-02 | 2 | 0 | 2 | 16 | 0 |
| 2027-02-14 | 2027-02-16 | 3 | 0 | 2 | 188 | 1 |
| 2027-04-08 | 2027-04-10 | 2 | 0 | 2 | 152 | 0 |

There are **3 unique priced-search candidates**: Dellarosa (822942), Opera Plaza Hotel Marrakech (778223), and Valeria Madina Club Resort All Inclusive (923007). All return star rating 4. No candidate was verified as a Medina riad or boutique hotel. Dellarosa's English address explicitly says **Quartier Hivernage**; Valeria's says **Route de Fes, Bab Atlas**. Static details place all three in region **33220**, rather than requested **33222**. These are material scope inconsistencies; the returned `search_scope` label alone is insufficient evidence of Medina membership. Dedicated district names were not returned, so `area_district` stays blank; addresses are retained separately.

Three named riad probes were absent from every region result but **present in keyword lookup**:

| Probe | Relevant returned names / IDs | Meaning |
| --- | --- | --- |
| Riad Yasmine Marrakech | Riad Yasmine Marrakech / 7583884; Riad Yasmine / 8271524 | Multiple potential identities; not deduplicated by assumption |
| Riad BE Marrakech | Riad Be Marrakech / 8272165 | Address explicitly includes Medina |
| Riad Kniza Marrakech | Riad Kniza / 2566742; RIAD KNIZA / 1272173 | Multiple potential identities; both map to region 33220 |

These are examples **missing from the priced region search**, not proof of missing catalogue records or sold-out hotels. Keyword mode does not check stay availability. No rates were requested for the probe hotels, to retain the small region-first pilot scope. A verified full count of Medina riads/boutique hotels, and a supported list of well-known properties absent from TourMind's entire catalogue, could not be established. The name-based riad count is a transparent string heuristic, not a property classification.

## Price basis and fields

There are **499 returned live-product rows**, all in **CNY**, plus **1** blank-price status row. All returned product adult capacities match the requested 2 adults. Prices and returned nightly rounding are preserved exactly; nightly values were not recomputed from totals. Product duplication is retained because products can differ by cancellation, meal or supplier and opaque rate codes are excluded from persisted output.

The source label is exactly **`tourmind_api`**, with the operation in a separate `endpoint` column. These are **TourMind supply quotes**, not observations of public Booking.com or Expedia storefront prices. The pinned README describes comparison across OTA and hotel suppliers; SKILL.md labels the displayed basis “TourMind live room rates”. Neither the documented rate contract nor the collected rate objects establishes a Booking.com/Expedia retail channel or attributes each quote to a named supplier. No retail parity, commission/net-price interpretation, or markup is inferred.

Of the returned products, **493** have `is_on_request=false` and **6** have `true`. The latter require supplier confirmation. No final inventory check was performed. Opera Plaza appears in the February search but its batch result is `no_matching_live_room`; that successful empty response remains in the dataset. It is not an API failure or evidence that the whole hotel is sold out.

Meal codes use v1.0.8's mapping, including type 2 = breakfast for booked guests; raw meal codes/counts remain available. Cancellation JSON preserves returned deadlines and timezone offsets. The API rate objects did not return an explicit tax-inclusion field: `taxes_included=not_returned` on product rows. The README/skill claim room prices include taxes, but this claim is kept separate from per-product API evidence.

Static `hotel.fees.mandatory` discloses additional at-property charges: city tax **MAD 19.80 per person/night** for Dellarosa and Opera Plaza; city tax **EUR 1.83 per person/night** for Valeria, with under-12 exemptions stated in each response. Dellarosa also returns a **MAD 1000 per stay breakage deposit**, Opera Plaza a **MAD 536 damage deposit before check-in**. These are API disclosures at the detail-call timestamps in the requests CSV, not independently verified tax rules. They remain in their original currencies; none is added to or converted into the CNY quote. The disclosure prose also says supplied charges were included, so the exact treatment remains ambiguous.

## Stability and repeatability

The **15 recorded completed calls** all returned HTTP **200**, top-level `ok=true`; no observed HTTP 429, 401, transport errors or failed batch items. Elapsed times were **1.187–18.140 seconds**, median **4.137 seconds**, measured by Python's monotonic clock, including network time. This is a small sample, not an SLA or proof that no limits exist. The one empty batch item is preserved rather than retried.

Requests ran serially (client concurrency **1**) with a **2-second pause** before each subsequent network call. Each stay queried at most **3 hotels**, below the maximum 20. There was an earlier manual location smoke test (HTTP 200, 1.714509 seconds, response not used for the dataset), and an interruption while a December 31 search was in flight. That unfinished attempt has no retained response/timing and is excluded from the 15-call statistics. Resume reused completed saved calls; no completed rates were recollected. Static details were collected in the resumed session.

The script and sanitized response log permit offline inspection and deterministic replay of the transformation. Temporal price stability was **not tested**: this is one completed collection per stay. The live API is dynamic, and v1.0.8 documents a separate final rate/inventory check, which is prohibited here. Therefore quoted inventory is query-time supply evidence only.

- **Estimates:** None. Candidate/row counts and timing statistics are calculated from saved responses. The “riad” name heuristic above is explicitly not an estimate of total coverage.
- **Gaps:** No verified comprehensive Medina coverage, district field, independent retail-price comparison, final inventory verification, longitudinal repeatability test, per-product tax boolean, or explicit permission for ongoing commercial rate monitoring. No missing values were invented. The filenames follow issue #1's requested **2026-10-26** prefix; actual collection request timestamps are **2026-10-25 UTC**. No booking/payment/account operation, user key, authentication flow, CAPTCHA, conversion, or scraping of other hotel sites was used. Only `research/` and `tools/` changed.
- **Licence or terms of use:** The pinned repo is MIT licensed for software/documentation. This does not itself establish a licence for hotel data or repeated non-booking business analysis. No published clause expressly authorizing that use was found in the inspected skill/reference/README/licence or TourMind Skills/business pages. The footer displayed Terms & Conditions, but clicking it produced no terms document or URL. Searches of TourMind's published pages did not establish a relevant clause; no clause is quoted because none was found. This is an evidence gap, not a conclusion that the use is permitted or prohibited. The [separate ToB integration](https://tourmind.com/en-US/skills/booking) requires an independently authorized token; the pinned README also distinguishes its business Skill Token from this public ToC integration. No token was obtained or used. Ongoing business collection rights remain unconfirmed.
- **Data file:** `research/data/2026-10-26-tourmind-marrakech-pilot.csv`; companion `research/data/2026-10-26-tourmind-marrakech-pilot-requests.csv` holds sanitized request/response evidence. Blank price fields belong to the explicit empty-status row, not zero-price inventory. `collected_at` is UTC request start time. No opaque access links, rate codes, contacts, credentials or client files are persisted.

## Reproduce the collection or inspect saved evidence

```bash
python3 tools/tourmind_rates.py --output-dir /tmp/tourmind-new-pilot
# After an interruption, reuse completed responses without requerying them:
python3 tools/tourmind_rates.py --output-dir /tmp/tourmind-new-pilot --resume
```

Python standard library only; outbound HTTPS required, no API key. New collections are refused if the output directory already contains pilot CSVs unless `--resume` is explicitly supplied. Replay of an interrupted network request with no saved response may make that request again. The script pins the v1.0.8 request contracts rather than checking for updates. It persists only allowlisted response fields and never exposes anonymous access tickets. Its HTTP callable rejects non-approved operations.
