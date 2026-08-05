<p align="center">
  <img src="./skills/webgpt-consult/assets/mobius-white.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#use">Use</a> ·
  <a href="#example">Example</a> ·
  <a href="#privacy-and-safety">Privacy &amp; Safety</a> ·
  <a href="README.md">中文</a>
</p>

`webgpt-consult` lets Codex use GPT-5.6 Sol Pro or High through ChatGPT Web in Chrome.

Tell Codex what you want help with. Codex works out what context matters, attaches relevant source files, logs, or documents when useful, and brings the Web answer back into the current task. The Skill keeps that connection reliable, including conversation continuity, Web model checks, and a basic local safety check before anything is sent.

> **AI agents should read [README_Agent.md](README_Agent.md) first. Runtime behavior is defined by [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md).**

## Install

You need Codex, the Codex Chrome plugin connected, ChatGPT Web signed in, and a Pro or Plus account with GPT-5.6 Sol Pro or High available on the Web side.

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

Add `-g` when updating a global install.

## Use

```text
/webgpt-consult <your consultation request>
```

For example:

```text
/webgpt-consult Ask GPT-5.6 Sol to investigate this login bug and inspect the relevant source and logs if needed.
```

Simple questions can be sent directly. For architecture work, code review, difficult debugging, or anything with substantial context, Codex uses the built-in standard `CONTEXT_PACKET_V1` to organize the task, background, user intent, local judgment, evidence, prior attempts, options, risks, and the exact ask before sending it to the Web model.

## Example

Suppose you have been stuck on a login bug:

```text
/webgpt-consult I have been chasing this login issue for a while. Ask GPT-5.6 Sol to help find the root cause.
```

Codex first looks at the current project and picks the material that matters, such as `auth.py`, `session.py`, and the error log. If the problem needs more structure, it uses the standard context packet. It checks outgoing text locally for obvious secrets, then opens ChatGPT Web through Chrome and uses GPT-5.6 Sol Pro when available, with High as the fallback.

After GPT-5.6 Sol reviews the material, Codex verifies that the reply belongs to this consultation and brings the answer back into the task. If you keep discussing the same issue, the Skill reuses the verified Web conversation and its already-confirmed model instead of reopening the model picker on every turn. It checks the picker again only for a new conversation, a branch, a conversation-identity change, or clear evidence that the Web model state changed.

## Privacy and safety

Before text is sent to the Web, the Skill locally blocks common API keys, passwords, access tokens, cookies or session data, private keys, one-time codes, and payment-card details. If something sensitive is found, sending stops until that value is removed or redacted.

Names, email addresses, physical addresses, and other private details that are unrelated to the question should also be left out. The safety check stays deliberately small and practical.

## Model

For a new Web conversation:

```text
GPT-5.6 Sol Pro
  ↓ unavailable
GPT-5.6 Sol High
  ↓ unavailable
stop
```

A verified multi-turn Web conversation reuses its confirmed model without repeatedly opening the picker. The model or reasoning level currently selected in Codex does not affect Web model selection.

## Package layout

```text
skills/webgpt-consult/
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── assets/
│   └── mobius-white.svg
├── references/
│   ├── chrome-workflow.md
│   └── context-packet-template.md
└── scripts/
    └── safety_guard.py
```

See [SKILL.md](skills/webgpt-consult/SKILL.md) for the detailed runtime rules.

## License

[MIT](LICENSE)
