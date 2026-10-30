---
name: d365-crm-data-model
description: Work correctly with the standard Dynamics 365 Sales and Customer Service data model from code, flows or queries - account, contact, lead, opportunity, quote, incident (case), activities and activityparty, statecode/statuscode pairs, the special messages that change lifecycle (QualifyLead, WinOpportunity, LoseOpportunity, CloseIncident, CloseQuote), customer and regarding polymorphic lookups, owner (user or team), and currency fields. Use this skill whenever code or a flow creates or closes leads, opportunities or cases, sends or logs emails, phone calls or appointments with To/From/attendees, sets statecode or statuscode, reports on the sales pipeline or case resolution, or migrates CRM data - even if the user just says "mark the deal as won" or "log this call against the customer".
---

# The Dynamics 365 CRM data model, from code

Sales and Service tables are not plain tables. Some state changes are business operations that
create related records, and activities keep their people in a separate table. Treating them as
plain CRUD produces records that look right in the grid and wrong in every report.

## Lifecycle changes go through their messages

| Goal | Use | Not |
|---|---|---|
| Qualify a lead | `QualifyLead` (CreateAccount, CreateContact, CreateOpportunity, Status 3 = Qualified) | Patching `statecode` on the lead |
| Disqualify a lead | Update `statecode` = 2 with a valid disqualified `statuscode` | Deleting the lead |
| Win an opportunity | `WinOpportunity` with an `opportunityclose` (opportunityid, actualrevenue, subject) and Status 3 | Patching `statecode` = 1 |
| Lose an opportunity | `LoseOpportunity` with an `opportunityclose` (competitor optional) and Status 4 Canceled or 5 Out-Sold | Patching `statecode` = 2 |
| Resolve a case | `CloseIncident` with an `incidentresolution` (incidentid, subject) and Status 5 Problem Solved or 1000 Information Provided | Patching `statecode` = 1 |
| Close a quote | `CloseQuote` with a `quoteclose` | Patching `statecode` |

Why: these messages create the close activity, keep revenue and resolution history, and run the
platform logic (forecasting, SLA, business process flow). An opportunity must have no open quotes
before it closes. Run each message with privileges on the related tables.

## statecode and statuscode

- `statecode` (Status) is fixed per table. `statuscode` (Status Reason) values belong to one state.
  An invalid pair fails.
- Read the real values from metadata (`StatusAttributeMetadata`) or the formatted-value annotation.
  Do not hard-code labels: environments add custom status reasons.
- Tables with enforced transitions (cases, custom tables) only accept allowed `statuscode` moves.

## Activities and their parties

- Email, phone call, appointment, letter and fax keep To/From/Cc/attendees as **activityparty** rows,
  not lookups. Send them as an array in the navigation property (for example `email_activity_parties`)
  with `participationtypemask`: 1 Sender, 2 To, 3 Cc, 4 Bcc, 5 Required attendee, 6 Optional,
  7 Organizer, 8 Regarding, 9 Owner, 10 Resource, 11 Customer.
- `regardingobjectid` links the activity to the account, opportunity or case. It is polymorphic:
  bind it with the table-specific navigation property (for example `regardingobjectid_account_email`).
- Creating an email record does not send it. Use `SendEmail` (or `SendEmailFromTemplate`) after creation.

## Polymorphic lookups you will meet

| Column | Targets | Bind with |
|---|---|---|
| `parentcustomerid` (contact) | account, contact | `parentcustomerid_account` / `parentcustomerid_contact` |
| `customerid` (opportunity, incident) | account, contact | `customerid_account` / `customerid_contact` |
| `ownerid` (most tables) | systemuser, team | `ownerid` with `/systemusers(id)` or `/teams(id)` |
| `regardingobjectid` (activities) | many | `regardingobjectid_<table>_<activity>` |

Confirm every navigation property name in `$metadata`. They are case-sensitive.

## Money and currency

Money columns have a base-currency twin (`revenue` and `revenue_base`). Set
`transactioncurrencyid` on create when the org has several currencies. Report in `_base` columns to
sum across currencies.

## Review checklist

- [ ] No direct `statecode` patch where a lifecycle message exists?
- [ ] Close activities carry the data reports need (actual revenue, competitor, resolution subject)?
- [ ] statuscode values read from metadata, valid for the target state?
- [ ] Activity parties sent as activityparty arrays with the right participation types?
- [ ] Emails that must go out are sent with SendEmail?
- [ ] Polymorphic lookups bound with the table-specific navigation property?
- [ ] Multi-currency reports use `_base` columns?

## Output

Return the corrected operation (message name, parameters, request body) and explain which related
records it creates, so the reader can check them in the app.

## References in this skill

- `references/lifecycle-requests.md` - Web API requests for qualify, win, lose, resolve and email with parties.

## Sources (Microsoft Learn)

- QualifyLeadRequest: https://learn.microsoft.com/dotnet/api/microsoft.crm.sdk.messages.qualifyleadrequest
- WinOpportunityRequest: https://learn.microsoft.com/dotnet/api/microsoft.crm.sdk.messages.winopportunityrequest
- Close opportunities as won or lost: https://learn.microsoft.com/dynamics365/sales/close-opportunity-won-lost-sales
- CloseIncidentRequest: https://learn.microsoft.com/dotnet/api/microsoft.crm.sdk.messages.closeincidentrequest
- Define custom state model transitions: https://learn.microsoft.com/power-apps/developer/data-platform/define-custom-state-model-transitions
- Table states (statecode/statuscode): https://learn.microsoft.com/power-apps/developer/data-platform/entity-metadata#table-states
- ActivityParty table: https://learn.microsoft.com/power-apps/developer/data-platform/activityparty-entity
- Multi-table lookups: https://learn.microsoft.com/power-apps/developer/data-platform/webapi/multitable-lookup
- Opportunity Close table reference: https://learn.microsoft.com/dynamics365/developer/reference/entities/opportunityclose
