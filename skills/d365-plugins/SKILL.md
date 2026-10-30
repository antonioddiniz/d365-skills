---
name: d365-plugins
description: Write, review and debug Dataverse / Dynamics 365 server-side code in C# - plug-ins (IPlugin), Custom APIs, custom workflow activities and their step registration (stage, mode, filtering attributes, images). Use this skill whenever the user mentions a plug-in, IPluginExecutionContext, IOrganizationService inside a plug-in, PreValidation/PreOperation/PostOperation, pre/post images, InvalidPluginExecutionException, Custom API, the Plug-in Registration Tool, "pac plugin", a plug-in timeout, an infinite loop between plug-ins, or SQL timeouts and rollbacks caused by business logic - even if they only paste a C# class that implements Execute(IServiceProvider).
---

# Dataverse plug-ins and Custom APIs

A plug-in runs inside the user's database transaction. Every second it spends is a second a user
waits, and every exception it throws rolls back somebody's save. Write it like code that runs in
someone else's checkout line.

## Hard limits (from the platform, not opinions)

| Limit | Value | What it means for the code |
|---|---|---|
| Message operation timeout | 2 minutes, including every sync and async step | Long work does not belong in a plug-in. Move it to async, Power Automate or Azure. |
| Target for one plug-in | 2 seconds or less | Above that, register asynchronous unless the result must be in the same transaction. |
| Depth | max 8 within one hour (default) | The platform kills loops. Do not use `context.Depth` as business logic: depth changes with every new code path. |
| Sandbox | CPU, memory, handle limits | Exceeding them kills the worker process. No threads, no static mutable state. |

## Choose the stage on purpose

| Stage | Transaction | Use it to |
|---|---|---|
| PreValidation (10) | Usually outside. Inside if another operation triggered it. Check `context.IsInTransaction`. | Reject the operation early with `InvalidPluginExecutionException`. Cheapest place to cancel. |
| PreOperation (20) | Inside | Change values on `Target` before they are saved. No extra Update call needed. |
| PostOperation (40), sync | Inside | Work that needs the record id or must roll back with the save. |
| PostOperation (40), async | Outside | Anything slow, external, or that can be retried. The default choice when in doubt. |

Cancel in PreValidation, not PreOperation. Rolling back a transaction costs the database real work.

## Rules that prevent the classic incidents

1. **Never call Update on the Target in Pre/PostOperation of its own Update.** Change `Target` in
   PreOperation instead. Updating the same row from PostOperation fires the pipeline again.
2. **Register filtering attributes on every Update step.** Without them the step fires on every save
   of the row, including saves from other plug-ins and integrations.
3. **Use images, not Retrieve.** Ask for a PreImage/PostImage with only the columns you read.
   A `Retrieve` with `new ColumnSet(true)` inside a sync step is the most common slow plug-in.
4. **Read Target defensively.** On Update, `Target` holds only the changed columns. A missing key
   is "not changed", not null. Merge Target over the PreImage to get the effective value.
5. **Stateless class.** The platform caches plug-in instances and runs them on several threads.
   No instance fields that change per execution, no static caches of business data.
6. **Throw `InvalidPluginExecutionException` with a plain-text message** for business errors.
   Other exception types show the user a generic error. The message cannot contain HTML.
7. **Trace, do not log to external sinks synchronously.** Use `ITracingService` (and `ILogger`
   where available). Plug-in Trace Log must be enabled to see traces.
8. **External HTTP calls:** set a timeout well under 2 minutes, set `KeepAlive = false`, handle
   failure without leaving the transaction half-done. Better: emit the event and call out async.
9. **Do not send `CreateMultiple`/`UpdateMultiple` from inside a plug-in.** They are for client
   apps. Do register plug-ins on them when bulk performance matters (see references).
10. **Elastic tables break the rollback rule.** Writes in PreOperation/PostOperation are not
    transactional there. Validate in PreValidation.

## Custom API instead of a "fake" plug-in

Use a Custom API when the caller wants an operation (verb), not a side effect of saving a row.

- The plug-in implements the main operation: read `InputParameters`, set `OutputParameters`.
  Register the assembly and type, but no step.
- Unique names, types and `IsOptional` cannot change after creation. Design them before creating.
- Protect it with `ExecutePrivilegeName` using an existing privilege.
- Ship it in a managed solution with **Is Customizable = false** on the API, each request
  parameter and each response property.
- `Enabled for Workflow` forbids functions and the Entity, EntityCollection and StringArray types.

## Review checklist

When reviewing plug-in code or a step registration, answer each line with OK, RISK or FIX:

- [ ] Stage and mode match the intent (validation, mutation, side effect)?
- [ ] Update steps have filtering attributes? Images ask only for columns used?
- [ ] No Retrieve with all columns, no query inside a loop?
- [ ] No Update of the Target from its own pipeline? Loop guard is not based on Depth?
- [ ] No static mutable state, no threads, no `async void`?
- [ ] Business errors use `InvalidPluginExecutionException` with a short text message?
- [ ] External calls have a timeout and `KeepAlive = false`, or move to async?
- [ ] Unit tests cover Create, Update with partial Target, and the error path?

## Output

Return: the risks found (severity, line, why it breaks in production), the corrected code, and the
registration to use (message, table, stage, mode, filtering attributes, images). For new code,
start from `references/plugin-skeleton.md`.

## References in this skill

- `references/plugin-skeleton.md` - base class, Target/PreImage merge, tracing, Custom API body.

## Sources (Microsoft Learn)

- Event execution pipeline: https://learn.microsoft.com/power-apps/developer/data-platform/event-framework
- Analyze plug-in performance (2 minutes, 2 seconds): https://learn.microsoft.com/power-apps/developer/data-platform/analyze-performance
- Best practices for plug-ins: https://learn.microsoft.com/power-apps/developer/data-platform/best-practices/business-logic/
- Handle exceptions in plug-ins: https://learn.microsoft.com/power-apps/developer/data-platform/handle-exceptions
- Depth and loop prevention: https://learn.microsoft.com/dotnet/api/microsoft.xrm.sdk.iexecutioncontext.depth
- Database transactions: https://learn.microsoft.com/power-apps/developer/data-platform/scalable-customization-design/database-transactions
- Create and use Custom APIs: https://learn.microsoft.com/power-apps/developer/data-platform/custom-api
- Plug-ins for CreateMultiple/UpdateMultiple: https://learn.microsoft.com/power-apps/developer/data-platform/write-plugin-multiple-operation
- Elastic tables transactional behavior: https://learn.microsoft.com/power-apps/developer/data-platform/elastic-tables
