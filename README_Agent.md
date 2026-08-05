# webgpt-consult: AI Agent bootstrap

This file is for AI agents that discover or support the project. Human users should read [README.md](README.md) or [README_en.md](README_en.md).

`webgpt-consult` is a lightweight Codex Skill for consulting ChatGPT Web through Chrome with GPT-5.6 Sol Pro or High.

The Skill handles browser transport, verified Web conversation continuity, browser-resource ownership, efficient Web-model reuse, request/result association, structured context handoff, and a small local secret/payment safety guard. Prompt design and evidence selection still belong to the current Codex model and the user's request.

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

Add `-g` for a global installation.

Do not invent another installer, package format, setup script, or symlink workflow.

## Invoke

User-facing entry point:

```text
/webgpt-consult <consultation request>
```

Implicit invocation is disabled.

When actually executing the Skill, resolve the installed Skill root and read:

```text
<SKILL_ROOT>/SKILL.md
<SKILL_ROOT>/references/chrome-workflow.md
```

For substantial/context-heavy consultations, also read:

```text
<SKILL_ROOT>/references/context-packet-template.md
```

`SKILL.md` is authoritative.

## Runtime boundary

The Skill does not impose one workflow on every request. It does provide the standard `CONTEXT_PACKET_V1` format for substantial consultations.

Codex decides from the current user request:

- what to ask ChatGPT Web;
- whether a simple prompt or full context packet is appropriate;
- how to phrase the prompt;
- whether files or source excerpts are useful;
- which evidence is necessary;
- how to use the returned answer.

For code tasks, Codex may upload selected source files directly. Prefer the smallest source set sufficient for the question.

For second and later turns in the same verified Web conversation, prefer a small delta prompt. Do not resend a full context packet unless older context is stale, ambiguous, or missing.

The Web model policy for a new conversation is:

```text
GPT-5.6 Sol Pro
  → otherwise GPT-5.6 Sol High
  → otherwise stop
```

A verified multi-turn conversation caches its confirmed Web model tier. Do not reopen the model picker on every follow-up. Re-verify only after a new/branched conversation, a conversation-identity change, a missing/invalid cache, clear UI evidence of a model change, a model error, or an explicit request to re-check the tier.

A browser runtime reset does not by itself invalidate the cached tier if the same Web conversation can be recovered and verified.

Codex model/reasoning labels are not Web model evidence.

## Continuity and browser resources

A verified Web conversation may be reused only while the current Codex conversation retains an unambiguous temporary binding. Lost or unverifiable binding means start fresh unless a `SENT`/`UNKNOWN` request is still unresolved and must first be recovered.

`Branch in new chat` may be used when the same consultation should continue but the current Web thread is too context-heavy. A branch is a new conversation and must establish its own Web-model verification.

Bindings and model caches are never persisted as reviewer/project memory.

Only browser tabs/pages explicitly created by this Skill in the current Codex conversation may be automatically closed, and only while their exact handles remain known. User-opened or ownership-unknown tabs are left alone.

Never use process-wide Chrome cleanup, process scanning, a background daemon, or a persistent tab registry.

## Safety

Never transmit known secrets, authentication material, or payment credentials. The installed package includes:

```text
<SKILL_ROOT>/scripts/safety_guard.py
```

Run it on the exact outgoing prompt text and every UTF-8 text attachment before Send. If it blocks, redact/remove the value locally and scan again. Review warnings for obvious private identifiers when relevant to the task.

The guard is intentionally narrow. Codex should minimize unrelated private information contextually before transmission.

## Do not invent behavior

Do not claim that the Skill:

- stores durable reviewer memory;
- maintains a project consultation database;
- requires every request to use a full context packet;
- automatically packages an entire repository;
- re-checks the model picker on every message in a verified conversation;
- owns or closes user browser tabs;
- supports Web models other than GPT-5.6 Sol Pro/High.

Repository discovery files are documentation. Runtime source of truth is `skills/webgpt-consult/SKILL.md` plus its references.
