# StayEasy client kit template v01

**Version:** 1.0  
**Status:** Approved  
**Owner:** Client Delivery  
**Date:** 2026-10-25  

Filled-in version of the approved folder standard in `docs/client_information_system.md`. Same folders; this kit adds the working documents for each step.

## New client in 5 steps

1. Copy this folder to `~/Documents/Projects/Stayeasy/clients/onboarding/<client_slug>/` on Adam's Mac (do not edit this master). The skill `skills/stayeasy-new-client/` does steps 1–3.
2. Replace `{{PROPERTY_NAME}}`, `{{OFFER}}` and the other placeholders. Unknown = `TBD`.
3. Paste the diagnostic form answers into `02_onboarding/intake/diagnostic_intake.md`, then fill `00_client_control/client_manifest.md`.
4. Send the client `02_onboarding/access_setup/access_request_fr.md` and `02_onboarding/baseline/data_request_fr.md`.
5. Use `CLAUDE.md` as the instructions of that client's Claude project.

Move the folder to `clients/active/` only when the onboarding gate (§6 of the client information system) passes.

## Where each working document lives

| Step | File |
|---|---|
| AI rules for this client | `CLAUDE.md` |
| Status, waiting items, next review | `00_client_control/project_state.md` |
| Client facts | `00_client_control/client_manifest.md`, `02_onboarding/intake/diagnostic_intake.md` |
| Decisions (validated before going live) | `00_client_control/decision_log.md` |
| Accesses (no passwords) | `00_client_control/access_register.md` |
| Access request to client (FR) | `02_onboarding/access_setup/access_request_fr.md` |
| Data request to client (FR) | `02_onboarding/baseline/data_request_fr.md` |
| KPI definitions | `02_onboarding/baseline/kpi_definitions.md` |
| Source exports + log | `03_source_data/` |
| Initial audit (FR) | `04_delivery/revenue_management/initial_audit.md` |
| Strategy proposal + owner validation (FR) | `04_delivery/revenue_management/strategy_proposal.md` |
| Competitor set and price log | `04_delivery/revenue_management/competitors/` |
| Monthly report (FR) | `05_reporting/monthly/monthly_report.md` |
| Monthly OTA commission check (FR) | `05_reporting/monthly/ota_commission_check.md` |
| Weekly pickup and distribution check (FR) | `04_delivery/revenue_management/weekly_pickup.md` |
| 12-month demand and rate calendar (FR) | `04_delivery/revenue_management/rate_calendar.md` |
| Direct booking plan (FR) | `04_delivery/marketing/direct_booking_plan.md` |
| Marketing calendar and review summary (FR) | `04_delivery/marketing/marketing_calendar.md` |

Website and Google offers use `04_delivery/website_direct_booking/` and `seo_google_business/`; templates for those are not written yet.

## Link with StayEasy Revenue Intelligence

The software in the `stayeasy-revenue-intelligence` repo has six agent prompts (`prompts/`: market, property, distribution, direct booking, revenue, report). They are drafts and do not run in Phase 1. This kit uses the same rules and KPI definitions (`docs/BUSINESS_RULES.md` in that repo), so a client set up here can be loaded there later with its own `property_id`.
