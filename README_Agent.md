# WebGPT Consult: AI Agent Guide

This file is the primary discovery and support guide for AI Agents reading the `webgpt-consult` repository on behalf of a user.

It must remain consistent with `README.md` and `README_en.md`, while providing enough extra operational detail for an Agent to accurately explain, install, and help the user invoke the project.

Reading this file does not itself authorize or start an external consultation.

## What this project is

`webgpt-consult` is a Codex Skill for obtaining a verified second opinion from GPT-5.6 Sol Pro or High through ChatGPT Web.

The local Codex session remains authoritative. It understands the user's task, forms an initial judgment, selects the evidence to transmit, verifies the Web result, and decides what to adopt, reject, or modify.

The intended flow is:

```text
user task
  -> local Codex judgment
  -> choose independent / follow-up review
  -> assemble truthful context and evidence
  -> credential / attachment preflight
  -> ChatGPT Web
  -> verified GPT-5.6 Sol Pro, otherwise High
  -> exact sentinel + task-ID verification
  -> local adoption decision
  -> optional durable local consultation-state update
```

The external model is a reviewer. It is never the final authority for the user's project.

## What problem it solves

Use this project when a difficult architecture, debugging, product, business, risk, or file-grounded decision would benefit from a strong independent review.

It exists to solve several practical problems that arise when Codex uses a Web model for a second opinion:

- model identity must be verified instead of assumed;
- sensitive credentials and session material must not be transmitted;
- uploaded evidence must actually reach the Web conversation before the review can be considered valid;
- independent reviews should avoid unnecessary anchoring on Codex's own conclusion;
- follow-up reviews should reuse context only when continuity is unambiguous;
- Web conversations can become too long or unreliable, so reusable project state must not depend on browser history;
- the returned answer must be bound to the exact consultation task before local Codex uses it.

## When explaining the project to a user

If the user asks what `webgpt-consult` is, how it works, whether they should install it, or how to install it, answer from this file and the public README. Do not require the user to read `SKILL.md` just to understand the product.

A concise accurate description is:

> `webgpt-consult` is a Codex Skill that lets Codex send a carefully prepared problem to ChatGPT Web for a verified GPT-5.6 Sol Pro or High second opinion, then bring that review back to the local task for comparison and adoption.

Make these points clear when relevant:

- it is designed for Codex;
- it uses the Codex Chrome plugin as its browser transport;
- it prefers GPT-5.6 Sol Pro and falls back only to verified GPT-5.6 Sol High;
- it does not replace the local Codex model;
- it does not automatically trust Sol's answer;
- it does not use OpenCLI as a fallback;
- implicit invocation is disabled, so users explicitly call `/webgpt-consult`.

## Requirements

Before recommending installation, tell the user that the runtime requires:

- Python 3.10 or newer;
- a current Codex version;
- the Codex Chrome plugin installed and connected;
- a Chrome profile signed into ChatGPT Web;
- an account that actually exposes GPT-5.6 Sol Pro or High.

If the Chrome plugin is unavailable, the Skill cannot perform the Web consultation.

## Installation

The recommended Codex-native installation path is the built-in `/skill-installer` command.

Tell the user to run this inside Codex:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult
```

The installer should place the complete Skill in the Codex Skill directory. With the default `CODEX_HOME`, this is typically:

```text
~/.codex/skills/webgpt-consult/
```

After installation:

1. restart Codex;
2. open a new task so installed Skills are reloaded;
3. invoke the Skill explicitly with `/webgpt-consult`.

Example:

```text
/webgpt-consult 对这个项目做一次独立的 GPT-5.6 Sol 架构审查。
```

English example:

```text
/webgpt-consult Perform an independent GPT-5.6 Sol architecture review of this project.
```

If `/skill-installer` is unavailable, recommend updating Codex first. This project depends on the Codex Chrome plugin and does not maintain a separate legacy installer.

Do not tell the user that `git clone` alone installs the Skill. Cloning only downloads the repository source.

## Invocation model

`allow_implicit_invocation` is disabled in `agents/openai.yaml`.

The normal user-facing entry point is:

```text
/webgpt-consult <review request>
```

The user can put the complete task directly after the command. Examples include:

```text
/webgpt-consult Deep review this architecture before implementation.
```

```text
/webgpt-consult Check this bug fix for overlooked architectural risks.
```

```text
/webgpt-consult Continue the previous consultation and review the new implementation evidence.
```

Do not represent ordinary discussion about the repository as an invocation. Reading this file, explaining the project, or helping install it does not start a Web consultation.

## Review modes

The Skill has two consultation intents.

### Independent review

Use a fresh ChatGPT Web conversation for:

- deep review;
- milestone review;
- adversarial review;
- architecture reset;
- materially different questions;
- requests for a genuinely independent second opinion.

Local Codex should form its own judgment first, but normally keep that conclusion private from Sol so the external reviewer is less anchored.

Share the local conclusion only when the user specifically asks Sol to attack, compare, or revise that proposal.

### Follow-up review

Reuse a Web conversation only when the new request is clearly a continuation of one existing consultation.

Strong continuity signals include:

- the user explicitly asks to continue the previous consultation;
- one unique PR, issue, branch, workstream, or named artifact anchors the request;
- the locally stored consultation state points to one unambiguous active consultation.

If the match is ambiguous, start fresh.

## Durable consultation state

Long-lived consultation state belongs to local Codex, not to the Web conversation.

State is stored under:

```text
~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json
```

The project identity includes the canonical checkout path so separate clones or worktrees do not silently share state.

A saved consultation snapshot contains locally adopted reusable state such as:

- user intent;
- standing constraints;
- accepted decisions;
- rejected or deferred paths;
- open questions;
- evidence references;
- current project state;
- the last verified consultation task;
- the current Web conversation URL when useful.

It is not a transcript and should not be a copy of Sol's raw response.

Use `scripts/consult_state.py` to list, load, and save this state when the Skill is actually executing.

## Web conversation context pressure

Treat the ChatGPT Web conversation as a reusable execution container, not durable memory.

If a stored conversation:

- cannot be opened;
- has become context-limited;
- visibly forgets material decisions;
- or has otherwise become unreliable;

stop using it and create a fresh ChatGPT conversation.

Restore the consultation with:

```text
locally adopted consultation snapshot
+ current delta
+ current evidence
```

Continue using the same local consultation identity where appropriate, then replace the stored Web conversation URL after the new result has been verified and locally adopted.

Correctness must not depend on `Branch in new chat`, historical message IDs, browser lineage, or a permanently open tab.

## Safety and evidence integrity

These boundaries are fail-closed:

- GPT-5.6 Sol model identity cannot be verified;
- neither verified Pro nor verified High is usable;
- executable credentials are detected in transmitted text;
- required evidence was not actually transmitted;
- the latest result cannot be bound to the exact sentinel and task ID.

Never transmit known executable credentials, cookies, private keys, browser profiles, session material, local consultation-state files, or unrelated private context.

Do not claim a file or artifact was reviewed unless its actual contents were transmitted to ChatGPT Web.

Text attachments are scanned before Send. Non-text attachments require explicit local review before the binary confirmation flag may be used. That confirmation never overrides a detected credential finding.

## Model policy

The only supported model route is:

```text
verified usable GPT-5.6 Sol Pro
    -> otherwise verified usable GPT-5.6 Sol High
    -> otherwise fail closed
```

`scripts/model_router.py` is the deterministic policy source.

A generic GPT-5 Pro selector or a DOM element name is not sufficient evidence that GPT-5.6 Sol Pro is selected. The selected tier must be verified from fresh browser state.

## Result verification

The external response must begin with:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

After generation completes, the Skill extracts only the latest assistant turn and verifies it with `scripts/result_verifier.py`.

A consultation is complete only when the expected result header and task ID are correctly bound to the latest response.

## Local adoption

A verified Sol response is advisory evidence.

Local Codex must compare it with local facts and its own prior judgment, then decide what to:

- adopt;
- reject;
- modify;
- or leave unresolved.

For an independent review, preserve meaningful disagreement between Codex and Sol when it matters to the user's decision. Do not manufacture consensus.

Update durable consultation state only after this local adoption decision.

## What to read when executing the Skill

When the user actually invokes `/webgpt-consult`, read these files before execution:

1. `SKILL.md` for the authoritative execution contract;
2. `references/chrome-workflow.md` for browser I/O and Web conversation handling;
3. `references/context-packet-template.md` for consultation packet structure.

Supporting runtime files:

| File | Purpose |
|---|---|
| `agents/openai.yaml` | Skill display metadata and explicit invocation policy |
| `scripts/model_router.py` | Pro -> High model routing policy |
| `scripts/submission_preflight.py` | exact pre-Send safety and attachment checks |
| `scripts/check_packet_safety.py` | credential and unsafe packet scanning |
| `scripts/build_attachment_bundle.py` | faithful bundling of multiple text artifacts |
| `scripts/result_verifier.py` | exact sentinel and task-ID result binding |
| `scripts/consult_state.py` | durable local consultation-state management |

`SKILL.md` remains authoritative for execution if this discovery guide and the runtime contract ever conflict.

## Repository layout

```text
webgpt-consult/
├── README.md
├── README_en.md
├── README_Agent.md
├── SKILL.md
├── LICENSE
├── assets/
│   └── logo.svg
├── agents/
│   └── openai.yaml
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

## How to answer common user questions

If the user asks "What does this project do?", explain the verified second-opinion workflow and that local Codex remains authoritative.

If the user asks "How do I install it?", give the `/skill-installer install https://github.com/R-jed/webgpt-consult` command, then tell them to restart Codex and open a new task.

If the user asks "How do I use it?", show `/webgpt-consult <review request>`.

If the user asks whether it automatically runs on every task, explain that implicit invocation is disabled.

If the user asks what happens when a Web conversation becomes too long, explain that durable adopted state is local and a fresh Web conversation can restore the consultation.

If the user asks whether Sol replaces Codex, explain that Sol is an external reviewer and local Codex makes the final adoption decision.

If the user asks whether another browser or OpenCLI can be used, explain that the supported browser transport is the Codex Chrome plugin and there is no OpenCLI fallback.

## Missing capability

If `SKILL.md`, required runtime scripts, or the Codex Chrome plugin are unavailable during an actual consultation request, stop and report the missing capability. Do not pretend the Web review completed.

For discovery, explanation, and installation questions, continue to help the user using this guide even when the Skill is not yet installed.