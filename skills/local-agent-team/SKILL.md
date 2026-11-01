---
name: local-agent-team
description: Plan, delegate, test, and deliver verified local work
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [agents, delegation, planning, verification]
---

# Local Agent Team

## When to Use

Use for multi-step projects, debugging, research with deliverables, or a user
request to use specialist agents. Handle simple commands directly.

## Quick Reference

All agents use the local llama.cpp endpoint and `local-hermes`. The server has
one 64K slot, so run one child at a time. The parent coordinates these roles:

| Role | Deliverable |
| --- | --- |
| Researcher | Evidence, sources, constraints, and a recommendation |
| Builder | A concrete artifact or change, plus validation results |
| Reviewer | Independent checks, reproducible defects, and remaining risks |

## Procedure

1. Inspect relevant files and tools. Define what success means and make a short
   plan. Read applicable project instructions before editing.
2. Use `skills_list` and `skill_view` for existing expertise. Use `find-skills`
   if a needed capability is missing.
3. Delegate a substantial focused task with `delegate_task(goal=..., context=...)`.
   Put the role, exact workspace paths, inputs, constraints, allowed edits,
   expected artifact, and acceptance checks in the context. Children do not
   know the conversation. Never ask two agents to edit the same files.
   Prefer a short plain-text result; add an output_schema only when the task
   actually needs machine-readable JSON.
4. A top-level delegation returns a background handle. Finish independent work
   and let the completion arrive. Do not poll files or invent the result. If no
   independent work remains, tell the user what is pending and end the turn so
   Hermes can deliver the child completion. Continue from that completion.
5. Inspect the delivered artifact and evidence. For consequential work, dispatch
   a separate Reviewer task after the Builder finishes. Fix concrete defects.
6. Run appropriate checks on the final result. Report what was completed,
   where to find it, what was actually tested, and any unverified part.
7. When a workflow proves reusable, save its tested procedure with `skill_manage`.

## Pitfalls

Skills add procedures, not guaranteed intelligence. A 4B model can make mistakes;
tools and independent verification provide the evidence. Child agents inherit
the parent's enabled tools, share files, and cannot request user clarification.
Do not widen permissions, auto-approve commands, or route to a cloud model to
make a child succeed. An interrupted or failed child is not completed work.

## Verification

Confirm the child actually ran, examine its result, and perform at least one
check that exercises the requested behavior rather than repeating its claim.
