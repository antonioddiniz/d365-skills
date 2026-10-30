# D365 Skills

**The senior Dynamics 365 reviewer your coding agent doesn't have.**

Seven [Agent Skills](https://agentskills.io) for Claude Code, GitHub Copilot, Cursor and any agent
that reads `SKILL.md`. They load on their own when your agent touches Dataverse, Dynamics 365 or
Power Automate, and they encode the rules that only show up in production: the plug-in that loops,
the sync that stops at 5,000 rows, the deploy that never deletes anything, the opportunity "won"
by patching `statecode`.

Every rule cites Microsoft Learn. No customer data, no magic, MIT license.

## Why this exists

Ask any agent to "mark the opportunity as won" and it will write `PATCH opportunities(id)
{ "statecode": 1 }`. It looks right. It skips the close activity, the actual revenue and the
forecast. The correct call is `WinOpportunity`. Agents make this class of mistake all over the
platform because the docs are huge and the traps are scattered.

Microsoft now ships official skills that **operate** Dataverse: connect, query and load data with
the Python SDK and CLIs, export and import solutions, assign roles, build flows and apps. That is
great, and you should install them. This pack covers the other half: **writing and reviewing the
code and designs** those tools don't judge. Server-side C#, Web API code in any language, platform
limits, security design, release strategy, flow reliability and the Sales/Service data model.

| You need to | Use |
|---|---|
| Connect, query, bulk-load with Python, run PAC CLI for you | [microsoft/Dataverse-skills](https://github.com/microsoft/Dataverse-skills) |
| Build Power Pages, code apps, canvas apps, mobile apps, PCF | [microsoft/power-platform-skills](https://github.com/microsoft/power-platform-skills) |
| Write or review plug-ins, Web API code, loaders, roles, releases, flows, CRM lifecycle logic | **this repo** |

They work together. Install both.

## The skills

| Skill | Loads when you... | Stops this from happening |
|---|---|---|
| [`d365-plugins`](skills/d365-plugins/SKILL.md) | write or review a C# plug-in, Custom API or step registration | Update loops, `Retrieve` with all columns in a sync step, cancels inside the transaction, 2-minute timeouts |
| [`d365-webapi`](skills/d365-webapi/SKILL.md) | call `/api/data/v9.x` from TS, C#, PowerShell or Python | Silent 5,000-row cutoffs, guessed lookup names, upserts that should have been updates |
| [`d365-limits-performance`](skills/d365-limits-performance/SKILL.md) | build a migration, sync or heavy query | 429 storms, 1,000-item batches, leading-wildcard queries that get throttled |
| [`d365-security-model`](skills/d365-security-model/SKILL.md) | design roles, BUs, teams, column security | Admin-cloned roles, missing Append/Append To, sharing as a design, integrations running as admin |
| [`d365-solution-alm`](skills/d365-solution-alm/SKILL.md) | move solutions between environments or build a pipeline | Unmanaged layers in prod, `pac import` without `--stage-and-upgrade`, hard-coded URLs |
| [`d365-flow-reliability`](skills/d365-flow-reliability/SKILL.md) | build or review a Dataverse-triggered flow | Flows firing on every save, silent green failures, duplicates on retry |
| [`d365-crm-data-model`](skills/d365-crm-data-model/SKILL.md) | qualify leads, close deals or cases, log activities | `statecode` patches instead of `WinOpportunity`/`CloseIncident`, activities without parties |

Each skill is a short `SKILL.md` with rules and the reason behind each one, a review checklist,
an output format, copy-ready examples in `references/`, and its Microsoft Learn sources.

## Install

Clone once:

```bash
git clone https://github.com/antonioddiniz/d365-skills.git
```

**Claude Code** (all projects):

```bash
mkdir -p ~/.claude/skills && cp -R d365-skills/skills/* ~/.claude/skills/
```

For one project only, copy into `<project>/.claude/skills/` instead.

**GitHub Copilot** (VS Code agent mode, Copilot CLI, cloud agent):

```bash
mkdir -p .github/skills && cp -R d365-skills/skills/* .github/skills/
```

Personal install for every repo: `~/.copilot/skills/`.

**Cursor:**

```bash
mkdir -p .cursor/skills && cp -R d365-skills/skills/* .cursor/skills/
```

Cursor also reads `.claude/skills/` and `.agents/skills/`, so one copy can serve several agents.

**Anything else** that supports Agent Skills: copy the folders into the agent's skills directory.
No build step, no dependencies.

## Does it trigger on the right prompt?

[`tests/trigger-cases.md`](tests/trigger-cases.md) lists 19 prompts: 14 that must load a specific
skill and 5 near-misses that must load none of them (admin clicks, canvas apps, PCF, plain SQL,
product questions).

**Last run (2026-10-30):** a model that saw only the seven skill descriptions routed all
**19 of 19** prompts correctly, 18 with high confidence. The one medium call was "log a phone call
against the case via the Web API", which sits between `d365-crm-data-model` (correct) and
`d365-webapi`. Overlaps it flagged, to watch as skills grow: Web API vs data model on activities,
limits vs flows on throttling, ALM vs flows on connection references.

Check structure, sources and secrets before every commit:

```bash
python3 scripts/validate.py
```

It fails on a name that does not match its folder, a description over 1,024 characters, fewer than
three Microsoft Learn sources, a missing reference file, or anything that looks like a secret or a
real tenant URL.

## Principles

- **Reasons, not commands.** Each rule says why it matters, so the agent can handle cases the rule
  did not foresee.
- **Sources or it didn't happen.** Every skill ends with the Microsoft Learn pages behind it.
  Limits and defaults change: the skills tell the agent to treat numbers as defaults, not constants.
- **Placeholders only.** `contoso_`, `yourorg`, zero GUIDs. Nothing from a real tenant.
- **Small and composable.** One concern per skill, under 120 lines, details in `references/`.

## Contributing

Found a production trap that is not here? See [CONTRIBUTING.md](CONTRIBUTING.md). A rule gets in
when it prevents a real incident and a Microsoft Learn page backs it.

## License and trademarks

MIT. See [LICENSE](LICENSE).

Not affiliated with or endorsed by Microsoft. Dynamics 365, Dataverse, Power Platform and Power
Automate are trademarks of the Microsoft group of companies.
