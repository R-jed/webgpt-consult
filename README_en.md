<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#how-to-use-it">How to use it</a> ·
  <a href="#what-it-does">What it does</a> ·
  <a href="#files-and-safety">Files and safety</a> ·
  <a href="README.md">中文</a>
</p>

`webgpt-consult` has one job: let Codex open ChatGPT Web, send GPT-5.6 Sol the problem you are working on together with the material that actually matters, then bring the answer back into the current task.

It is useful when you are stuck on a bug, want another model to challenge an architecture or product decision, want a second review before shipping, or want to keep discussing the same problem over several rounds without rebuilding the whole context every time.

Small questions stay small. For difficult work, the Skill can organize the problem, evidence, previous attempts, current judgment, and risks before sending them. Follow-up turns try to stay in the same verified ChatGPT Web conversation, so the background and model choice do not have to be rebuilt for every message.

> **AI agents should read [README_Agent.md](README_Agent.md) first. The actual runtime rules are in [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md).**

## Install

You need:

- Codex
- Chrome that Codex can control
- a signed-in ChatGPT Web account
- access to GPT-5.6 Sol Pro or High

Install for the current project:

```bash
npx skills add R-jed/webgpt-consult
```

Install globally for Codex:

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

Update:

```bash
npx skills update webgpt-consult
```

Add `-g` when updating a global installation.

## How to use it

Call the Skill directly:

```text
/webgpt-consult <what you want ChatGPT Web to review>
```

For example:

```text
/webgpt-consult I have been chasing this login bug for a while. Ask GPT-5.6 Sol to find the root cause and inspect the relevant source and logs if needed.
```

You do not need to manage the browser steps yourself. Codex decides what evidence is useful, sends the consultation through Chrome, and brings the Web answer back.

## What it does

A normal consultation looks roughly like this:

```text
Your question
  ↓
Codex understands the task and selects the useful evidence
  ↓
Sensitive text is checked locally
  ↓
Reuse the existing ChatGPT Web conversation, or open a fresh one
  ↓
A fresh conversation uses GPT-5.6 Sol Pro when available, otherwise High
  ↓
Upload the real files that matter and verify the message
  ↓
Send once and wait for the complete answer
  ↓
Codex checks the Web advice against local source, logs, and facts
  ↓
Useful conclusions return to the current task
```

If you keep working on the same problem, the Skill tries to keep the same verified Web conversation and model. One round can review the architecture, the next can review your implementation, and another can inspect a new failing test without resending the entire history.

If Chrome disconnects, the Skill first tries to recover the original conversation. If the disconnect happens around the Send click, it does not blindly send the same consultation again.

Larger tasks can use `CONTEXT_PACKET_V1`. Think of it as a tidy handoff that separates the problem, background, evidence, previous attempts, current view, and risks. Small questions do not have to use it.

## Files and safety

ChatGPT Web cannot read a local path on your computer. Mentioning `/Users/me/project/auth.py` does not mean the file was delivered. Source, logs, or documents only count as evidence after the real content is uploaded, pasted, or placed in an attachment.

When only a few files matter, the Skill prefers the original files. When many text files are needed, it can build one Markdown bundle with filenames, sizes, and content-integrity information. Oversized evidence is not silently cut by default. If a complete bundle cannot be produced, the helper stops unless partial bundling was explicitly allowed.

The bundle accepts normal UTF-8 text and Unicode text with an explicit UTF-16 or UTF-32 BOM. If the encoding cannot be determined reliably, it stops instead of guessing and changing the content.

Before sending text to the Web, the Skill locally checks for common API keys, passwords, access tokens, cookies or session data, private keys, one-time codes, and payment-card details. Relevant project or business context can stay when it matters to the answer. Unrelated private information should be removed.

## Model and limits

For a fresh ChatGPT Web conversation:

```text
GPT-5.6 Sol Pro
  ↓ unavailable
GPT-5.6 Sol High
  ↓ unavailable
stop
```

A verified conversation keeps using its confirmed model. The Skill does not reopen the model picker for every follow-up.

The runtime uses Chrome controlled by Codex. It does not keep long-term consultation memory on disk, and it does not automatically upload an entire repository. The ChatGPT Web answer is an external opinion; Codex still checks it against the local task before using it.

## For people who want to inspect the source

The main files are:

```text
skills/webgpt-consult/
├── SKILL.md                         # overall rules
├── references/
│   ├── chrome-workflow.md           # executable Chrome workflow
│   └── context-packet-template.md   # context format for larger consultations
├── scripts/
│   ├── build_attachment_bundle.py   # multi-file text bundle helper
│   └── safety_guard.py              # local sensitive-data check
├── evals/evals.json                 # browser acceptance scenarios
└── tests/                            # automated tests
```

AI-agent setup is in [README_Agent.md](README_Agent.md). Detailed runtime behavior is in [SKILL.md](skills/webgpt-consult/SKILL.md).

## License

This project is released under the [MIT License](LICENSE). Third-party copyright and license notices are recorded in [THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
