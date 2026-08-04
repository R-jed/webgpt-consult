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

## Context-window rollover

When a workstream reaches clear conversation/context-length pressure, the Skill does not keep retrying in the same overfull parent and does not branch from the latest message.

`Branch in new chat` inherits history up to the selected message. Branching from the latest message therefore keeps the long tail and provides little real compaction.

The first verified consultation creates two anchors: immutable `root_task_id` identifies the full workstream lineage, while `branch_base_task_id` identifies the compact baseline that actually exists in the current ChatGPT conversation. They are initially the same.

On rollover, Codex branches from the active branch base and sends a cumulative `CONTINUITY_CAPSULE_V1` containing the reusable state accumulated since that base:

```text
current long conversation
        ↓
active branch-base assistant result
        ↓
Branch in new chat
        ↓
CONTINUITY_CAPSULE_V1
  accepted decisions
  rejected paths
  standing constraints
  open questions
  evidence index
  current state
  current ask
        ↓
continue the same workstream with bounded history
```

The capsule is built locally from project evidence and verified consultation results. It is a state-transfer artifact, not a casual transcript summary, and the overfull Web ChatGPT thread is not trusted to summarize itself as the source of truth. Required sections must be populated and the capsule explicitly attests that no material reusable context was intentionally omitted.

If `Branch in new chat` succeeds, the active branch base remains available in the child conversation, so `branch_base_task_id` stays unchanged.

If the Web UI cannot create a reliable branch, the branch-base message cannot be uniquely found, the parent cannot be loaded, or inherited baseline content is wrong, the Skill falls back to `rollover_fresh`: a completely fresh ChatGPT conversation receives the same standalone capsule plus any current evidence that still needs to be transmitted. The first verified result in that fresh conversation becomes the new active `branch_base_task_id`, while the original `root_task_id` remains immutable.

The registry preserves the current URL, recent parent URLs, root task, active branch base, rollover count/mode, and capsule hash so the workstream lineage remains auditable.

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
│   ├── continuity-capsule-template.md
│   └── context-packet-template.md
├── scripts/
│   ├── build_attachment_bundle.py
│   ├── check_packet_safety.py
│   ├── continuity_capsule.py
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
