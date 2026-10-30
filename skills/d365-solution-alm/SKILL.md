---
name: d365-solution-alm
description: Plan and review application lifecycle management for Dynamics 365, Dataverse and Power Platform solutions - managed versus unmanaged, publishers and prefixes, solution layers and the active (unmanaged) layer, upgrade versus update versus stage-for-upgrade versus patch, removing components, segmented solutions, environment variables, connection references, the deployment settings file for automated import, pac CLI, Pipelines in Power Platform and Build Tools. Use this skill whenever the user moves customizations between dev, test and production, sets up CI/CD or a pipeline for Power Platform, asks why a change in production does not show up or cannot be removed, sees solution import errors or dependency errors, plans a release or rollback, or hard-codes URLs, IDs or connections inside flows and apps. Exporting or importing one solution by command is a mechanic; deciding how releases should work is this skill.
---

# Solution ALM for Power Platform

Production should only ever receive managed solutions built from source control. Everything else
is a story you will tell during the post-mortem.

## The rules

1. **Unmanaged lives in dev only.** Test, UAT and production get managed solutions. An unmanaged
   import into production creates an active layer that sits on top of every future release.
2. **One publisher, chosen once.** The prefix is permanent for every component created with it.
3. **Know the layer stack.** Runtime behavior comes from the top layer ("top wins"), except forms,
   model-driven apps and site maps, which merge. If a release "does not apply", look for an
   unmanaged active layer on that component and remove it.
4. **Pick the import action deliberately:**

| Action | Removes components that left the solution | Use when |
|---|---|---|
| Upgrade (default) | Yes | Normal release. Keeps target identical to source. |
| Stage for upgrade | Yes, after "Apply upgrade" | You must migrate data between old and new before deleting. |
| Update | No | Fast hotfix that removes nothing. Leaves drift behind. |
| Patch | No | Avoid. Microsoft no longer recommends patches. |

   Tool mapping: UI "Upgrade" = `pac solution import --stage-and-upgrade` = Pipelines default.
   UI "Stage for upgrade" = `--import-as-holding`. **`pac solution import` with no flag is an Update**,
   so a pipeline without `--stage-and-upgrade` silently stops deleting removed components.
   Avoid `--force-overwrite` and `--publish-changes` for managed imports: both slow the import,
   and the first hides an unmanaged-layer problem instead of fixing it.
5. **Delete through an upgrade.** Remove the component in dev, bump the version, import as Upgrade.
   Deleting a managed solution deletes its components **and their data**.
6. **Version every export:** major.minor.build.revision, always higher than the target.
7. **No environment-specific values inside components.** Use environment variables for URLs, ids
   and settings, and connection references for connections. Do not put secrets in environment
   variable values that get exported to source control.
8. **Automate import with a deployment settings file** (`pac solution create-settings`) that fills
   connection references and environment variables per stage. Connections must exist in the target
   and be owned by, or shared with, the connection reference owner.
9. **Segment solutions** by deployment cadence or team, and add only the table assets you changed
   (not "add all assets"). Smaller solutions mean smaller blast radius.
10. **Block unmanaged customizations** in test and production environments so nobody can create an
    active layer by hand.
11. **Custom APIs and anything other solutions depend on:** set Is Customizable = false in managed.
12. **Release is a pipeline,** not a person: export (unmanaged for source, managed for deploy),
    unpack to source control, build, import with settings, run smoke tests, enable flows.

## Release review checklist

- [ ] Target receives managed only? No unmanaged layer on components in this release?
- [ ] Version higher than target? Import action chosen and justified?
- [ ] Components removed in this release will actually be deleted (Upgrade)? Data impact checked?
- [ ] No hard-coded URLs, GUIDs or connections in flows, plug-ins or apps?
- [ ] Deployment settings file present for each target stage? Connections exist and are shared?
- [ ] Plug-in steps and flows enabled after import? Owner of flows is a service account?
- [ ] Rollback plan stated (previous managed version available, data migration reversible)?
- [ ] Smoke test list for the target runs after import?

## Output

Return the release plan: solutions and versions, import action per solution, settings file per
stage, post-import steps, rollback. For a problem: the layer or dependency causing it and the fix.

## References in this skill

- `references/pipeline-commands.md` - pac CLI commands and a deployment settings example.

## Sources (Microsoft Learn)

- Solution concepts: https://learn.microsoft.com/power-platform/alm/solution-concepts-alm
- Solution layers: https://learn.microsoft.com/power-platform/alm/solution-layers-alm
- Upgrade or update a solution: https://learn.microsoft.com/power-apps/maker/data-platform/update-solutions
- Segmented solutions: https://learn.microsoft.com/power-platform/alm/segmented-solutions-alm
- Connection references and environment variables in automated deployments: https://learn.microsoft.com/power-platform/alm/conn-ref-env-variables-build-tools
- Build Tools tasks: https://learn.microsoft.com/power-platform/alm/devops-build-tool-tasks
- Pipelines in Power Platform: https://learn.microsoft.com/power-platform/alm/pipelines
- Managed properties: https://learn.microsoft.com/power-platform/alm/managed-properties-alm
- Import performance recommendations (option mapping across tools): https://learn.microsoft.com/power-platform/alm/performance-recommendations
- pac solution reference: https://learn.microsoft.com/power-platform/developer/cli/reference/solution
- Block unmanaged customizations: https://learn.microsoft.com/power-platform/alm/block-unmanaged-customizations
