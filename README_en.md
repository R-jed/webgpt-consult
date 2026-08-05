<p align="center">
  <img src="./assets/logo.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<h3 align="center">GPT-5.6 Sol Pro / High second-opinion Skill for Codex</h3>

<p align="center">Judge locally · Review independently on the Web · Verify · Adopt locally</p>

<p align="center">
  <img src="https://img.shields.io/badge/Codex-Skill-111827" alt="Codex Skill" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB" alt="Python 3.10+" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2EA44F" alt="MIT License" /></a>
  <a href="https://github.com/R-jed/webgpt-consult/stargazers"><img src="https://img.shields.io/github/stars/R-jed/webgpt-consult?style=flat&logo=github" alt="GitHub stars" /></a>
</p>

<p align="center">
  <a href="#about">About</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#safety-and-verification">Safety</a> ·
  <a href="#key-files">Key files</a> ·
  <a href="README.md">中文</a>
</p>

<a id="about"></a>

## About

> **AI agents should read [README_Agent.md](README_Agent.md) first, then treat [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md) as the execution contract.**

`webgpt-consult` lets Codex obtain a verified independent second opinion from GPT-5.6 Sol Pro or High through ChatGPT Web.

Local Codex owns task understanding, the initial judgment, evidence selection, and the final decision. WebGPT reviews the problem independently. After the external result is verified, Codex decides locally what to adopt, reject, or modify.

```text
user task
  → local Codex judgment
  → choose independent / continuation / branch
  → assemble only the evidence needed for the current question
  → credential / attachment preflight
  → ChatGPT Web
  → GPT-5.6 Sol Pro, otherwise High
  → sentinel + task ID verification
  → local adoption decision
```

Why this project exists:

- difficult architecture, debugging, product, and risk decisions often benefit from an independent strong-model review
- WebGPT stays a second-opinion reviewer instead of becoming long-lived project memory
- each review sends only what the current question requires, reducing anchoring and understanding drift from accumulated historical summaries
- model identity, credential hygiene, attachment integrity, and result binding are explicitly verified

<a id="quick-start"></a>

## Quick start

### Requirements

- Python 3.10+
- a current Codex version
- Codex Chrome plugin installed and connected
- ChatGPT Web signed in in Chrome
- an account that actually exposes GPT-5.6 Sol Pro or High

### One-line install

Run this inside Codex:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

The canonical installable Skill lives at `skills/webgpt-consult/`. Using an explicit GitHub skill path lets the Codex installer identify the Skill directory directly and install it as:

```text
~/.codex/skills/webgpt-consult/
```

After installation, try `/webgpt-consult` on the next turn. If the current Codex client has not refreshed its Skill list, restart Codex or open a new task.

If `/skill-installer` is unavailable, update Codex first. `webgpt-consult` depends on the Codex Chrome plugin and does not maintain a separate legacy installer.

> `git clone` is for reading or developing the source only. Cloning the repository does not register the Skill with Codex.

### First use

Implicit invocation is disabled. Invoke the Skill explicitly with `/webgpt-consult`:

```text
/webgpt-consult Perform an independent GPT-5.6 Sol architecture review of this project.
```

Or:

```text
/webgpt-consult Check this fix for overlooked architectural risks and return a second opinion.
```

There is no OpenCLI fallback. The Skill stops when the Chrome plugin is unavailable.

<a id="usage"></a>

## Usage

### Three review modes

| Mode | Best for | Web behavior |
|---|---|---|
| `independent` | deep review, milestone review, adversarial review, architecture reset, a different project, or a materially different question | fresh conversation |
| `continuation` | a clear continuation of the current review when the current Codex conversation can still verify the bound Web conversation | continue the bound conversation |
| `branch` | the same review should continue, but the active conversation has accumulated too much context | `Branch in new chat` from an earlier relevant message |

In `independent` mode, local Codex forms its own judgment first but normally keeps that conclusion private from Sol to reduce anchoring.

Use `continuation` only when the current Codex conversation can identify and verify the immediately relevant Web review. If the binding is missing, identity verification fails, or multiple candidates exist, switch to `independent`.

Use `branch` only to relieve context pressure. After a branch review is successfully verified, the temporary binding moves to the new branch.

### Conversation binding

The Skill never guesses the "previous review" from ChatGPT history. After a Web review completes successfully and its result is verified, the current Codex conversation temporarily retains the smallest useful conversation binding:

```text
Chrome tab/page handle, when available
+ exact chatgpt.com conversation URL, when available
+ previous verified Task-ID
+ previous verified sentinel
```

The tab handle and conversation URL are locators only. The previous `Task-ID + sentinel` are the identity check.

A `continuation` follows this fixed resolution order:

```text
reuse the previously bound Chrome tab/page handle
  ↓ handle unavailable
open the exact conversation URL retained by the current Codex conversation
  ↓
inspect the immediately relevant prior assistant result from a fresh DOM view
  ↓
match previous Task-ID + previous sentinel
  ↓ exact match
allow continuation
```

If any step cannot be verified, use `independent` and open a fresh conversation.

The Skill never locates a prior review using ChatGPT sidebar titles, recent-chat ordering, project names, browser history, approximate timestamps, or semantic similarity.

This binding lives only inside the current Codex conversation. It is not written to files, the repository, a database, or a long-lived cache. A new Codex conversation starts with no Web binding and therefore defaults to `independent`.

`branch` must start from the currently verified binding. The binding moves from the old conversation to the new branch only after the branch result passes verification.

### Web conversation continuity

`webgpt-consult` does not persist review history, conversation URLs, project summaries, accepted decisions, or reviewer memory locally.

Continuity exists only through the temporary binding between the current Codex conversation and the active ChatGPT Web review:

- a direct continuation of the same review uses `continuation`
- a different project normally uses `independent`
- a materially different question in the same project normally uses `independent`
- a context-heavy active conversation uses `branch`
- a lost or unverifiable session binding uses `independent`

`Branch in new chat` inherits all history before the selected message. Choose an earlier point that still contains useful shared context, then send the minimum evidence required for the current question again.

If no useful branch point exists, start a fresh conversation.

This keeps WebGPT independent while still giving the current Codex conversation deterministic short-term continuity when the immediately relevant review thread is available and verifiable.

<a id="safety-and-verification"></a>

## Safety and verification

These boundaries fail closed:

- GPT-5.6 Sol model identity cannot be verified
- neither Pro nor High is usable
- executable credentials are detected in the packet or transmitted text attachments
- required evidence was not actually uploaded
- the final reply cannot be bound to the exact sentinel and task ID

Run preflight immediately before Send:

```bash
python3 ~/.codex/skills/webgpt-consult/scripts/submission_preflight.py packet.md \
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

`result_verifier.py` verifies the latest assistant turn. A sentinel appearing later in prose does not count.

<a id="key-files"></a>

## Key files

| File | Purpose |
|---|---|
| [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md) | authoritative Skill execution contract |
| [README_Agent.md](README_Agent.md) | AI-agent discovery, installation, and support entry point |
| [skills/webgpt-consult/agents/openai.yaml](skills/webgpt-consult/agents/openai.yaml) | display metadata and invocation policy |
| [skills/webgpt-consult/references/chrome-workflow.md](skills/webgpt-consult/references/chrome-workflow.md) | ChatGPT Web browser, conversation binding, and branching workflow |
| [skills/webgpt-consult/references/context-packet-template.md](skills/webgpt-consult/references/context-packet-template.md) | Web review context template |
| [skills/webgpt-consult/scripts/model_router.py](skills/webgpt-consult/scripts/model_router.py) | Pro → High identity and routing policy |
| [skills/webgpt-consult/scripts/submission_preflight.py](skills/webgpt-consult/scripts/submission_preflight.py) | pre-send safety and attachment checks |
| [skills/webgpt-consult/scripts/result_verifier.py](skills/webgpt-consult/scripts/result_verifier.py) | exact external-result binding |

### Repository layout

```text
webgpt-consult/
├── README.md
├── README_en.md
├── README_Agent.md
├── LICENSE
├── assets/
│   └── logo.svg
└── skills/
    └── webgpt-consult/
        ├── SKILL.md
        ├── LICENSE
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   ├── chrome-workflow.md
        │   └── context-packet-template.md
        └── scripts/
            ├── build_attachment_bundle.py
            ├── check_packet_safety.py
            ├── model_router.py
            ├── result_verifier.py
            └── submission_preflight.py
```

## License

[MIT](./LICENSE)
