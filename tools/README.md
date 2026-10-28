# Tools

Scripts Codex writes to collect or clean research data. One script per data source, with a short header comment: what it collects, from where, and the terms that allow it.

- Read credentials from environment variables only. Never commit them.
- Write output to `research/data/` with `source` and `collected_at` columns.
- Respect the collection rules in `AGENTS.md` (official APIs, public pages within their terms, files Adam provides).

## Weekly own-site parity (Codex)

Follow Part 1 of `skills/weekly-price-check/SKILL.md`. Configure active properties
in `research/config/properties.csv`; public property tokens are saved in
`research/config/property_tokens.csv`. No client exports or guest data belong here.

```bash
# No API call or file write; no key required. Local date defaults to Casablanca.
python3 tools/price_parity.py --property riad_thais --dry-run
# Optional four check-in overrides (checkout is always +2 days):
python3 tools/price_parity.py --property riad_thais --dates 2026-12-10,2026-12-31,2027-02-14,2027-04-08 --dry-run
# Once authorized for a weekly run, with SERPAPI_API_KEY set in the environment:
python3 tools/price_parity.py --property riad_thais
python3 tools/parity_summary.py research/data/parity/YYYY-MM-DD-riad_thais.csv
python3 -m unittest discover -s tools/tests -v
```

Default check-ins are +7/+21/+45/+90 days from the Casablanca run date; stays are
2 nights, 2 adults, 1 room, no children. Known tokens cost one detail request/date.
For a new property, one exact-name discovery may cost an extra request; ambiguous
matches stop attribution instead of guessing. `--max-requests 1 --dates YYYY-MM-DD`
is a single-call smoke test, not a full weekly check. Never follow result URLs.

The shared `research/data/parity/serpapi_ledger.csv` counts every reserved attempt,
including failed, interrupted and cached calls, against 20/property and 200/total
per UTC collection month. It includes the five known October issue #3 pilot calls.
The collector locks and reserves before sending, never retries automatically, and
prints remaining budgets. Do not delete/reset the ledger or use parallel copies
of it. Other scripts, machines or external account use must be reconciled into
this ledger before collection; it cannot observe spending outside the ledger.
The old pilot's separate cap is not an account-wide guard: use this weekly tool
for future collection. No account endpoint is called. Budget month uses actual
UTC request time even with `--run-date` calendar overrides.

Dry-run plans may exceed available quota; reservations always enforce the caps.
A run-level lock protects same-date outputs. Existing daily CSVs are never
replaced; partial runs stay visible. Discovery and errors consume budget too.
Credentials come only from the environment; key-bearing URLs and raw exception
messages are never persisted. Cache is yes/no only when explicitly exposed;
otherwise it is unknown and consumes one conservative budget unit. Errors and
missing site prices produce status rows, never zero prices.

The summary keeps different currencies, dates, occupancy and tax bases separate;
it uses returned extracted stay totals (nightly-only prices form separate groups).
The computed gap is `(highest-lowest)/lowest*100`; zero denominators are undefined.
It reports ties, missing official offers and unknown comparability without pricing
advice. Public API observations do not establish identical rooms or rate plans.
Terms and their unresolved reuse limits: https://serpapi.com/legal .
