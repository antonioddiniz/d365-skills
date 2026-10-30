# Contributing

A rule gets in when it prevents a real production problem and a Microsoft Learn page backs it.

1. One skill per folder in `skills/`, with `SKILL.md` (frontmatter `name` = folder) and optional `references/`.
2. Every rule explains **why** it matters. Agents follow reasons better than commands.
3. Every skill ends with `## Sources`, at least three Microsoft Learn links.
4. Examples use placeholders (`contoso_`, `yourorg`, zero GUIDs). No customer data, no tenant URLs, no secrets.
5. Add at least one trigger case to `tests/trigger-cases.md` for a new skill.
6. Run `python3 scripts/validate.py` before opening a pull request. It must print `0 problem(s)`.
