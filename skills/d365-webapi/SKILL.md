---
name: d365-webapi
description: Correct Dataverse Web API (OData v4) requests in any language - TypeScript, JavaScript, C#, PowerShell, Python or raw HTTP. Covers paging with odata.maxpagesize and @odata.nextLink, FetchXML paging cookies, $select/$filter/$expand, formatted values and annotations, setting lookups with @odata.bind (including customer and owner polymorphic lookups), upsert with alternate keys, If-Match/ETag concurrency, $batch and the bulk messages. Use this skill whenever code calls /api/data/v9.x, builds an OData query against Dynamics 365 or Dataverse, gets "An undeclared property was found in the payload", only returns 5,000 rows, writes an integration or sync with Dataverse, or uses Xrm.WebApi - even if the user just says "pull the accounts from Dynamics".
---

# Dataverse Web API, done right

Most Web API bugs are silent: the call succeeds and returns the wrong amount of data, or writes a
lookup to nowhere. The rules below target those silent failures first.

## Reading

1. **Always `$select`.** Without it you get every column, which is slow and can time out.
   The primary key comes back anyway.
2. **Page with the header, not with `$top`.** Send `Prefer: odata.maxpagesize=N` (N up to 5,000)
   and follow `@odata.nextLink` until it is absent. `$skip` is not supported. `$top` together with
   maxpagesize is ignored.
3. **Do not touch the nextLink.** Use it exactly as returned, with the same maxpagesize. The
   `$skiptoken` inside is opaque.
4. **Order deterministically.** Include a unique column (the primary key) at the end of `$orderby`.
   Paging over a non-unique sort can skip or repeat rows.
5. **FetchXML paging:** use `count`, `page` and the returned `paging-cookie`. Never combine with
   `top`. Simple paging (no cookie) stops at 50,000 rows. Elastic tables page at 500.
6. **Ask for annotations when you show values to people:**
   `Prefer: odata.include-annotations="*"` returns `@OData.Community.Display.V1.FormattedValue`
   for choices, lookups, money and dates. Do not rebuild option labels by hand.
7. **Read lookups through `_name_value`.** For polymorphic lookups (`customerid`, `ownerid`,
   `regardingobjectid`) also read `@Microsoft.Dynamics.CRM.lookuplogicalname` to know the table.
8. **`$count=true` caps at 5,000.** For larger totals use an aggregate query.

## Writing

1. **Set lookups with the single-valued navigation property + `@odata.bind`:**
   `"parentcustomerid_account@odata.bind": "/accounts(<guid>)"`. The navigation property name is
   case-sensitive and often differs from the column name. Polymorphic lookups have one property per
   target table (`parentcustomerid_account`, `parentcustomerid_contact`). Confirm the name in
   `$metadata` or in the relationship's `ReferencingEntityNavigationPropertyName`. Never guess.
2. **Clear a lookup** by sending the navigation property (without `@odata.bind`) as `null`, or
   `DELETE .../navprop/$ref`.
3. **Update vs upsert is one header.** `PATCH` with `If-Match: *` is a pure update (404 if missing).
   `PATCH` without it is an upsert. `If-None-Match: *` makes it create-only (412 if it exists).
4. **Upsert by alternate key** in the URL: `/contoso_things(contoso_externalid='A-42')`. Do not repeat
   the key columns in the body.
5. **Optimistic concurrency:** send the `@odata.etag` you read in `If-Match`. A 412 means someone
   changed the row. Re-read and decide, do not blindly retry.
6. **Send only changed columns.** Every column in the body counts as "changed" for plug-in filtering
   attributes, flow triggers and auditing.
7. **Bulk:** prefer `CreateMultiple`/`UpdateMultiple`/`UpsertMultiple` for tables that support them
   (each item needs `@odata.type`). One bad record fails the whole call, so validate first.
   Otherwise use `$batch` (up to 1,000 operations, start with ~10) with parallel requests.
   Change sets are atomic. Elastic tables do not honor that atomicity.

## Errors to handle on every call

| Status | Meaning | Do |
|---|---|---|
| 429 | Service protection limit | Wait `Retry-After` seconds, then retry. See `d365-limits-performance`. |
| 412 | ETag or If-None-Match precondition failed | Re-read, merge or report. |
| 404 on PATCH with If-Match | Row gone | Do not recreate silently. |
| 400 "undeclared property" | Wrong navigation property name | Look it up in `$metadata`. |

## Output

When writing or fixing code: return the corrected request (method, URL, headers, body) and the
client code, with paging and 429 handling included. Never put a real org URL, client secret or
token in examples. Read them from configuration.

## References in this skill

- `references/http-cookbook.md` - copy-ready requests: paging loop, lookups, upsert, ETag, batch, bulk.

## Sources (Microsoft Learn)

- Page results with OData: https://learn.microsoft.com/power-apps/developer/data-platform/webapi/query/page-results
- Page results with FetchXML: https://learn.microsoft.com/power-apps/developer/data-platform/fetchxml/page-results
- Select columns and lookup annotations: https://learn.microsoft.com/power-apps/developer/data-platform/webapi/query/select-columns
- Associate and disassociate rows: https://learn.microsoft.com/power-apps/developer/data-platform/webapi/associate-disassociate-table-rows
- Multi-table lookups: https://learn.microsoft.com/power-apps/developer/data-platform/webapi/multitable-lookup
- Upsert a table row: https://learn.microsoft.com/power-apps/developer/data-platform/use-upsert-insert-update-record
- Conditional operations (ETag): https://learn.microsoft.com/power-apps/developer/data-platform/webapi/perform-conditional-operations-using-web-api
- Bulk operation messages: https://learn.microsoft.com/power-apps/developer/data-platform/bulk-operations
- Batch operations: https://learn.microsoft.com/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api
- Web API client errors: https://learn.microsoft.com/troubleshoot/power-platform/dataverse/dataverse-web-api-and-sdk/web-api-client-errors
