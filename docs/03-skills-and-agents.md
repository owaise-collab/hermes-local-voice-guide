# 3. Skill discovery and useful child agents

## Why skills help

A skill is an instruction document loaded when needed. It can teach a workflow, command sequence, or verification procedure. It cannot add missing credentials, guarantee a model's reasoning quality, or make unavailable tools appear.

Hermes already includes many skills. This kit adds two small ones instead of loading an enormous collection into every request.

## The adapted GitHub discovery skill

The original setup installed [Vercel's find-skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) through Hermes's native installer. The repository-page URL failed in that run; the direct raw URL worked and the native scan returned `SAFE`:

```powershell
hermes skills install 'https://raw.githubusercontent.com/vercel-labs/skills/main/skills/find-skills/SKILL.md' --category autonomous-ai-agents --yes
```

That scan describes the content fetched during the reference setup, not a promise about future upstream changes.

The upstream skill uses `npx skills add -g`, which targets other agents' skill locations. We adapted its procedure to Hermes's native commands and retain the upstream attribution/license. `Configure-Hermes.ps1` installs the adapted copy included in this repository, so you do not need to first install the upstream copy. Copy only the specific bundled skill folders if installing manually; do not replace your entire skills directory.

Try:

```powershell
hermes skills search 'find-skills' --limit 3 --json
hermes skills inspect skills-sh/vercel-labs/skills/find-skills
hermes skills list
```

Or ask Hermes: **“Find a skill that helps me review Python code, inspect it, and explain whether it fits this project.”**

The skill first checks installed skills, then the hub and reputable GitHub sources, inspects dependencies and platform support, uses the native security scan, and applies a relevant skill when authorized. It does not bypass blocked scans with `--force`.

## The local-agent-team skill

The parent agent coordinates three roles; these are focused task instructions, not three separate installed LLMs:

| Role | Expected result |
| --- | --- |
| Researcher | Evidence, relevant sources, constraints, recommendation |
| Builder | A concrete change or artifact, plus checks |
| Reviewer | Independent checks, reproducible defects, unresolved limitations |

All children use the same local model endpoint. We limit concurrency to one and keep a flat delegation tree. This is appropriate for the tested single-slot server: extra agents add independent context, not extra GPU capacity.

The skill teaches the parent to define success, pass exact paths and constraints to the child, let background completion arrive, inspect the delivered result, test it, and report only what is established. A child starts without the conversation history. Shared files mean ownership must be explicit; avoid two agents editing the same file.

The config contains:

```yaml
delegation:
  backend: default
  max_iterations: 40
  max_concurrent_children: 1
  max_spawn_depth: 1
  subagent_auto_approve: false
  model: local-hermes
  base_url: http://127.0.0.1:8080/v1
  api_key: local-only
  api_mode: chat_completions
  fallback_providers: []
```

`local-only` is a placeholder for a loopback server running without API authentication, not a cloud API key. Do not reuse this unauthenticated setup for a network-exposed server.

## A realistic request

Start a fresh chat and try:

> Use local-agent-team. Inspect my project at D:/Projects/example. Ask one Builder agent to fix the failing parser case without changing unrelated files. Give it the failing input and acceptance check. When it completes, read its changes, run the relevant check, and report the result and any remaining issue.

Use a real project path and a specific goal. For a harmless setup test, use the file-writing prompt in the [validation guide](06-validation-and-rollback.md#test-a-real-child-agent).

Top-level delegation is asynchronous. Hermes may acknowledge that work is pending, then resume when the child finishes. Keep the owning interactive session open for the test; do not mistake that acknowledgment for a completed result. Prefer ordinary plain-text child summaries unless you actually need an output schema.

## Learning a reusable procedure

After a task succeeds, ask Hermes to save the tested workflow as a skill using its `skill_manage` tool. Keep the procedure specific, with verification and known pitfalls. Do not save credentials, private transcripts, or machine-specific user paths into a skill meant for sharing.

The appended [SOUL instructions](../config/soul-addition.md) make these behaviors persistent. They preserve normal approval rules, including for voice requests and child agents.

Upstream references: [skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) and [delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation).
