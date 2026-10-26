---
name: "weekly-price-check"
description: "Weekly price check for one StayEasy property: own prices across booking sites (Codex, SerpApi) and competitor prices on Booking.com (Claude), logged with source and date."
---

# Weekly price check

Run once a week per property (default Monday). Two parts, done by two roles, then one short summary by Claude.

## Inputs

- Property config: `research/config/properties.csv` (one row per property: name, SerpApi search query, comp set file). Adam adds or removes properties.
- Comp set: the property's `comp_set.csv` (5–8 named competitors, each with its Booking.com link).
- Check-in dates for this week, computed from the run date: **+7, +21, +45 and +90 days**, 2 nights, 2 adults, 1 room. Add a known event date (holiday, festival, long weekend) in place of +45 when Adam names one.

## Part 1 – Own prices across sites (Codex, SerpApi)

1. Run `tools/price_parity.py` for each property in the config, for the 4 dates.
2. One property-detail request per property per date. Never more than **20 requests per property per month**, and never more than **200 in total per month**. The monthly ledger is `research/data/parity/serpapi_ledger.csv`. If the next call would exceed a cap, stop and say so in the PR.
3. Output: `research/data/parity/YYYY-MM-DD-<property_slug>.csv`, one row per date × site, with `source=serpapi_google_hotels` and `collected_at`.
4. One PR per week, titled `Weekly parity YYYY-MM-DD`. List in the PR: requests used this run, used this month, and any site or date with no price.

## Part 2 – Competitor prices (Claude, Booking.com connector)

1. For each competitor in the comp set and each of the 4 dates, search Booking.com by destination (`Medina, Marrakech` or the property's area) and pick the matching listing **by its Booking.com link or ID**. Never pick by name alone; a name search can return a different property.
2. If the competitor is not in the results, write `not_found`; never substitute another property.
3. Append one row per competitor × date to that property's `rate_shop_log.csv` (on Adam's Mac, in the client folder) with `source = Booking.com via Claude connector` and `captured_at`. Fields the connector does not return (room type, rate plan, taxes) are `not_returned`.
4. Light use only: one search per date per area, no repeated polling.

## Part 3 – Summary (Claude)

Fill the competitor and parity lines of the property's `weekly_pickup.md`:

- **Parity:** for each date, the lowest site, the highest site and the gap in %, computed in Python from the CSV. Flag a gap above 5% and any date where the official website is missing.
- **Position:** the property's Booking.com price against the comp set median for each date (Python), with how many competitors were found.
- **Proposals**, only if the evidence supports them, each with evidence, risk, confidence and a review date. Low occupancy alone is never a reason to lower a price. Nothing changes without the owner's written approval.

## Rules

- No invented prices. A missing value stays missing.
- Prices are compared only for the same dates, nights and guests. Say when tax treatment differs or is unknown.
- One property per summary. Never mix properties or clients.
- API keys only in environment variables; never in files, chat or issues.
