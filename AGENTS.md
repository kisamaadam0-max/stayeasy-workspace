# StayEasy workspace: rules for every AI and human

StayEasy (stayeasy.ma) is a digital and commercial management agency for riads, villas and independent hotels in Morocco. This repository is the shared toolbox Claude and Codex both work from: the client kit, the skills, the business rules, and the research Codex collects so Claude can analyse it.

Codex reads this file directly. Claude reads it through `CLAUDE.md`.

## Roles

| Who | Role | Does here | Does not |
| --- | --- | --- | --- |
| Adam | Owner | Approves and merges every PR; decides what is kept | — |
| Claude | Revenue Manager and Sales Strategist | Writes research requests, analyses research, maintains `templates/`, `skills/` and `docs/` | Write scrapers or code |
| Codex | Research and data engineer | Collects data and research asked for in `research_request` issues; writes scripts in `tools/`; delivers into `research/` | Change templates, skills or business rules; give pricing advice |
| ChatGPT | Second opinion | Reviews a note or plan when Adam asks | Write to the repo |

## How Claude and Codex work together

1. Adam tells Claude what he needs.
2. Claude opens a `research_request` issue: the question, the data needed, the period, the accepted sources, the output format.
3. Codex delivers in one PR: data in `research/data/`, a note in `research/notes/`, any script in `tools/`.
4. Claude reviews the PR. It checks sources, dates, gaps and whether the data answers the question, and comments on the PR.
5. Adam merges. Claude then writes the analysis or recommendation.

One issue = one branch = one PR. Status and questions go in the issue, not in files.

## Rules for every research delivery

- **No invented data.** Every figure has a source (URL or file) and the date it was collected. If something can't be found, say so; never fill the gap.
- **Facts and estimates are separate.** Estimates are labelled "estimate", with the method.
- **Legal collection only.** Use official APIs, public pages within their terms, or files Adam provides. No logging in to accounts, no CAPTCHA bypass, no aggressive scraping of Booking.com, Expedia, Airbnb or Google.
- **No personal data.** No guest names, emails, phone numbers or reviewer identities. Aggregate it, or drop it.
- **No credentials** in files, code or issues. Use environment variables, never committed.
- **Data files** are CSV, UTF-8, one header row, with `source` and `collected_at` (ISO date) columns. Prices state currency and whether taxes and breakfast are included.

## Rules for client work

- Client folders stay on Adam's Mac (`~/Documents/Projects/Stayeasy/clients/`), never in this repo. `clients/` is ignored by git.
- One client per folder. Never reuse one client's rates, data or results for another, or for Adam's own properties (Riad Thaïs, Riad Saba, Riad Alaya).
- Nothing changes in an extranet, channel manager or website without the owner's written approval, logged in that client's `decision_log.md`.
- Low occupancy alone is never a reason to lower a price.
- KPIs are calculated in Python or SQL from exports, never estimated by an AI. Definitions are in `templates/client_kit/02_onboarding/baseline/kpi_definitions.md`.
- Never promise results to an owner.

## Skills

A skill is a step-by-step procedure in `skills/<name>/SKILL.md`. When a request matches a skill's description, follow that file exactly.

| Skill | Use when |
| --- | --- |
| `skills/stayeasy-new-client/` | Adam has a new client to set up |

## Map

| Folder | What is in it | Who changes it |
| --- | --- | --- |
| `templates/client_kit/` | Master template copied for every new client | Claude (Adam approves) |
| `skills/` | Procedures for Claude and Codex | Claude (Adam approves) |
| `docs/` | Client information system, file naming standard | Claude (Adam approves) |
| `research/notes/` | One note per research question | Codex writes, Claude reviews |
| `research/data/` | Collected datasets (CSV) | Codex |
| `tools/` | Scripts that collect or clean research data | Codex |
| `clients/` | Ignored; client work is on the Mac | — |

Business rules and KPI definitions shared with the software are in the `stayeasy-revenue-intelligence` repo (`docs/BUSINESS_RULES.md`). That repo is the app; no app work happens here.

## Definition of done for a PR

- The issue's questions are answered, or the gaps are listed.
- Every data row has a source and a collection date.
- No personal data, credentials or client files.
- The PR template is filled in.
