# Client Information System

**Version:** 1.1  
**Status:** In Review  
**Owner:** Client Delivery  
**Date:** 2026-07-23  
**Review frequency:** Monthly  

## 1. Objective

Give every client one isolated, complete record from qualification through archive. A team member should be able to understand the agreement, contacts, systems, current priorities, decisions, work status, results, and risks without searching email or WhatsApp history.

## 2. Client lifecycle folders

| Folder | Entry condition | Exit condition |
|---|---|---|
| `clients/onboarding/` | Agreement approved or onboarding authorized | Access, baseline, kickoff, responsibilities, and first plan accepted |
| `clients/active/` | Onboarding gate passed | Paused, offboarding, or termination decision |
| `clients/paused/` | Written temporary suspension | Reactivation or offboarding decision |
| `clients/offboarding/` | End-of-service process opened | Access revoked, handover complete, records reconciled |
| `clients/archived/` | Offboarding accepted | Retention expiry or approved deletion decision |

Moving the folder changes lifecycle status. Do not create duplicate client folders in several statuses.

## 3. Standard client folder

```text
client-slug/
├── 00_client_control/
│   ├── client_manifest.md
│   ├── contacts_and_roles.md
│   ├── scope_and_responsibilities.md
│   ├── decision_log.md
│   ├── risk_and_issue_log.md
│   └── access_register.md
├── 01_commercial_legal/
│   ├── proposal/
│   ├── agreement/
│   ├── change_requests/
│   └── renewal/
├── 02_onboarding/
│   ├── intake/
│   ├── kickoff/
│   ├── access_setup/
│   └── baseline/
├── 03_source_data/
│   ├── pms/
│   ├── channel_manager/
│   ├── ota/
│   ├── website_analytics/
│   └── finance_inputs/
├── 04_delivery/
│   ├── revenue_management/
│   ├── ota_distribution/
│   ├── website_direct_booking/
│   ├── seo_google_business/
│   ├── marketing/
│   └── consulting/
├── 05_reporting/
│   ├── monthly/
│   ├── quarterly/
│   └── decision_packs/
├── 06_communications/
│   ├── meeting_notes/
│   ├── approvals/
│   └── formal_correspondence/
├── 07_assets/
│   ├── client_supplied/
│   ├── stayeasy_created/
│   └── approved_for_use/
├── 08_billing_reference/
├── 09_offboarding/
└── 99_archive/
```

Ready-to-copy master with all working documents: `templates/client_kit/` in this repo (approved 2026-10-25).

Billing reference contains invoice identifiers and status references; final finance records belong in the Phase 3 finance system.

## 4. Client manifest

Every client root contains `client_manifest.md` with:

- Legal and trading name
- Client slug and internal ID
- Property name, address, city, property type, and sellable keys
- Lifecycle status
- Account owner and delivery owner
- Decision-maker, financial contact, operational contact, emergency contact
- Contract start, term, renewal date, and notice period
- Approved service scope and exclusions
- Fee structure and source document link
- Systems in use
- Source-of-truth reports and data definitions
- Client communication channel and meeting cadence
- Data classification and retention category
- Open risks and dependencies
- Last updated date

## 5. Required control records

### Decision log

| Date | Decision | Reason | Decision-maker | Effective date | Affected records | Review date |
|---|---|---|---|---|---|---|

Record rate-policy guardrails, promotions, channel launches, scope changes, exception approvals, and material client instructions.

### Risk and issue log

| ID | Type | Description | Impact | Likelihood | Owner | Mitigation | Due date | Status |
|---|---|---|---|---|---|---|---|---|

Risks may happen; issues have happened. Keep them distinct.

### Access register

| System | Account owner | StayEasy user | Access level | Granted by/date | MFA | Last review | Revoke by |
|---|---|---|---|---|---|---|---|

Never place passwords in this register.

### Communication log

| Date | Channel | Participants | Subject | Decision/action | Owner | Due date | Evidence link |
|---|---|---|---|---|---|---|---|

Only material decisions and commitments need logging. Routine chat does not.

## 6. Onboarding file gate

A client cannot move to `active/` until:

- [ ] Signed/approved commercial authority exists
- [ ] First payment requirement is satisfied where applicable
- [ ] Scope, exclusions, and RACI are accepted
- [ ] Contacts and escalation path are confirmed
- [ ] Accounts are client-owned or ownership risk is documented
- [ ] Role-based access and MFA are configured
- [ ] Baseline data is received or missing-data risk is accepted
- [ ] KPI definitions and sources are agreed
- [ ] Kickoff meeting is complete
- [ ] First 30-day plan is approved
- [ ] Client folder and control records are complete

## 7. Active-client monthly file gate

Before monthly reporting closes:

- Source exports are saved with source and period in the filename.
- Data completeness issues are documented.
- Material actions appear in the decision log.
- Deliverables are stored in the correct service folder.
- The approved report is saved in `05_reporting/monthly/`.
- The sent date and recipient are recorded.
- Next actions have owners and dates in the task system.

## 8. Pausing and offboarding

### Pause

Document reason, effective date, billing treatment reference, services suspended, access retained, monitoring required, reactivation condition, and decision date.

### Offboarding

1. Confirm final service date and open commitments.
2. Export required records and deliver agreed handover.
3. Return or transfer client-owned assets and accounts.
4. Revoke StayEasy and contractor access.
5. Remove automations, forwarding, tokens, and integrations.
6. Confirm final report and outstanding issue ownership.
7. Record asset permissions and case-study rights after termination.
8. Move the folder to `archived/` only after the offboarding checklist is accepted.

## 9. Data minimization and retention

- Store only data required for contracted work, evidence, compliance, or dispute management.
- Avoid exporting guest names, contact details, identity documents, or payment data when aggregated reports are sufficient.
- Redact guest personal information before using screenshots in internal learning or marketing.
- Retention periods must be finalized in Phase 3 with Moroccan legal/accounting advice.
- Until then, do not permanently delete signed agreements, invoices, source performance evidence, access records, approvals, or disputes.

## 10. Common mistakes

- One folder named “clients” with mixed files.
- Client decisions stored only in WhatsApp.
- Reusable templates edited inside a client folder without preserving the approved master.
- Saving reports without the reporting period or approval status.
- Using the same credentials for several people.
- Keeping client access after offboarding.
- Calling a client active before scope, access, and data are ready.

