# Retry patterns for service protection limits

## .NET (Dataverse ServiceClient / IOrganizationService)

`ServiceClient` already retries service protection errors by default. If you call
`IOrganizationService` through another wrapper, read the wait time from the fault:

```csharp
static TResult ExecuteWithRetry<TResult>(Func<TResult> call, int maxRetries = 5)
{
    for (int attempt = 0; ; attempt++)
    {
        try { return call(); }
        catch (FaultException<OrganizationServiceFault> ex) when (
            attempt < maxRetries &&
            ex.Detail.ErrorDetails.TryGetValue("Retry-After", out var retryAfter))
        {
            Thread.Sleep((TimeSpan)retryAfter); // the server decides the wait
        }
    }
}
```

The three service protection codes are `-2147015902` (number of requests), `-2147015903`
(execution time) and `-2147015898` (concurrent requests).

## Bounded parallelism (.NET)

```csharp
// Use ServiceClient.RecommendedDegreesOfParallelism (from the x-ms-dop-hint header) when available.
var options = new ParallelOptions { MaxDegreeOfParallelism = client.RecommendedDegreesOfParallelism };
await Parallel.ForEachAsync(batches, options, async (batch, ct) =>
{
    await SendBatchWithRetryAsync(batch, ct);
});
```

Start low. Raise it while 429s stay rare. Clone or pool the client per thread as the SDK
documentation recommends.

## Web API (any language)

Read the `Retry-After` header (seconds) on a 429 and sleep that long. See the TypeScript
`fetchWithRetry` in the `d365-webapi` cookbook.

## PowerShell

`Invoke-RestMethod -MaximumRetryCount 3 -RetryIntervalSec 5` honors `Retry-After` on 429, but it
also retries every 4xx/5xx. For scripts, wrap the call and retry only 429.
