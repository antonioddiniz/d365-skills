# Web API cookbook

`{org}` is the environment URL (for example `https://yourorg.crm.dynamics.com`). Read it from
configuration. Tokens come from MSAL or managed identity, never from source code.

Common headers on every request:

```http
Accept: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
Authorization: Bearer <token-from-config>
```

## Read everything, page by page (TypeScript)

```ts
async function getAll<T>(url: string, token: string, pageSize = 1000): Promise<T[]> {
  const rows: T[] = [];
  let next: string | undefined = url;
  while (next) {
    const res = await fetchWithRetry(next, {
      headers: {
        Accept: "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        Authorization: `Bearer ${token}`,
        Prefer: `odata.maxpagesize=${pageSize}, odata.include-annotations="*"`,
      },
    });
    const body = await res.json();
    rows.push(...body.value);
    next = body["@odata.nextLink"]; // use as-is, never edit it
  }
  return rows;
}

// 429 handling: honor Retry-After, back off, give up after a few tries.
async function fetchWithRetry(url: string, init: RequestInit, max = 5): Promise<Response> {
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(url, init);
    if (res.status !== 429 || attempt >= max) {
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      return res;
    }
    const wait = Number(res.headers.get("Retry-After") ?? 5);
    await new Promise(r => setTimeout(r, wait * 1000));
  }
}

const url = `${org}/api/data/v9.2/accounts?$select=name,accountnumber,_primarycontactid_value`
          + `&$filter=statecode eq 0&$orderby=name,accountid`;
```

## Set a customer lookup on create

```http
POST {org}/api/data/v9.2/contacts
Content-Type: application/json

{
  "firstname": "Ana",
  "lastname": "Example",
  "parentcustomerid_account@odata.bind": "/accounts(00000000-0000-0000-0000-000000000001)"
}
```

Wrong: `"parentcustomerid@odata.bind"`. That property does not exist and the call fails with
"An undeclared property was found in the payload".

## Upsert by alternate key, create-only and update-only

```http
PATCH {org}/api/data/v9.2/contoso_orders(contoso_externalid='ERP-1001')
Content-Type: application/json

{ "contoso_amount": 120.5 }
```

- Add `If-Match: *` for update-only (404 if missing).
- Add `If-None-Match: *` for create-only (412 if it exists).
- Add `Prefer: return=representation` plus `$select=contoso_orderid` if you must know which one happened (201 created, 200 updated). It costs an extra read.

## Optimistic concurrency

```http
PATCH {org}/api/data/v9.2/accounts(00000000-0000-0000-0000-000000000001)
If-Match: W/"468026"
Content-Type: application/json

{ "creditlimit": 50000 }
```

412 means the row changed after you read it.

## FetchXML with paging cookie

```http
GET {org}/api/data/v9.2/accounts?fetchXml=<url-encoded fetch>
Prefer: odata.include-annotations="Microsoft.Dynamics.CRM.fetchxmlpagingcookie,Microsoft.Dynamics.CRM.morerecords"
```

While `@Microsoft.Dynamics.CRM.morerecords` is true: take the `pagingcookie` attribute of the
returned `@Microsoft.Dynamics.CRM.fetchxmlpagingcookie` element, URL-decode it **twice**, XML-encode
it into the `paging-cookie` attribute, increment `page`, keep `count`, then URL-encode the whole
FetchXML again. Always end the `<order>` list with the primary key.

## Bulk create

```http
POST {org}/api/data/v9.2/contoso_readings/Microsoft.Dynamics.CRM.CreateMultiple
Content-Type: application/json

{
  "Targets": [
    { "@odata.type": "Microsoft.Dynamics.CRM.contoso_reading", "contoso_value": 1 },
    { "@odata.type": "Microsoft.Dynamics.CRM.contoso_reading", "contoso_value": 2 }
  ]
}
```

One invalid item fails the whole request. Validate before sending, keep batches modest, run a few
in parallel, and retry 429 with `Retry-After`.
