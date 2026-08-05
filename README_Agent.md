# webgpt-consult: AI Agent bootstrap

This file is for AI agents that discover or support the project. Human users should read [README.md](README.md) or [README_en.md](README_en.md).

`webgpt-consult` is a lightweight Codex Skill for consulting ChatGPT Web through Chrome with GPT-5.6 Sol Pro or High.

The Skill is intentionally thin. It handles browser transport, verified Web conversation continuity, browser-resource ownership, model boundaries, request/result association, and a small local secret/payment safety guard. Prompt design and evidence selection belong to the current Codex model and the user's request.

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

`SKILL.md` is authoritative.

## Runtime boundary

The Skill does not impose a fixed review methodology or context packet.

Codex decides from the current user request:

- what to ask ChatGPT Web;
- how to phrase the prompt;
- whether files or source excerpts are useful;
- which evidence is necessary;
- how to use the returned answer.

For code tasks, Codex may upload selected source files directly. Prefer the smallest source set sufficient for the question.

The Web model policy is:

```text
GPT-5.6 Sol Pro
  → otherwise GPT-5.6 Sol High
  → otherwise stop
```

Codex model/reasoning labels are not Web model evidence.

## Continuity and browser resources

A verified Web conversation may be reused only while the current Codex conversation retains an unambiguous temporary binding. Lost or unverifiable binding means start fresh.

`Branch in new chat` may be used when the same consultation should continue but the current Web thread is too context-heavy.

Bindings are never persisted as reviewer/project memory.

Only browser tabs/pages explicitly created by this Skill in the current Codex conversation may be automatically closed, and only while their exact handles remain known. User-opened or ownership-unknown tabs are left alone.

Never use process-wide Chrome cleanup, process scanning, a background daemon, or a persistent tab registry.

## Safety

Never transmit known secrets, authentication material, or payment credentials. The installed package includes:

```text
<SKILL_ROOT>/scripts/safety_guard.py
```

Use it on UTF-8 text that may contain sensitive values. If it blocks, redact/remove the value locally and scan again. Do not bypass the guard.

The guard is intentionally narrow. Do not expand project behavior into a general DLP/PII system. Codex should minimize unrelated private information contextually before transmission.

## Do not invent behavior

Do not claim that the Skill:

- stores durable reviewer memory;
- maintains a project consultation database;
- has a fixed architecture-review or adversarial-review prompt;
- requires a fixed packet format;
- automatically packages an entire repository;
- owns or closes user browser tabs;
- supports Web models other than GPT-5.6 Sol Pro/High.

Repository discovery files are documentation. Runtime source of truth is `skills/webgpt-consult/SKILL.md` plus its Chrome workflow reference.
