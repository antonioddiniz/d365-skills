---
name: d365-limits-performance
description: Keep Dataverse / Dynamics 365 integrations, migrations and queries inside the platform limits - service protection API limits (429 Too Many Requests, Retry-After, 6,000 requests / 20 minutes execution / 52 concurrent per user per 5 minutes per web server), throttling-aware retry, parallelism versus batching, bulk messages, and query anti-patterns that cause timeouts (leading wildcards, too many columns, sorting by choice or joined columns, filtering on calculated columns). Use this skill whenever the user builds a data load, migration, nightly sync, ETL into or out of Dataverse, sees 429 / "Number of concurrent requests exceeded" / "Combined execution time" / PerformanceValidationIssuesCauseTimeout / LeadingWildcardCauseTimeout errors, or asks why a Dataverse query or job is slow.
---

# Dataverse limits and performance

The platform tells you how fast you may go. The client that listens to `Retry-After` finishes
first. The client that hammers gets longer and longer penalties.

## The limits (defaults, per user, per web server, 5-minute sliding window)

| Measure | Default | Error |
|---|---|---|
| Requests | 6,000 | 429, Retry-After |
| Combined execution time | 20 minutes (1,200 s) | `-2147015903` |
| Concurrent requests | 52 or higher | `-2147015898`, returned immediately |

These numbers can change and vary by environment. Do not hard-code them as a rate limiter.
Plug-ins and workflows calling Dataverse internally are not subject to these limits.
Entitlement (licensing) limits are separate and batching does not avoid them.

## How to move a lot of data

1. **Let the server set the pace.** Start low, ramp up, and on 429 wait exactly `Retry-After`
   seconds before sending more from that user. Never retry immediately in a tight loop.
2. **Parallel single requests beat big batches.** Bound the degree of parallelism with the value
   of the `x-ms-dop-hint` response header, which is the environment's recommended parallelism.
   `ServiceClient` (and `CrmServiceClient`) already wait `Retry-After` and resend for you.
3. **Batches: start at ~10 operations,** not 1,000. Large batches hit the execution-time limit
   instead of the request limit.
4. **Prefer bulk messages** (`CreateMultiple`, `UpdateMultiple`, `UpsertMultiple`) on tables that
   support them. Data must be clean: one error fails the call.
5. **Synchronous plug-ins are your hidden cost.** During a load, each row pays for every sync step.
   Consider the bypass optional parameter (privileged users only) or disabling steps during the
   window, and say clearly what logic is skipped.
6. **Several application users multiply throughput only if the business accepts it.** Limits are
   per user. Do not create identities just to evade governance.

## Query anti-patterns (Dataverse names them in the error)

| Anti-pattern id | Fix |
|---|---|
| `PerformanceLeadingWildCard` | No `like '%x'`, `ends-with`, or values starting with `_`, `[`, `-%`, `'%`. Use Dataverse search or redesign the data. |
| `LargeAmountOfAttributes` | Select only needed columns. Never `all-attributes` or no `$select`. |
| `LargeAmountOfLogicalAttributes` | Fewer logical columns (values stored in other tables). |
| `PerformanceLargeColumnSearch` | Do not filter on large text (memo) columns. |
| `OrderOnEnumAttribute` | Do not sort by choice columns. |
| `OrderOnPropertiesFromJoinedTables` | Do not sort by columns from link-entity / `$expand`. |
| `FilteringOnCalculatedColumns` | Filter on stored columns, not calculated or formula columns. |

Also: filter on indexed columns (primary keys, lookups, alternate keys), limit join depth, and
page with cookies. Simple FetchXML paging stops at 50,000 rows.

## Review checklist for a job or integration

- [ ] 429 handling reads `Retry-After` (Web API header or `OrganizationServiceFault.ErrorDetails["Retry-After"]`)?
- [ ] Bounded parallelism, no unbounded `Task.WhenAll` over thousands of rows?
- [ ] Batch size small and measured, not 1,000 by default?
- [ ] Bulk messages used where the table supports them?
- [ ] Every query has `$select`/attributes, deterministic order, cookie paging?
- [ ] None of the seven anti-patterns above?
- [ ] Sync plug-ins on the target table counted in the load plan?

## Output

For a job design: throughput plan (parallelism, batch size, bulk or not), retry policy, the list of
sync logic that runs per row, and the query fixes. For an error: the limit hit, the cause, the fix.

## References in this skill

- `references/retry-patterns.md` - retry loops for .NET SDK, Web API and PowerShell.

## Sources (Microsoft Learn)

- Service protection API limits: https://learn.microsoft.com/power-apps/developer/data-platform/api-limits
- API limits overview (service protection vs entitlement): https://learn.microsoft.com/power-apps/maker/data-platform/api-limits-overview
- Send parallel requests: https://learn.microsoft.com/power-apps/developer/data-platform/send-parallel-requests
- Optimize performance for bulk operations: https://learn.microsoft.com/power-apps/developer/data-platform/optimize-performance-create-update
- Query anti-patterns: https://learn.microsoft.com/power-apps/developer/data-platform/query-antipatterns
- Query throttling: https://learn.microsoft.com/power-apps/developer/data-platform/query-throttling
- Bypass custom business logic: https://learn.microsoft.com/power-apps/developer/data-platform/bypass-custom-business-logic
