---
name: d365-security-model
description: Design and review the Dataverse / Dynamics 365 security model - business units, security roles and access levels (User/Basic, Business Unit/Local, Parent:Child/Deep, Organization/Global), owner teams, Microsoft Entra group teams, access teams and team templates, hierarchy security, record sharing (PrincipalObjectAccess), column-level security with field security profiles and masking, and application users for integrations. Use this skill whenever the user asks who can see or edit which records, designs roles for a new app or rollout, adds business units or teams, sees "principal user is missing privilege" errors, wants to hide a column such as a document number or salary, gives an integration or service principal access, or complains that sharing made the system slow. This is about designing the model; assigning one role to one user is an admin task.
---

# Dataverse security model

Security in Dataverse is cumulative: a user gets the broadest access of all roles, team roles and
shares that apply. So every grant is permanent until someone removes it, and nobody removes it.
Design for the least access that lets people work, and make exceptions visible.

## The building blocks, in the order to use them

1. **Business units** define the data boundary, not the org chart. Add one only when a group must
   not see another group's records. Each user and team belongs to exactly one.
2. **Security roles** grant privilege x access level per table:
   Create, Read, Write, Delete, Append, Append To, Assign, Share at
   User (Basic), Business Unit (Local), Parent:Child (Deep), Organization (Global), or None.
   Organization-owned tables only have Global or None.
3. **Owner teams / Entra group teams** own records and carry roles. Use them when a group owns work
   together. Members still need their own role to create user-owned records.
4. **Access teams** (with a team template) give per-record access to a changing group of people.
   They own nothing and have no roles. Good for "the people on this deal".
5. **Hierarchy security** (manager or position) for "managers see their reports' records".
6. **Sharing** is for exceptions only. It is slower and harder to audit than roles. Share with a
   team, not with many users one by one.
7. **Column-level security** when record access is right but one column is not. It never grants
   record access. Use profiles for groups, field sharing for one record, masking for partial reveal.
   Use it only where needed: each secured column has a cost.

## Rules that prevent the usual mess

- **Never clone System Administrator or System Customizer** to build an app role. Start from a
  minimal role and add privileges the app actually uses.
- **Append and Append To come in pairs.** To set a lookup from A to B, the user needs Append on A and
  Append To on B. Missing one is the most common "missing privilege" error.
- **Integrations run as application users** (Entra app registration) with a dedicated role scoped
  to the tables and levels they use. Never as a person, never as System Administrator by default.
- **Automatic sharing is a smell.** Plug-ins or flows that share every new record create
  PrincipalObjectAccess growth and slow queries. Prefer team ownership, BU design or access teams.
- **Roles and field security profiles travel in solutions.** Business units, teams and user
  assignments do not. Plan them per environment.
- **Test with a real non-admin user.** Admins bypass most checks, so admin testing proves nothing.

## Design review checklist

- [ ] Each BU exists because of a data boundary that someone named?
- [ ] Each role states its persona and the tables it needs, at the lowest level that works?
- [ ] No role cloned from an admin role? No user with System Administrator "for now"?
- [ ] Lookups covered by Append + Append To pairs?
- [ ] Team type matches the need (owner vs access vs Entra group)?
- [ ] Sharing used only for exceptions? No automation that shares every record?
- [ ] Sensitive columns (document ids, health, salary) secured with a profile and, if useful, masking?
- [ ] Integrations use application users with their own scoped role?
- [ ] Test plan uses non-admin accounts for each persona?

## Output

Return a persona-by-table matrix (privilege and level), the team and BU design with the reason for
each, the column security plan, and the risks found. Prefer a table to prose.

## References in this skill

- `references/role-matrix-template.md` - persona matrix template and how to read access levels.

## Sources (Microsoft Learn)

- Security concepts for developers: https://learn.microsoft.com/power-apps/developer/data-platform/security-concepts
- Security concepts in Dataverse (sharing, column security): https://learn.microsoft.com/power-platform/admin/wp-security-cds
- How access to a record is determined: https://learn.microsoft.com/power-platform/admin/how-record-access-determined
- Security roles and privileges: https://learn.microsoft.com/power-platform/admin/security-roles-privileges
- Access teams and owner teams: https://learn.microsoft.com/power-apps/developer/data-platform/use-access-teams-owner-teams-collaborate-share-information
- Column-level security with code: https://learn.microsoft.com/power-apps/developer/data-platform/column-level-security
- Column-level security example (masking): https://learn.microsoft.com/power-platform/admin/column-level-security-example
- Security strategy for customer engagement apps: https://learn.microsoft.com/dynamics365/guidance/implementation-guide/security-strategy-product-ce
