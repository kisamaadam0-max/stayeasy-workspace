# Source data – {{PROPERTY_NAME}}

**Version:** 1.0  
**Status:** Approved  
**Owner:** Client Delivery  
**Date:** 2026-10-25  

- One subfolder per system. Exports are saved exactly as received or downloaded and never edited.
- Name: `YYYY-MM-DD_<source>_<content>_<period>.csv` (date = export date).
- Each file gets one line in `exports_log.csv` with the result of the data checks in `02_onboarding/baseline/kpi_definitions.md`.
- Remove guest names, emails and phone numbers when an aggregated export is enough.
