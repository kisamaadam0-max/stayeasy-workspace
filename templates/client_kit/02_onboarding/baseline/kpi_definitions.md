# KPI definitions

**Version:** 1.0  
**Status:** Approved  
**Owner:** Client Delivery  
**Date:** 2026-10-25  

Same definitions for every client, so reports are comparable over time. Each report states the period, the source export and its date. The onboarding gate requires these definitions to be agreed with the client. Core KPIs follow `docs/BUSINESS_RULES.md` in the `stayeasy-revenue-intelligence` repo, which the software implements and tests; if that file changes, update this one. KPIs marked *kit addition* are not yet in the software and are calculated in Python from the exports.

| KPI | Formula | Notes |
|---|---|---|
| Available room nights | sellable units × nights in period | Whole-property rental: 1 unit. Units closed for works excluded only if the owner confirms it. |
| Occupancy | occupied room nights ÷ available room nights × 100 | Count by stay date, cancelled excluded. |
| ADR | recognized room revenue ÷ occupied room nights | State whether tourist tax, VAT and breakfast are included. Default: excluded. |
| RevPAR | recognized room revenue ÷ available room nights | Check it equals Occupancy × ADR. |
| Booking window | mean days between booking creation and arrival, active reservations in the stay window | Also show the median when a few long-lead bookings skew the mean. |
| Cancellation rate | cancelled reservations ÷ all reservations in the stay window × 100 | Also by channel. |
| Channel mix | occupied room nights per normalized channel ÷ total occupied room nights | |
| Direct share | direct occupied room nights ÷ total occupied room nights × 100 | Direct = website engine, phone, email, WhatsApp. |
| Pickup | occupied room nights created during the lookback window and intersecting the stay window | Always state the lookback window and stay window. |
| On the books (OTB) — *kit addition* | confirmed room nights for future dates as of a snapshot date | Always quote the snapshot date. |
| Net revenue — *kit addition* | room revenue − OTA commission − payment fees | Use each channel's actual commission from contracts or invoices, never an assumed rate. |
| Net ADR — *kit addition* | net revenue ÷ occupied room nights | Per channel and total. |
| Average length of stay — *kit addition* | occupied room nights ÷ reservations | |

## Data checks before any KPI

Missing dates, duplicate bookings, test bookings, impossible values (occupancy > 100%, negative revenue, zero price with nights sold), export period not matching the request, empty files. Flag what was found and how it was handled.

Small properties: with 10 units or fewer, one booking moves occupancy by 10 points or more. Do not call a change a trend without at least several weeks of data.
