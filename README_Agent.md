# WebGPT Consult: AI Agent Bootstrap

This file is a discovery guide. Reading it does not authorize a consultation by itself.

## Purpose

WebGPT Consult is a Codex Skill for obtaining a verified GPT-5.6 Sol Pro/High second opinion while keeping local Codex responsible for evidence, judgment, adoption, and final delivery.

Use it only when the user explicitly invokes the Skill or clearly requests this consultation workflow.

## Authoritative files

When invoked, read:

1. `SKILL.md` for the execution contract.
2. `references/context-packet-template.md` for packet structure.
3. `references/chrome-workflow.md` for browser I/O.

Do not invent additional routing or continuity rules from this README.

## Runtime invariants

- Python >= 3.10.
- Codex Chrome plugin is the only browser transport.
- Model routing is verified Pro -> verified High -> fail closed.
- `scripts/model_router.py` defines deterministic model policy.
- `scripts/submission_preflight.py` must pass before Send.
- Exact sentinel + task-ID verification is required after extraction.
- Durable consultation state is local and optional for correctness.
- Local state lives under `~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json`.
- State files must never be uploaded to ChatGPT.

## Review intent

Use a fresh Web conversation for independent, milestone, adversarial, or materially different reviews.

Reuse a stored conversation only for a clear follow-up to one consultation. If the match is ambiguous, start fresh.

For independent reviews, form the local judgment first but normally keep it private from Sol. Include it only when Sol is specifically being asked to attack, compare, or revise that proposal.

## Continuity

Use `scripts/consult_state.py` to list or load locally adopted consultation state.

A Web ChatGPT conversation is disposable. If it is unavailable, context-limited, or unreliable, open a fresh conversation and restore the consultation from the durable local snapshot plus the current delta and current evidence.

Do not depend on Branch in new chat, message lineage, rollover counters, or continuity capsules.

Continuity failure is fail-soft. Safety, model identity, evidence truthfulness, and result binding remain fail-closed.

## State ownership

Update durable state only after local Codex has compared Sol's answer with project evidence and decided what to adopt, reject, or modify.

The saved snapshot should represent current locally adopted truth, not raw Sol output or a transcript.

## Safety

Do not send executable credentials, session material, browser profiles, local consultation-state files, or unrelated private context. Do not claim an artifact was reviewed unless its actual contents were transmitted.

Non-text attachments require local review before the explicit binary confirmation flag is used. A detected credential cannot be overridden.

## Missing capability

If `SKILL.md`, required scripts, or the Codex Chrome plugin are unavailable, stop and report the missing requirement. Do not pretend the external consultation completed.
