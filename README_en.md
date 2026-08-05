<p align="center">
  <img src="./skills/webgpt-consult/assets/mobius-white.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#use">Use</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#privacy-and-safety">Privacy &amp; Safety</a> ·
  <a href="README.md">中文</a>
</p>

`webgpt-consult` lets Codex send a problem, the relevant source, and selected files to GPT-5.6 Sol in ChatGPT Web through Chrome, then bring the answer back into the current task.

You only need to say what you want reviewed. Simple questions stay simple. Larger tasks use the standard `CONTEXT_PACKET_V1` to carry the background, evidence, prior attempts, risks, and exact question. Follow-up consultations reuse the same verified Web conversation and model whenever possible, so Codex does not keep rebuilding the same context or reopening the model picker.

> **AI agents should read [README_Agent.md](README_Agent.md) first. Runtime behavior is defined by [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md).**

## Install

You need Codex, the Codex Chrome plugin connected, and a signed-in ChatGPT Web account where GPT-5.6 Sol Pro or High is available.

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

Codex decides what context is actually useful. For code work it can upload selected files or send only the important excerpts. If an attachment was not successfully uploaded, the Skill does not treat it as evidence that ChatGPT Web has seen.

## How it works

The first time a new ChatGPT Web conversation is used, the Skill verifies GPT-5.6 Sol Pro, with High as the fallback. Follow-up requests in that same verified conversation reuse the confirmed model. The picker is checked again only for a new conversation, a branch, a conversation-identity change, or clear evidence that the Web model state has changed.

Substantial consultations use the standard `CONTEXT_PACKET_V1`. Later turns in the same conversation send only the new evidence, current state, and next question instead of repeating the full packet.

```text
Your request
  ↓
Codex selects the relevant context and files
  ↓
Local safety check
  ↓
Reuse the verified conversation, or open a new ChatGPT Web conversation
  ↓
GPT-5.6 Sol Pro / High
  ↓
Send once and wait for the complete reply
  ↓
Verify the result and return it to the current task
```

For example, suppose you are debugging a login issue:

```text
/webgpt-consult I have been chasing this login issue for a while. Ask GPT-5.6 Sol to help find the root cause.
```

Codex might select `auth.py`, `session.py`, and the actual error as evidence. The first consultation can carry the full context. If you then say, “I implemented the suggestion, but this test still fails,” the next Web turn only needs the new code, the test result, and the new question.

If Chrome disconnects or the Send outcome becomes uncertain, the Skill first tries to recover the original conversation so the same request is not submitted twice.

## Privacy and safety

Before text is sent to the Web, the Skill locally blocks common API keys, passwords, access tokens, cookies or session data, private keys, one-time codes, and payment-card details. Names, email addresses, physical addresses, and other private details that do not matter to the question should also be left out.

This is a basic safety layer. Codex still chooses the smallest useful evidence set for the task.

## Model

For a new Web conversation:

```text
GPT-5.6 Sol Pro
  ↓ unavailable
GPT-5.6 Sol High
  ↓ unavailable
stop
```

A verified multi-turn Web conversation reuses its confirmed model. The model or reasoning level currently selected in Codex does not affect Web model selection.

## Package layout

```text
skills/webgpt-consult/
├── SKILL.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
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

This project is released under the [MIT License](LICENSE). The `CONTEXT_PACKET_V1` structure and parts of the Chrome consultation workflow are adapted from `gpt56-sol-pro-consult` in `zjp1997720/zhijian-skills`; see [THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
