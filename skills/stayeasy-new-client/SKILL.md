---
name: "stayeasy-new-client"
description: "Open a new StayEasy client (riad, villa or hotel): copy the approved client kit into clients/onboarding, fill the placeholders and diagnostic answers, and return the next steps."
---

# StayEasy – new client setup

Use when Adam says he has a new StayEasy client, or asks to set up / onboard a client.

## Source of truth

- Master template: `templates/client_kit/` in the `stayeasy-workspace` repo (on Adam's Mac: `~/Documents/Projects/stayeasy-workspace/templates/client_kit/`). Read its `README.md` first. Pull the repo before copying so the template is current.
- Folder rules and onboarding gate: `docs/client_information_system.md`.
- Naming: `docs/file_naming_standard.md` (lowercase snake_case slug, dated deliverables).
- KPI and safety rules shared with the software: `docs/BUSINESS_RULES.md` in the `stayeasy-revenue-intelligence` repo.
- Client folders are created on Adam's Mac in `~/Documents/Projects/Stayeasy/clients/`, never inside this repo.

If the Mac folder is not reachable, ask Adam to connect `~/Documents/Projects` before doing anything. Never rebuild the template from memory.

## Steps

1. Ask only for what is missing, in one message: property name, property type, city, owner / decision-maker, offer (Gestion OTA & Revenue | Croissance Digitale Complète | Site Web Hôtelier | Site Web & Visibilité Google), inventory model (room-by-room | whole-property), reporting currency (MAD/EUR), client language (FR/EN). Take answers from the diagnostic form if Adam pastes it.
2. Choose `client_slug` (lowercase snake_case, e.g. `villa_example`). Check that no folder with that slug exists in any `clients/` lifecycle folder.
3. Copy the master folder to `~/Documents/Projects/Stayeasy/clients/onboarding/<client_slug>/`. Never edit the master.
4. Replace `{{PROPERTY_NAME}}`, `{{PROPERTY_TYPE}}`, `{{CITY}}`, `{{OWNER_NAME}}`, `{{OFFER}}`, `{{START_DATE}}`, `{{CURRENCY}}`, `{{CLIENT_LANGUAGE}}`, `{{INVENTORY_MODEL}}`, `{{STAYEASY_EMAIL}}` (default contact@stayeasy.ma) in every file. Unknown values stay `TBD`; never guess.
5. Put the diagnostic answers in `02_onboarding/intake/diagnostic_intake.md` (source and date on each line) and copy what fits into `00_client_control/client_manifest.md`.
6. Set `00_client_control/project_state.md` to phase 0 with today's date.
7. Reply to Adam with: the folder path, the filled `CLAUDE.md` to paste as the client's Claude project instructions, the two French lists to forward (`02_onboarding/access_setup/access_request_fr.md`, `02_onboarding/baseline/data_request_fr.md`), and the open `TBD` items.

## Rules

- One client per folder and per Claude project. Never copy data, rates, competitors or results from another client or from Adam's own properties (Riad Thaïs, Riad Saba, Riad Alaya).
- Never store passwords, 2FA codes or API keys.
- Do not contact the client; Adam forwards.
- Do not move the folder to `clients/active/` until the onboarding gate in the client information system passes.