# Flow expressions and patterns

## Trigger condition (only when status reason is "Approved" = 100000001)

```
@equals(triggerOutputs()?['body/statuscode'], 100000001)
```

Prefer Filter rows when OData can express it: `statuscode eq 100000001`.

## Catch scope: get the failed action messages

Filter array on `result('Try')` where `item()?['status']` is equal to `Failed`, then:

```
first(body('Filter_array'))?['error']?['message']
```

## Run URL for the alert

After Parse JSON on `workflow()`:

```
https://make.powerautomate.com/environments/@{body('Parse_JSON')?['tags']?['environmentName']}/flows/@{body('Parse_JSON')?['tags']?['logicAppName']}/runs/@{body('Parse_JSON')?['run']?['name']}
```

## Idempotent create

1. List rows on the target table with Filter rows `contoso_externalid eq '<id>'` and Row count 1.
2. Condition on `length(outputs('List_rows')?['body/value'])` equal to 0, then Add, else Update.

Better, when the table has an alternate key: one Upsert through the Dataverse connector's
"Upsert a row" or an HTTP request with Dataverse `PATCH` by key. One call, no race.

## Guard against self-trigger

Trigger on Modified with Select columns `contoso_status`. The flow writes `contoso_lastsync` only.
Because `contoso_lastsync` is not in Select columns, the flow's own update does not trigger it.
