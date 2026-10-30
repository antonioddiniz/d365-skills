---
name: d365-flow-reliability
description: Make Power Automate cloud flows that touch Dataverse / Dynamics 365 reliable and cheap to run - trigger filtering (select columns, filter rows, trigger conditions, scope), try/catch/finally with Scope and Configure run after, retry policies, idempotency against duplicate triggers, Apply to each concurrency, List rows paging and FetchXML, throughput limits, connection references and run-only users. Use this skill whenever the user designs or reviews a flow on "When a row is added, modified or deleted", a flow that runs too often or loops, fails silently, creates duplicates, hits throttling or 5,000-row limits, needs error notifications, or will be moved to another environment - even if they only paste a flow definition JSON or a screenshot description.
---

# Reliable Dataverse flows

A flow that triggers on every save of a busy table is a plug-in without a debugger. Filter first,
then handle failure, then make re-runs harmless.

## Trigger: run only when it matters

1. **Change type** only for the events you handle (Added, Modified, Deleted).
2. **Select columns** (Modified only) to the columns that matter. The flow fires when a listed
   column is *in the update request*, even with the same value. Never list the primary key or
   columns that every update sends. Lookup columns are not supported in Select columns.
3. **Filter rows** with an OData expression (no `$filter=` prefix) so the flow runs only when
   the row qualifies after the save: `statecode eq 0 and revenue gt 100000`.
4. **Trigger conditions** for logic OData cannot express. They stop the run before it costs anything.
5. **Scope** (User, BU, Parent:Child, Organization) is about whose rows trigger the flow.
   Integrations usually need Organization.
6. **Loop guard:** a flow that updates the same row it triggers on must not list that column in
   Select columns, or must compare before writing.

## Failure: try, catch, finally

- Put the work in a **Scope "Try"**. Add **Scope "Catch"** with Configure run after =
  has failed / has timed out. Add **Scope "Finally"** after both if cleanup is needed.
- In Catch, read the error with `result('Try')` filtered to failed actions, log it with the run
  URL built from `workflow()`, then **terminate as Failed** so monitoring sees the failure.
- Do not catch and continue silently. A green run that did nothing is the worst outcome.

## Retries and idempotency

- Connector actions retry by default (exponential, up to 4 retries for most). For calls that hit a
  slow dependency, set an explicit exponential policy with longer intervals.
- **Retries and duplicate triggers happen.** Make writes idempotent: upsert by alternate key,
  check-before-create, or store a processed marker. Never "Add a new row" blindly in a retried path.
- 429 from Dataverse is handled by the connector retry. Do not add a "Delay 1 minute and try again"
  loop on top of it.

## Volume

- **List rows** returns up to 5,000 rows by default. Turn on pagination with a threshold or loop on
  the skip token for more, and always set Select columns and Filter rows.
- **Apply to each** runs sequentially by default. Concurrency (1 to 50) helps only at the top level:
  nested loops run sequentially. Never use concurrency with variables you append to.
- Prefer one FetchXML query with aggregates or a Dataverse bulk/Custom API call over thousands
  of loop iterations.
- Throughput limits depend on the flow's performance profile. A flow that stays above them for
  14 days is turned off.

## Portability

- Flows live in solutions, use **connection references**, and read URLs and ids from
  **environment variables**. No hard-coded GUIDs, environment URLs or personal connections.
- The owner is a service account or service principal, not the person who built it.

## Review checklist

- [ ] Trigger has Change type, Select columns and Filter rows set, or a stated reason why not?
- [ ] No self-trigger loop?
- [ ] Try/Catch/Finally scopes, Catch terminates as Failed and logs the run URL?
- [ ] Writes are idempotent under retry and duplicate trigger?
- [ ] List rows has Select columns, Filter rows, and paging if it can exceed 5,000?
- [ ] Concurrency used only where order and shared variables do not matter?
- [ ] Connection references, environment variables, service-account owner?

## Output

Return the issues by severity with the exact setting to change (trigger property, action setting,
expression), and the corrected trigger and Catch scope.

## References in this skill

- `references/expressions.md` - trigger conditions, error extraction, run URL, idempotency patterns.

## Sources (Microsoft Learn)

- Dataverse trigger (filter columns, filter rows, scope): https://learn.microsoft.com/power-automate/dataverse/create-update-delete-trigger
- Optimize triggers (trigger conditions): https://learn.microsoft.com/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers
- Robust error handling (scopes, run after, retry): https://learn.microsoft.com/power-automate/guidance/coding-guidelines/error-handling
- Work only with relevant data: https://learn.microsoft.com/power-automate/guidance/coding-guidelines/work-with-relevant-data
- Parallel execution and concurrency: https://learn.microsoft.com/power-automate/guidance/coding-guidelines/implement-parallel-execution
- List rows (paging, FetchXML): https://learn.microsoft.com/power-automate/dataverse/list-rows
- Limits and configuration: https://learn.microsoft.com/power-automate/limits-and-config
- Default retry policy behavior: https://learn.microsoft.com/azure/logic-apps/error-exception-handling#retry-policies
