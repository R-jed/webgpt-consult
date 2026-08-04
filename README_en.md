<h1 align="center">webgpt consult</h1>

<p align="center">
  <strong>A Codex Skill for a verified GPT-5.6 Sol Pro/High second opinion</strong><br/>
  Web chats are disposable; local judgment and adopted project state are durable
</p>

<p align="center">
  <a href="README.md">中文</a> ·
  <a href="SKILL.md">Skill contract</a> ·
  <a href="README_Agent.md">AI Agent guide</a>
</p>

## Core purpose

`webgpt-consult` lets local Codex send a carefully prepared difficult problem and truthful evidence to ChatGPT Web for a GPT-5.6 Sol second opinion. The external answer remains advisory. Local Codex decides what to adopt, reject, or modify.

The supported path is intentionally narrow:

```text
local Codex judgment
  -> independent or follow-up review
  -> truthful context + evidence
  -> fail-closed preflight
  -> verified GPT-5.6 Sol Pro, then High
  -> exact result verification
  -> local adoption decision
  -> optional durable local state update
```

## Independent vs follow-up review

Use `independent` for milestone reviews, deep reviews, adversarial checks, architecture resets, or materially different questions. It always starts a fresh ChatGPT conversation. Codex still forms its own judgment first, but normally keeps that conclusion private from Sol to reduce anchoring.

Use `follow-up` only for a clear continuation of one consultation. Explicit continuation or one unique anchor such as a PR, issue, branch, or named artifact can justify reuse of the stored Web conversation.

If the match is ambiguous, start fresh. Repeating some context is safer than attaching the request to the wrong consultation.

## Durable continuity

Long-lived consultation state lives locally:

```text
~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json
```

Each snapshot stores only locally adopted reusable state such as user intent, standing constraints, accepted decisions, rejected or deferred paths, open questions, evidence references, and current state.

It is not a transcript and it is not a backup of Sol's raw answer.

List consultations for the current checkout with:

```bash
python3 scripts/consult_state.py --project-root . list
```

A corrupt state file is skipped with a warning instead of blocking the Skill. Project identity includes the canonical checkout path so separate clones or worktrees do not silently share consultation state.

## When the Web chat reaches context pressure

A ChatGPT Web conversation is only a reusable execution container.

If the stored chat is unavailable, context-limited, visibly forgetting important decisions, or otherwise unreliable, stop using it and open a fresh conversation. Restore the same local consultation from:

```text
durable local snapshot
+ current delta
+ current evidence
```

The local `consult_id` remains the same and the stored `conversation_url` is replaced after the new result is verified and locally adopted.

Correctness no longer depends on `Branch in new chat`, historical message IDs, rollover counters, root tasks, branch bases, or continuity capsules.

## Safety and evidence integrity

These remain fail-closed boundaries:

- GPT-5.6 Sol model identity cannot be verified
- neither Pro nor High is usable
- executable credentials are detected in transmitted text
- required evidence was not actually transmitted
- exact sentinel/task binding fails

Run preflight immediately before Send:

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-... \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --attachment ./src/example.py
```

Non-text attachments require local manual review before `--confirm-unscanned-binary` may be used. That confirmation never overrides a detected credential finding.

## Model routing

```text
verified usable GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
verified usable GPT-5.6 Sol High
      ↓ unavailable
fail closed
```

`model_router.py` is the deterministic policy source. DOM refs are click locators only, and generic GPT-5 Pro evidence does not establish GPT-5.6 Sol identity.

## Result verification

The external reply must start with:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

`scripts/result_verifier.py` verifies the extracted latest assistant turn locally. A sentinel merely appearing later in prose does not count.

## Requirements

- Python >= 3.10
- Codex
- Codex Chrome plugin installed and connected
- ChatGPT Web signed in in the selected Chrome profile
- GPT-5.6 Sol Pro or High actually exposed by the account

There is no OpenCLI fallback.

## Development validation

```bash
git clone https://github.com/R-jed/webgpt-consult.git
cd webgpt-consult
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile scripts/*.py
```

Cloning the repository only downloads source. It does not register the Skill with Codex.

## Repository layout

```text
webgpt-consult/
├── SKILL.md
├── README.md
├── README_en.md
├── README_Agent.md
├── agents/openai.yaml
├── references/
│   ├── chrome-workflow.md
│   └── context-packet-template.md
├── scripts/
│   ├── build_attachment_bundle.py
│   ├── check_packet_safety.py
│   ├── consult_state.py
│   ├── model_router.py
│   ├── result_verifier.py
│   └── submission_preflight.py
├── tests/
└── VALIDATION.md
```

AI agents should read [README_Agent.md](README_Agent.md) first and treat [SKILL.md](SKILL.md) as the authoritative execution contract.

## License

MIT
