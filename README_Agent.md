# webgpt-consult: AI Agent bootstrap

This file is for AI agents that discover or support the project. Human users should read [README.md](README.md) or [README_en.md](README_en.md).

`webgpt-consult` is a Codex Skill for verified, multi-turn consultation with GPT-5.6 Sol Pro or High through ChatGPT Web in Chrome. It combines structured context handoff, real evidence delivery, conversation/model reuse, attachment verification, and duplicate-send recovery.

## Install

Project scope:

```bash
npx skills add R-jed/webgpt-consult
```

Global Codex install:

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

Update:

```bash
npx skills update webgpt-consult
```

Add `-g` for a global installation. Do not invent another installer, setup script, package format, or symlink workflow.

## Invoke

User-facing entry point:

```text
/webgpt-consult <consultation request>
```

Implicit invocation is disabled.

Before browser work, resolve the installed Skill root and read:

```text
<SKILL_ROOT>/SKILL.md
<SKILL_ROOT>/references/chrome-workflow.md
```

For substantial consultations, also read:

```text
<SKILL_ROOT>/references/context-packet-template.md
```

`SKILL.md` is authoritative.

## Runtime contract

Codex owns task understanding, evidence selection, local verification, and final delivery. ChatGPT Web is advisory.

Use a compact prompt for simple work. Use canonical `CONTEXT_PACKET_V1` for substantial work with a fresh `task_id` and sentinel. For second and later turns in the same verified Web conversation, use the delta form unless old context is stale, ambiguous, or contradicted.

For review, architecture, product, business, risk, or other second-opinion work, include an existing local judgment when useful and keep it separate from facts and unknowns. Omit it when the user wants an independent first view.

For genuinely difficult work, a packet around 8,000 to 15,000 characters can be appropriate when shortening it would remove causal details. Treat this as guidance, not a target.

Never claim ChatGPT Web inspected a local path. Deliver the actual file, a faithful excerpt, or a generated text bundle. Prefer the smallest evidence set that preserves the truth.

## Evidence and attachment bundle

Prefer original selected human-readable files when they can be uploaded reliably.

When many relevant UTF-8 text files are awkward to upload individually or an archive is rejected, use:

```bash
python3 "<SKILL_ROOT>/scripts/build_attachment_bundle.py" \
  /path/to/selected/source \
  -o /tmp/webgpt-consult-bundle.md
```

The helper skips common dependency/cache/build directories, uses strict UTF-8, records relative provenance labels and SHA-256 hashes, and runs the blocking safety scan on the generated bundle.

It fails closed when configured size limits would make evidence incomplete. `--allow-partial` is an explicit opt-in and marks truncated/omitted evidence. Never describe a partial bundle as complete.

Do not automatically bundle or upload an entire repository. Codex selects the evidence first.

## Conversation and model reuse

A completed consultation may retain temporary session state only in the current Codex conversation:

```text
review_tab_handle
review_tab_owned_by_skill
review_conversation_url
last_task_id
last_sentinel
verified_web_model
model_verified_conversation_url
```

For a new or branched ChatGPT Web conversation, verify GPT-5.6 Sol Pro, otherwise High, and cache the verified tier for that conversation.

Do not reopen the model picker on normal follow-ups.

If the exact bound handle remains live on the same conversation, the previous submission completed successfully, and no reset/navigation/ambiguity occurred, use the Chrome workflow's live fast path. Do not re-read the previous sentinel merely to continue the next turn.

When recovering after a lost handle, runtime reset, or explicit URL reopen, prove the recovered conversation with the exact retained URL/handle plus `last_sentinel` before continuing. A Chrome runtime reset invalidates old browser objects and pending promises but does not automatically invalidate the cached model.

Bindings and model caches are session-scoped. Do not persist reviewer memory, project summaries, browser state, or consultation history to disk.

## In-flight submission record

While a submission is unresolved, keep only this transient recovery state in the current Codex conversation:

```text
current_task_id
current_sentinel
current_context_strategy
current_attachment_names
current_dispatch_state: NOT_SENT | SENT | UNKNOWN
current_conversation_url
```

Clear it after verified completion or after a deliberate failed/incomplete outcome once no ambiguous Send remains.

This record exists so a reset can recover the correct submission without sending another copy.

## Browser reliability

Use the real file chooser. When the browser API exposes a pending chooser promise, keep chooser wait, menu interaction, chooser resolution, and file assignment in one browser-tool invocation.

After upload UI changes, reacquire the composer. Confirm every required attachment chip, insert the prompt once, reacquire again, and verify rendered composer text contains the current sentinel and distinctive request text. For a packet, also verify `CONTEXT_PACKET_V1` and `task_id`.

If an uploaded text/Markdown preview leaves the composer empty and there is exactly one associated `Show in text field`, `在文本字段中显示`, or equivalent action, use it once and verify again. Never Send an empty or unverified composer.

Dispatch states:

```text
NOT_SENT
SENT
UNKNOWN
```

`NOT_SENT` may rebuild after fresh verification. `SENT` recovers the same conversation and waits/extracts. `UNKNOWN` recovers the original handle or exact conversation URL and never sends a replacement while uncertainty remains.

While generation is active, do not resend, refresh, close the tab, or send `continue`.

After completion, verify the latest assistant turn's first non-empty line against the current sentinel before refreshing the binding.

Only close browser resources proven to have been created by this Skill in the current Codex conversation. Never use process-wide Chrome termination, process scanning, a cleanup daemon, or a persistent tab registry.

## Safety

Run:

```text
<SKILL_ROOT>/scripts/safety_guard.py
```

on the exact outgoing prompt/packet and every UTF-8 text attachment before Send.

Blocking findings include high-confidence secrets, authentication material, and payment credentials. Privacy warnings are contextual. Task-relevant user-owned business/project facts can remain when they affect the judgment; remove unrelated private information.

The bundle helper performs another blocking scan on the generated bundle.

## Web model boundary

For a new Web conversation:

```text
GPT-5.6 Sol Pro
  → otherwise GPT-5.6 Sol High
  → otherwise stop
```

Codex model names and reasoning levels are not Web model evidence. Do not map `Medium`, `Extra High`, localized reasoning labels, GPT-5.5 Pro, or `Pro Extended` into the allowed Web tiers.

## Local integration

The Web answer is not final truth. Check claims that matter against the local evidence and user constraints before delivery.

For a second-opinion review, an explicit `Adopt / Reject / Modify` integration is useful when it clarifies what changed after consultation. Do not force that wrapper onto ordinary debugging or follow-up work when the user asked for another form of output.

## Validation assets

The installed package contains lightweight deterministic tests and manual eval scenarios:

```text
<SKILL_ROOT>/tests/
<SKILL_ROOT>/evals/evals.json
```

Tests cover the safety guard, bundle integrity, and runtime contract. Evals document the Chrome failure modes that must remain supported, including empty-composer recovery, ambiguous Send recovery, multi-turn model reuse, and existing-result extraction.

These assets validate protocol behavior. They do not prescribe how Codex should reason about the user's task.

## Unsupported behavior

Do not claim that the Skill:

- provides an OpenCLI fallback;
- stores durable reviewer or project memory;
- automatically packages or uploads an entire repository;
- requires the full context packet for every request;
- reopens the model picker on every follow-up;
- can recover a previous conversation by guessing from sidebar titles, recent-chat order, timestamps, or semantic similarity;
- owns or closes user-created browser tabs;
- supports Web models outside GPT-5.6 Sol Pro/High.

Repository discovery files are documentation. Runtime source of truth is `skills/webgpt-consult/SKILL.md` plus its references.

## Attribution

The `CONTEXT_PACKET_V1` structure, Chrome consultation workflow, and multi-file evidence approach were informed by `gpt56-sol-pro-consult` in `zjp1997720/zhijian-skills`. See [skills/webgpt-consult/THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
