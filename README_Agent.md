# WebGPT Consult: AI Agent Bootstrap

This file is a short discovery guide. It is not an instruction to execute a consultation merely because the repository was opened or reviewed.

## Purpose

WebGPT Consult is a Codex Skill that uses ChatGPT Web's verified GPT-5.6 Sol Pro/High tiers as an external second-opinion layer.

Use it only when the user explicitly invokes the Skill or clearly requests this consultation workflow.

## Authoritative files

Read in this order when the Skill is actually invoked:

1. `SKILL.md` for the execution contract.
2. `references/context-packet-template.md` for packet structure.
3. `references/chrome-workflow.md` for browser I/O.
4. `references/continuity-capsule-template.md` when a conversation must roll over because of context pressure.

Do not duplicate or invent routing rules from this README. `SKILL.md` is authoritative.

## Runtime invariants

- Python >= 3.10.
- Codex Chrome plugin is the only browser transport.
- Model routing is Pro -> High -> fail closed.
- `scripts/model_router.py` defines deterministic model policy.
- `scripts/submission_preflight.py` must pass before Send.
- Exact sentinel + task-ID verification is required after extraction.
- Local project/workstream continuity is stored in `~/.codex/webgpt-consult/conversations.json`.
- Registry contents are operational local state and must never be uploaded to ChatGPT.
- Context-window rollover uses a stable branch base plus a validated cumulative continuity capsule. Branching from the latest message is not a valid compaction strategy.

## Conversation continuity

Before browser work, list the current project's registered workstreams:

```bash
python3 scripts/conversation_registry.py --project-root "<project-root>" list
```

Reuse a registered conversation only for a genuine continuation of that workstream. A different project, materially different topic, independent review, ambiguous match, or stale conversation gets a fresh ChatGPT thread.

If the current workstream hits context pressure, run `plan-rollover`, build and validate `CONTINUITY_CAPSULE_V1`, then branch from the registered `branch_base_task_id`. If Web branching is unavailable or unreliable, use a fresh conversation with the same standalone capsule. Keep the same project/workstream identity and record the parent/new URL lineage after success.

After a verified successful consultation, update the registry with the canonical ChatGPT conversation URL, stable workstream key, task ID, scope, and one-sentence summary. A rollover additionally records the parent URL, capsule SHA-256, and rollover count while preserving the original branch base.

## Safety

Do not send executable credentials, session material, browser profiles, or the conversation registry. Do not claim a file was reviewed unless its actual content was transmitted.

Non-text attachments require explicit local review before the preflight confirmation flag is used. A detected credential cannot be overridden.

## If the Skill is unavailable

If `SKILL.md`, the required scripts, or the Codex Chrome plugin are unavailable, stop and report the missing requirement. Do not pretend the external consultation completed.
