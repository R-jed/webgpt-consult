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

`webgpt-consult` lets Codex send a problem and the evidence that actually matters to GPT-5.6 Sol in ChatGPT Web through Chrome, then bring the result back into the current task.

Simple questions stay simple. Larger architecture, code, debugging, product, and risk tasks use the standard `CONTEXT_PACKET_V1` to keep background, evidence, prior attempts, local judgment, options, and risks clear. Follow-up turns reuse the same verified Web conversation and model whenever possible, avoiding repeated context uploads, model-picker checks, and duplicate submissions.

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

Codex decides which material is actually useful. ChatGPT Web cannot read a local path by itself, so source, logs, or documents count as evidence only after their real content is uploaded, pasted, or placed in an attachment bundle.

When many text files are needed, the Skill includes a bundle helper that produces one Markdown attachment with provenance labels and SHA-256 hashes. It does not silently truncate oversized evidence by default. If the selected evidence would be incomplete, it stops unless partial bundling was explicitly allowed.

## How it works

The first time a new ChatGPT Web conversation is used, the Skill verifies GPT-5.6 Sol Pro, with High as the fallback. Normal follow-up turns in that same conversation reuse the verified model.

When the original tab and conversation identity are still intact, follow-ups use a live fast path and continue directly. After a Chrome reconnect, lost tab handle, or explicit conversation reopen, the Skill uses the previous sentinel to prove it recovered the same conversation before continuing.

Substantial work uses `CONTEXT_PACKET_V1`. For architecture, risk, product, or other second-opinion reviews, an existing local judgment is kept separate from facts so GPT-5.6 Sol can challenge a concrete position. The Web answer remains advisory. Codex still checks it against local source and facts and decides what to adopt, modify, or reject.

Later turns in the same conversation send only the new evidence, current state, and next question unless older context needs correction.

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
Check the Web advice against local evidence
  ↓
Return it to the current task
```

For example, suppose you are debugging a login issue:

```text
/webgpt-consult I have been chasing this login issue for a while. Ask GPT-5.6 Sol to help find the root cause.
```

Codex might select `auth.py`, `session.py`, and the real error output. If several source files matter, it can upload the selected originals or build one review bundle. If you then say, “I implemented the suggestion, but this test still fails,” the next Web turn only needs the changed code, the test result, and the new question.

If Chrome disconnects around the Send click, the Skill tracks the outcome as `NOT_SENT`, `SENT`, or `UNKNOWN`. An uncertain outcome is recovered from the original conversation instead of submitting the same request again.

## Privacy and safety

Before text is sent to the Web, the Skill locally blocks common API keys, passwords, access tokens, cookies or session data, private keys, one-time codes, and payment-card details.

Task-relevant project or business context can remain when it materially affects the judgment. Unrelated names, email addresses, physical addresses, and other private details should be removed. The goal is to block credentials and unnecessary private data without stripping away context the consultation actually needs.

## Model

For a new Web conversation:

```text
GPT-5.6 Sol Pro
  ↓ unavailable
GPT-5.6 Sol High
  ↓ unavailable
stop
```

A verified multi-turn Web conversation reuses its confirmed model. The picker is opened again only for a new conversation or branch, an identity change, contradictory model state, a model error, or an explicit request to re-check the tier.

The model or reasoning level currently selected in Codex does not affect Web model selection.

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
├── scripts/
│   ├── build_attachment_bundle.py
│   └── safety_guard.py
├── evals/
│   └── evals.json
└── tests/
    ├── test_attachment_bundle.py
    ├── test_safety_guard.py
    └── test_skill_contract.py
```

See [SKILL.md](skills/webgpt-consult/SKILL.md) for the detailed runtime rules.

## License

This project is released under the [MIT License](LICENSE). The `CONTEXT_PACKET_V1` structure, Chrome consultation workflow, and multi-file evidence handling were informed by `gpt56-sol-pro-consult` in `zjp1997720/zhijian-skills`; see [THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
