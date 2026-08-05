<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="webgpt-consult: a verified GPT-5.6 Sol second opinion for Codex through ChatGPT Web">
</p>

<p align="center">
  <a href="README.md">中文</a> ·
  <a href="SKILL.md">Skill contract</a> ·
  <a href="README_Agent.md">AI Agent guide</a>
</p>

`webgpt-consult` is a Codex Skill for difficult architecture, debugging, product, business, risk, and file-grounded review work. Local Codex forms its own judgment first, sends a carefully bounded evidence set through the Codex Chrome plugin to ChatGPT Web, obtains a GPT-5.6 Sol second opinion, verifies the returned result, and then decides locally what to adopt, reject, or modify.

<p align="center">
  <img src="./assets/readme/workflow.svg" width="100%" alt="webgpt-consult workflow from local judgment through evidence, preflight, Sol review, verification, and local adoption">
</p>

## Two review modes

Use `independent` for milestone reviews, deep reviews, adversarial checks, architecture resets, or materially different questions. It starts a fresh ChatGPT conversation. Codex still forms its own judgment first, but normally keeps that conclusion private from Sol to reduce anchoring.

Use `follow-up` only for a clear continuation of one consultation. Explicit continuation, or one unique anchor such as a PR, issue, branch, or named artifact, can justify reusing the stored Web conversation.

If the match is ambiguous, start fresh. Repeating some context is safer than attaching a request to the wrong consultation.

## Durable continuity

Long-lived consultation state is stored locally:

```text
~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json
```

Each snapshot contains only locally adopted reusable state such as user intent, standing constraints, accepted decisions, rejected or deferred paths, open questions, evidence references, and current project state.

A ChatGPT Web conversation is an execution container. If the stored chat is unavailable, context-limited, visibly forgetting important decisions, or otherwise unreliable, Codex opens a fresh conversation and restores the same consultation from the local snapshot plus the current delta and current evidence.

<p align="center">
  <img src="./assets/readme/continuity.svg" width="100%" alt="webgpt-consult keeps durable consultation state locally while allowing Web conversations to be replaced under context pressure">
</p>

List consultations for the current checkout with:

```bash
python3 scripts/consult_state.py --project-root . list
```

Project identity includes the canonical checkout path, so separate clones or worktrees do not silently share consultation state.

## Safety and verification

These boundaries fail closed:

- GPT-5.6 Sol model identity cannot be verified
- neither Pro nor High is usable
- executable credentials are detected in transmitted text
- required evidence was not actually transmitted
- exact sentinel and task-ID binding fails

Run preflight immediately before Send:

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-... \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --attachment ./src/example.py
```

Non-text attachments require local review before `--confirm-unscanned-binary` may be used. That confirmation never overrides a detected credential finding.

Model routing is fixed:

```text
verified GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
verified GPT-5.6 Sol High
      ↓ unavailable
fail closed
```

The external reply must begin with:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

`scripts/result_verifier.py` verifies the latest assistant turn. A sentinel merely appearing later in prose does not count.

## Quick start

Requirements: Python 3.10+, Codex, a connected Codex Chrome plugin, ChatGPT Web signed in in the selected Chrome profile, and an account that actually exposes GPT-5.6 Sol Pro or High.

If your Codex environment uses the Skills CLI:

```bash
npx skills add R-jed/webgpt-consult -g -y
```

Restart or open a new Codex task, then invoke it explicitly:

```text
Use $webgpt-consult to get a strict GPT-5.6 Sol review of this architecture.
```

You may also clone the repository and load the complete directory through the Skill or Plugin mechanism supported by your Codex environment. `git clone` alone does not register the Skill.

There is no OpenCLI fallback. The Skill stops when the Chrome plugin is unavailable.

## Release layout

```text
webgpt-consult/
├── SKILL.md
├── README.md
├── README_en.md
├── README_Agent.md
├── LICENSE
├── agents/openai.yaml
├── assets/readme/
│   ├── hero.svg
│   ├── workflow.svg
│   └── continuity.svg
├── references/
│   ├── chrome-workflow.md
│   └── context-packet-template.md
└── scripts/
    ├── build_attachment_bundle.py
    ├── check_packet_safety.py
    ├── consult_state.py
    ├── model_router.py
    ├── result_verifier.py
    └── submission_preflight.py
```

AI agents should read [README_Agent.md](README_Agent.md) first and treat [SKILL.md](SKILL.md) as the authoritative execution contract.

## License

[MIT](./LICENSE)
