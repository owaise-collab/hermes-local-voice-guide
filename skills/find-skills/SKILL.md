---
name: find-skills
description: Find and install useful skills from GitHub and Hermes Hub
version: 1.0.0
metadata:
  hermes:
    tags: [skills, discovery, github, learning]
---

# Find Skills for Hermes

Adapted from Vercel's GitHub find-skills skill for Hermes's native installer.
Source: https://github.com/vercel-labs/skills/tree/main/skills/find-skills
Upstream attribution and its MIT notice are in this guide's THIRD_PARTY_NOTICES.md.

## When to Use

Use when the user asks to find or add a skill, wants a new capability, or a task
needs a specialized workflow. Search for a relevant skill before inventing one.

## Quick Reference

Use `terminal` to run these native Hermes commands in PowerShell:

```powershell
hermes skills search "keyword" --limit 5 --json
hermes skills inspect SOURCE/PATH
hermes skills install SOURCE/PATH --yes
hermes skills list
```

Use the exact source identifier returned by search. A GitHub SKILL.md can also
be installed using its raw HTTPS URL, as this skill itself was installed.
Use `skills_list` and `skill_view` to read installed skills. Do not use the
upstream `npx skills add -g` command: it installs into other agents' locations.

## Procedure

1. Identify the desired task and search installed skills with `skills_list`.
2. Search the Hermes Hub with focused keywords. Try a synonym if needed.
   Check reputable sources such as Vercel, Anthropic, Microsoft, and the
   official Hermes catalog. GitHub repository stars are context, not proof.
3. Inspect a candidate's SKILL.md, referenced scripts, required tools, and OS
   requirements. Prefer Windows-compatible instructions. Do not execute setup
   scripts merely because search returned them.
4. If adding a relevant skill is authorized by the user's request, install it
   with `hermes skills install ... --yes`, retaining Hermes's security scan.
   Do not bypass a blocked scan with --force. Report any actual blocker.
5. Read the installed skill with `skill_view` and use it to complete the user's
   task. Installing instructions alone does not finish a task.
6. If no suitable skill exists, solve the task using available tools. Save a
   concise tested reusable procedure with `skill_manage` when useful.

## Pitfalls

Never invent a repository path, install count, dependency, or successful test.
Inspect before running code. A skill cannot add credentials or missing model
abilities. New skill descriptions may need a fresh chat or /reload-skills.

## Verification

Confirm the installer succeeded, `hermes skills list` includes the skill,
`skill_view` loads it, and a relevant task actually works.
