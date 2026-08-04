<h1 align="center">webgpt consult</h1>

<p align="center">
  <strong>A Codex Skill for verified GPT-5.6 Sol Pro/High second-opinion reviews</strong><br/>
  Preserve project context while keeping final judgment local
</p>

<p align="center">
  <a href="README.md">中文</a> ·
  <a href="SKILL.md">Skill contract</a> ·
  <a href="README_Agent.md">AI Agent guide</a>
</p>

## What it does

`webgpt-consult` lets Codex send a carefully prepared problem and its evidence to ChatGPT Web for a GPT-5.6 Sol second opinion. The external answer remains advisory. Local Codex verifies the evidence and owns the final adoption decision.

The supported path is intentionally narrow:

```text
local judgment
  -> project/workstream conversation routing
  -> context packet + exact attachments
  -> fail-closed preflight
  -> Codex Chrome plugin
  -> GPT-5.6 Sol Pro, then High
  -> exact result verification
  -> local adoption decision
```

## Project-scoped conversation continuity

The Skill no longer treats every consultation as a brand-new ChatGPT thread, and it does not force an entire repository into one permanent conversation either.

A local registry is stored at:

```text
~/.codex/webgpt-consult/conversations.json
```

One project may keep multiple workstreams:

```text
Project
  architecture-routing  -> conversation A
  performance-debugging -> conversation B
  release-risk          -> conversation C
```

A direct follow-up to the same decision, bug, PR, branch, artifact, architecture question, or implementation plan should reuse the matching registered conversation. A materially different topic, an independent review, a context reset, an ambiguous match, or a different project should start a fresh conversation.

Continuity survives tab or browser closure because the registry stores the canonical ChatGPT conversation URL rather than tab state.

## Safety and evidence integrity

Run one preflight over the exact payload before Send:

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-20260804-220000 \
  --sentinel WEBGPT_CONSULT_RESULT_20260804_220000 \
  --attachment ./src/example.py
```

Text packets and text attachments are scanned for credential-like material. Known credentials fail closed.

Non-text attachments are blocked as `manual_review_required` until the Agent confirms they are intended and have been locally reviewed. That confirmation never overrides a detected credential.

The text bundle builder also fails by default on missing explicit inputs, empty bundles, silent truncation, silent size-limit omissions, and credential findings.

## Model routing

Only these tiers are supported:

```text
GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
GPT-5.6 Sol High
      ↓ unavailable
fail closed
```

`model_router.py` is the deterministic model policy source. DOM references are click locators, not model identity evidence. A generic GPT-5 Pro selector does not establish GPT-5.6 Sol identity.

## Result verification

The assistant reply must begin with these two non-empty lines:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

Then verify the extracted assistant turn locally with `scripts/result_verifier.py`. A sentinel merely appearing later in prose does not count.

## Requirements

- Python >= 3.10
- Codex
- Codex Chrome plugin installed and connected
- ChatGPT Web signed in in the selected Chrome profile
- GPT-5.6 Sol Pro or High actually exposed by the account

Plugin availability can depend on plan, workspace policy, role, and supported surface. There is no OpenCLI fallback.

## Installation

Install the complete Skill directory through the Skills / Plugin mechanism available in your Codex environment so `SKILL.md`, `scripts/`, `references/`, and `agents/` remain together.

For source development:

```bash
git clone https://github.com/R-jed/webgpt-consult.git
cd webgpt-consult
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Cloning the repository only downloads the source. It does not by itself register the Skill with Codex.

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
│   ├── conversation_registry.py
│   ├── model_router.py
│   ├── result_verifier.py
│   └── submission_preflight.py
├── tests/
└── VALIDATION.md
```

AI agents should read [README_Agent.md](README_Agent.md) first and treat [SKILL.md](SKILL.md) as the authoritative execution contract.

## License

MIT
