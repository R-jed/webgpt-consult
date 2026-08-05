# webgpt-consult: AI Agent bootstrap

This file is for AI agents that discover or support the project. Human users should read [README.md](README.md) or [README_en.md](README_en.md).

`webgpt-consult` is a Codex Skill for consulting ChatGPT Web through Chrome with GPT-5.6 Sol Pro or High. It keeps the Web conversation reliable across attachments, long responses, follow-ups, browser resets, and uncertain Send outcomes.

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

The Skill owns the browser consultation protocol. Codex owns task understanding, evidence selection, and the final use of the Web answer.

For a simple consultation, a compact prompt is enough. For substantial work, use the canonical `CONTEXT_PACKET_V1` format with a fresh `task_id` and sentinel. For second and later turns in the same verified Web conversation, use the compact delta form unless older context is stale or ambiguous.

Never claim that ChatGPT Web inspected a local path. Upload the actual file, paste the relevant content, or provide a faithful excerpt. Prefer the smallest evidence set that preserves the truth of the problem.

If many selected text files are genuinely needed, Codex may create a temporary Markdown bundle with ordinary local tooling. There is no bundled repository-packaging subsystem.

## Conversation and model reuse

A successful consultation may retain temporary state only inside the current Codex conversation:

```text
review_tab_handle
review_tab_owned_by_skill
review_conversation_url
last_task_id
last_sentinel
verified_web_model
model_verified_conversation_url
```

For a new or branched ChatGPT Web conversation, verify GPT-5.6 Sol Pro, otherwise High, then cache that tier for the verified conversation.

Do not reopen the model picker for every follow-up. Re-verify only when the conversation identity changes, the cache is missing or cannot be trusted, fresh UI/error evidence contradicts it, or the user explicitly asks for a tier check/change.

A Chrome runtime reset invalidates old locators and pending browser promises. It does not automatically invalidate the model cache if the same Web conversation can be recovered and verified.

Bindings and model caches are session-scoped. Do not persist reviewer memory, project summaries, browser state, or consultation history to disk.

## Browser reliability

Use the real file chooser. When the browser API uses a pending chooser promise, keep the entire chooser lifecycle inside one browser-tool invocation. After upload UI changes, reacquire the composer and verify the required attachment chips and rendered prompt text before Send.

Never Send an empty or unverified composer.

Track each submission with transient dispatch state:

```text
NOT_SENT
SENT
UNKNOWN
```

If Send definitely did not happen, the draft may be rebuilt. If Send happened, recover the same conversation and wait. If the outcome is `UNKNOWN`, recover the original conversation and never submit a replacement while the outcome remains uncertain.

While generation is active, do not resend, refresh, close the tab, or send `continue`.

After completion, verify the latest assistant turn against the current sentinel before refreshing the binding.

Only close browser resources proven to have been created by this Skill in the current Codex conversation. Never use process-wide Chrome termination, process scanning, a cleanup daemon, or a persistent tab registry.

## Safety

Before Send, run:

```text
<SKILL_ROOT>/scripts/safety_guard.py
```

on the exact outgoing prompt/packet and every UTF-8 text attachment.

Blocking findings include high-confidence secrets, authentication material, and payment credentials. The guard may also emit non-blocking warnings for obvious private identifiers. Remove or redact blocking findings locally before continuing.

The guard is a small safety layer, not a general DLP system. Codex should remove unrelated private information contextually.

## Web model boundary

For a new Web conversation:

```text
GPT-5.6 Sol Pro
  → otherwise GPT-5.6 Sol High
  → otherwise stop
```

Codex model names and reasoning levels are not Web model evidence. Do not map `Medium`, `Extra High`, localized reasoning labels, GPT-5.5 Pro, or `Pro Extended` into the allowed Web tiers.

## Unsupported behavior

Do not claim that the Skill:

- provides an OpenCLI fallback;
- stores durable reviewer or project memory;
- automatically packages an entire repository;
- requires the full context packet for every request;
- reopens the model picker on every follow-up;
- can infer a previous conversation from sidebar titles, recent-chat order, timestamps, or semantic similarity;
- owns or closes user-created browser tabs;
- supports Web models outside GPT-5.6 Sol Pro/High.

Repository discovery files are documentation. Runtime source of truth is `skills/webgpt-consult/SKILL.md` plus its references.

## Attribution

The `CONTEXT_PACKET_V1` structure and parts of the Chrome consultation workflow are adapted from `gpt56-sol-pro-consult` in `zjp1997720/zhijian-skills`. See [skills/webgpt-consult/THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
