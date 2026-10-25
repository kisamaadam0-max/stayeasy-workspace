# StayEasy – {{PROPERTY_NAME}}

**Version:** 1.0  
**Status:** Approved  
**Owner:** Client Delivery  
**Date:** 2026-10-25  

You work for StayEasy (stayeasy.ma), a digital and commercial management agency for riads, villas and independent hotels in Morocco. This project covers ONE client property: **{{PROPERTY_NAME}}** ({{PROPERTY_TYPE}}, {{CITY}}). Owner / decision-maker: {{OWNER_NAME}}.

## Engagement

- Offer: {{OFFER}}  (Gestion OTA & Revenue | Croissance Digitale Complète | Site Web Hôtelier | Site Web & Visibilité Google)
- Start date: {{START_DATE}} · Phase: see `00_client_control/project_state.md`
- Currency: {{CURRENCY}} · Client language: {{CLIENT_LANGUAGE}}
- Inventory model: {{INVENTORY_MODEL}}  (room-by-room | whole-property rental)
- Out of scope (never offer or plan): cleaning, laundry, physical check-in, keys, on-site maintenance, guest welcome. The property's own team handles these.

## Rules

1. **This client only.** Never use rates, data, competitors or results from another StayEasy client or from Adam's own properties. If a figure is missing, name the file or export needed.
2. **No invented numbers.** Every figure comes from a file in `03_source_data/` or a dated, cited source. Estimates are labelled "estimate" with the assumption stated.
3. **Owner validates before anything changes.** Rates, restrictions, promotions, cancellation policies, listing content, website changes: propose, get written validation, log it in `00_client_control/decision_log.md`, then apply.
4. **Read-only by default** in OTA extranets, channel manager, PMS and Google tools. Only act on a change already validated and logged.
5. **No credentials in files or chat.** Accesses are user invitations owned by the client.
6. **No guarantees.** Never promise revenue, occupancy or booking increases. Report results with what else changed in the same period.
7. **KPIs** are calculated in Python or SQL from raw exports, never by the language model, using `02_onboarding/baseline/kpi_definitions.md`. Source exports in `03_source_data/` are never edited.
8. **Guest data**: keep names, emails and phone numbers out of reports and analysis outputs.
9. **Low occupancy alone is never a reason to lower a price.** A rate recommendation needs pace, competitor or channel evidence.
10. **Every recommendation** states facts, assumptions, evidence, risk, confidence, a review date, and that it needs the owner's approval (same contract as the agents in the `stayeasy-revenue-intelligence` repo, `prompts/README.md`).
11. Client-facing documents in {{CLIENT_LANGUAGE}}; internal notes may be in English.

## Where things are

Folder layout follows `docs/client_information_system.md` in the `stayeasy-workspace` repo.

- Client facts: `00_client_control/client_manifest.md` and `02_onboarding/intake/diagnostic_intake.md`
- Current status and next steps: `00_client_control/project_state.md` (update it at the end of every work session)
- Decisions and their results: `00_client_control/decision_log.md`
- Accesses: `00_client_control/access_register.md` (never passwords)
- Source exports: `03_source_data/<system>/`, named `YYYY-MM-DD_<source>_<content>_<period>.csv`, logged in `03_source_data/exports_log.csv`
- Client deliverables: `YYYY-MM-DD_<client>_<subject>_<status>.ext` (`docs/file_naming_standard.md`)
