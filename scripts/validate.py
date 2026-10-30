#!/usr/bin/env python3
"""Validate every skill in ./skills. Standard library only. Exit code 0 = pass, 1 = fail.

Checks:
  1. Frontmatter has `name` equal to the folder name (lowercase, hyphens, <= 64 chars).
  2. `description` exists, 1-1024 characters (Agent Skills limit).
  3. A "## Sources" section with at least 3 learn.microsoft.com links.
  4. Every `references/<file>` mentioned in SKILL.md exists.
  5. No secrets or real tenant URLs in any file (client secrets, bearer tokens, *.dynamics.com orgs).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SECRET_PATTERNS = [
    (re.compile(r"(?i)client[_-]?secret\s*[:=]\s*['\"]?[A-Za-z0-9~._-]{12,}"), "client secret"),
    (re.compile(r"Bearer\s+eyJ[A-Za-z0-9._-]{20,}"), "bearer token"),
    (re.compile(r"https://(?!yourorg\b)[a-z0-9-]+\.crm\d*\.dynamics\.com", re.I), "real org URL"),
    (re.compile(r"(?i)AccountKey=[A-Za-z0-9+/=]{20,}"), "storage key"),
]


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def check_skill(folder):
    errors = []
    skill_md = folder / "SKILL.md"
    if not skill_md.exists():
        return [f"{folder.name}: missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        return [f"{folder.name}: missing YAML frontmatter"]
    name = fm.get("name", "")
    if name != folder.name or not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{folder.name}: name '{name}' must equal folder, lowercase-hyphen, <= 64 chars")
    desc = fm.get("description", "")
    if not 1 <= len(desc) <= 1024:
        errors.append(f"{folder.name}: description length {len(desc)} outside 1-1024")
    sources = text.split("## Sources", 1)
    if len(sources) < 2:
        errors.append(f"{folder.name}: no '## Sources' section")
    elif len(re.findall(r"https://learn\.microsoft\.com/\S+", sources[1])) < 3:
        errors.append(f"{folder.name}: fewer than 3 Microsoft Learn sources")
    for ref in set(re.findall(r"references/[A-Za-z0-9._-]+\.md", text)):
        if not (folder / ref).exists():
            errors.append(f"{folder.name}: mentions {ref} but file is missing")
    return errors


def check_secrets():
    errors = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in {".md", ".py", ".json", ".txt", ".yml", ".yaml"}:
            continue
        if path.name == "validate.py":
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(content):
                errors.append(f"{path.relative_to(ROOT)}: looks like a {label}")
    return errors


def main():
    folders = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    errors = [e for f in folders for e in check_skill(f)] + check_secrets()
    for e in errors:
        print(f"FAIL  {e}")
    print(f"{len(folders)} skills checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
