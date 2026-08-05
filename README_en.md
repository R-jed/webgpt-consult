<p align="center">
  <img src="./skills/webgpt-consult/assets/logo.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

`webgpt-consult` is a lightweight Codex Skill that lets Codex consult GPT-5.6 Sol Pro or High through ChatGPT Web in Chrome.

The Skill handles browser transport, model boundaries, conversation continuity, verified conversation binding, browser-resource lifecycle, and a small local safety guard. The current Codex model decides what to ask, how to phrase the prompt, and which source files or other evidence are useful for the user's request.

> **AI agents should read [README_Agent.md](README_Agent.md) first. Runtime behavior is defined by [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md).**

## Install

Requirements:

- Codex
- Codex Chrome plugin connected
- ChatGPT Web signed in through Chrome
- GPT-5.6 Sol Pro or High available in ChatGPT Web
- Python 3.10+ for the local safety guard only

Project-scoped install:

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

Add `-g` when updating a global installation.

## Use

Invoke explicitly:

```text
/webgpt-consult <your consultation request>
```

Examples:

```text
/webgpt-consult Review this architecture for obvious risks.
```

```text
/webgpt-consult Ask GPT-5.6 Sol to inspect the relevant source files and diagnose this bug.
```

```text
/webgpt-consult Continue the previous Web consultation and focus on the implementation results I just added.
```

There is no fixed consultation template. Codex may compose the prompt directly and may upload relevant source code, logs, documents, screenshots, or other files when useful.

For code work, prefer the smallest source set that is sufficient for the question. Relevant excerpts or selected files are usually better than uploading an entire repository for convenience.

## How it works

```text
user request
  → Codex prepares the consultation
  → basic local sensitive-data guard
  → Chrome
  → GPT-5.6 Sol Pro
     or High when Pro is unavailable
  → verify the current response
  → return to the Codex task
```

When the user clearly continues the same consultation, the Skill can reuse the verified Web conversation bound to the current Codex conversation. If that binding cannot be verified, it starts a fresh ChatGPT conversation.

If the active Web conversation becomes too context-heavy, Codex may use `Branch in new chat` or start fresh.

Conversation binding exists only inside the current Codex conversation. It is not written to project files, a database, or long-lived reviewer memory.

## Browser resources

The Skill may automatically close only old tabs that it explicitly created during the current Codex conversation and can still identify by an exact browser handle.

User-opened Chrome or ChatGPT tabs, ownership-unknown tabs, and tabs with active generation are left alone.

The project does not use `pkill`, `killall`, Chrome process scanning, a background cleanup daemon, or a persistent tab registry.

## Privacy and safety

A small local guard blocks high-confidence:

- API keys and common provider tokens
- passwords and authentication secrets
- cookies, session tokens, and Authorization headers
- private keys
- OTPs and recovery codes
- payment-card numbers, CVV/CVC, and payment PINs

The guard intentionally does not attempt to become a general PII or DLP platform.

Codex should still minimize disclosure before sending and remove unrelated names, email addresses, physical addresses, internal information, or other private context that the Web consultation does not need.

All outgoing UTF-8 prompt text and UTF-8 text attachments should pass the local guard before Send:

```bash
python3 <SKILL_ROOT>/scripts/safety_guard.py prompt.txt src/example.py
```

If it blocks, remove or redact the sensitive value locally and scan again. Do not bypass the guard.

## Model boundary

The Web model policy is fixed:

```text
GPT-5.6 Sol Pro
  → unavailable
GPT-5.6 Sol High
  → unavailable
stop
```

Codex's own model or reasoning-level labels are unrelated to Web model verification.

## Package layout

```text
skills/webgpt-consult/
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── assets/
│   └── logo.svg
├── references/
│   └── chrome-workflow.md
└── scripts/
    └── safety_guard.py
```

See [SKILL.md](skills/webgpt-consult/SKILL.md) for the runtime contract.

中文: [README.md](README.md)

## License

[MIT](LICENSE)
