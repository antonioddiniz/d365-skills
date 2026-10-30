# Plug-in skeleton and patterns

All names below (`contoso_`, `sample_`) are placeholders. Replace them with your publisher prefix.

## Base plug-in with tracing and effective values

```csharp
using System;
using Microsoft.Xrm.Sdk;

public sealed class AccountCreditLimitPlugin : IPlugin
{
    // No instance fields that change per execution: the platform caches and reuses this object.
    private readonly string _unsecureConfig;

    public AccountCreditLimitPlugin(string unsecureConfig, string secureConfig)
    {
        _unsecureConfig = unsecureConfig; // read-only after construction
    }

    public void Execute(IServiceProvider serviceProvider)
    {
        var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
        var tracing = (ITracingService)serviceProvider.GetService(typeof(ITracingService));

        if (!context.InputParameters.TryGetValue("Target", out var t) || !(t is Entity target))
            return;

        // On Update, Target holds only changed columns. Merge it over the PreImage.
        context.PreEntityImages.TryGetValue("PreImage", out var pre);
        Money limit = Effective<Money>(target, pre, "creditlimit");
        tracing.Trace("creditlimit effective = {0}", limit?.Value);

        if (limit != null && limit.Value < 0)
        {
            // Plain text only. Thrown in PreValidation, it cancels before the transaction.
            throw new InvalidPluginExecutionException("Credit limit cannot be negative.");
        }
    }

    private static T Effective<T>(Entity target, Entity pre, string column)
    {
        if (target.Attributes.ContainsKey(column)) return target.GetAttributeValue<T>(column); // changed (may be null on purpose)
        return pre != null ? pre.GetAttributeValue<T>(column) : default;                       // unchanged
    }
}
```

Registration for this example: message `Update`, table `account`, stage PreValidation, sync,
filtering attributes `creditlimit`, PreImage named `PreImage` with column `creditlimit` only.
Add a second step on `Create` without an image.

## Changing values: do it in PreOperation, on the Target

```csharp
// Stage 20 (PreOperation). No service.Update call: the platform saves Target.
target["contoso_normalizedname"] = (target.GetAttributeValue<string>("name") ?? "").Trim().ToUpperInvariant();
```

## Calling an external service (async step)

```csharp
using var http = new System.Net.Http.HttpClient { Timeout = TimeSpan.FromSeconds(15) };
http.DefaultRequestHeaders.ConnectionClose = true; // KeepAlive = false
// Read the endpoint from an environment variable or secure config. Never hard-code secrets.
```

## Custom API main operation

```csharp
public sealed class CalculateDiscountApi : IPlugin
{
    public void Execute(IServiceProvider serviceProvider)
    {
        var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
        // Request parameter unique name: Amount (Decimal, required)
        var amount = (decimal)context.InputParameters["Amount"];
        // Response property unique name: Discount (Decimal)
        context.OutputParameters["Discount"] = amount >= 1000m ? amount * 0.05m : 0m;
    }
}
```

Register the assembly and the type. Set the Custom API **Plugin Type** to this class. Do not register a step.

## Unit test shape

Test three cases for every Update plug-in: Create, Update where the column is in Target,
Update where it is not (value comes from the PreImage). Any mocking framework or a fake
`IServiceProvider` works. The point is to prove the partial-Target behavior, which is where most
plug-in bugs live.
