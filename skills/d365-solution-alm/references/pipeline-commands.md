# pac CLI release commands

Authenticate with a service principal in CI. Never commit secrets: use the pipeline's secret store.

```bash
# 1. Export from dev (unmanaged for source control, managed for deployment)
pac solution export --name ContosoCore --path out/ContosoCore.zip --managed false
pac solution export --name ContosoCore --path out/ContosoCore_managed.zip --managed true

# 2. Unpack the unmanaged zip into source control
pac solution unpack --zipfile out/ContosoCore.zip --folder src/ContosoCore --packagetype Both

# 3. Generate the deployment settings template once, then keep one copy per stage
pac solution create-settings --solution-zip out/ContosoCore_managed.zip --settings-file config/test/deploymentSettings.json

# 4. Import into the target as an upgrade, with settings, asynchronously
pac solution import --path out/ContosoCore_managed.zip --settings-file config/test/deploymentSettings.json \
  --stage-and-upgrade --async --activate-plugins
```

Without `--stage-and-upgrade`, `pac solution import` performs an **Update**: components you removed
in dev stay in the target. `--import-as-holding` is the two-step "Stage for upgrade" (then
`pac solution upgrade --solution-name ContosoCore`). Confirm flags with `pac solution import --help`
for your pac version.

## deploymentSettings.json shape

```json
{
  "EnvironmentVariables": [
    { "SchemaName": "contoso_ApiBaseUrl", "Value": "https://api.test.example.com" }
  ],
  "ConnectionReferences": [
    {
      "LogicalName": "contoso_sharedcommondataservice_ref",
      "ConnectionId": "<connection id in the target environment>",
      "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
    }
  ]
}
```

Values that are secrets do not belong here or in environment variables exported with the solution.
Use a secret-type environment variable backed by Azure Key Vault, or the pipeline secret store.
