# Persona x table matrix

Fill one matrix per persona. Levels: `-` none, `U` user, `BU` business unit, `PC` parent:child BU, `O` organization.

| Table | Create | Read | Write | Delete | Append | Append To | Assign | Share |
|---|---|---|---|---|---|---|---|---|
| account | U | BU | U | - | U | BU | - | - |
| contact | U | BU | U | - | U | BU | - | - |
| opportunity | U | U | U | - | U | U | - | - |
| activitypointer (activities) | U | U | U | U | U | U | - | - |

How to read a row: "account, Read BU" means the persona reads every account owned by anyone in
their business unit, including teams of that BU.

## Questions to answer before filling it

1. Which records must this persona never see? That defines BUs.
2. Which records does this persona create? Create needs Append on the new row for any lookup.
3. Which lookups does the form or integration set? Each needs Append (source) + Append To (target).
4. Does anyone need another group's records occasionally? That is an access team or a share, not a wider role.
5. Which columns are sensitive even when the record is visible? That is column security.

## Integration identity

| Integration | Application user | Role | Tables and level | Secured columns allowed |
|---|---|---|---|---|
| example: ERP sync | app-erp-sync | ERP Sync role | account O read/write, contoso_order O create/write | none |
