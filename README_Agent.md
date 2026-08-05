# WebGPT Consult — AI Agent Bootstrap

> **For AI agents.** If you are a human reader, use [README.md](README.md) or [README_en.md](README_en.md).

This file is the discovery, installation-support, and bootstrap guide for AI agents handling `webgpt-consult` on behalf of a user.

It must stay consistent with the public README while being more operational. The goal is that a user can give an Agent this repository URL and the Agent can accurately explain the project, guide installation, verify the expected installation state, show the correct invocation, and enter the real Skill workflow when requested.

Reading this file alone does not authorize installation, environment changes, or an external Web consultation.

`<SKILL_ROOT>` below means the actual installed `webgpt-consult` directory when the Skill is present locally.

---

## 0. First instruction for the Agent

After reading this file, classify the user's intent and follow exactly one path.

### A. The user is asking what this project is

Explain the project from this file. Do not start an installation and do not start a Web consultation.

Minimum explanation:

> `webgpt-consult` is a Codex Skill that lets local Codex obtain a verified GPT-5.6 Sol Pro or High second opinion through ChatGPT Web. Codex prepares the evidence, verifies the returned result, and remains responsible for the final decision.

Mention the Chrome-plugin dependency and the explicit `/webgpt-consult` invocation when relevant.

### B. The user is asking to install the project

Guide or perform installation only because the user explicitly requested it.

Use the Codex-native installation route:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult
```

Then instruct the user to restart Codex and open a new task so installed Skills are reloaded.

If the Agent cannot itself issue a Codex slash command in the current environment, give the exact command to the user. Never claim installation succeeded when the command was not actually executed and verified.

After installation, the expected default location is typically:

```text
~/.codex/skills/webgpt-consult/
```

If `/skill-installer` is unavailable, recommend updating Codex first. Do not invent a legacy installer.

### C. The user is asking how to use the project

Show the explicit user-facing entry point:

```text
/webgpt-consult <review request>
```

Examples:

```text
/webgpt-consult 对这个项目做一次独立的 GPT-5.6 Sol 架构审查。
```

```text
/webgpt-consult Check this fix for overlooked architectural risks.
```

Do not treat an ordinary discussion about the repository as an invocation.

### D. The user actually invokes `/webgpt-consult`

Enter the runtime workflow. Read, in this order:

1. `<SKILL_ROOT>/SKILL.md`
2. `<SKILL_ROOT>/references/chrome-workflow.md`
3. `<SKILL_ROOT>/references/context-packet-template.md`

Then execute the consultation contract defined there.

### E. The user is troubleshooting installation or invocation

Check the smallest relevant set of facts first:

1. Is the current Codex version recent enough to expose `/skill-installer` and the required Chrome capability?
2. Is `webgpt-consult` actually present in the Codex Skill directory?
3. Does the installed directory contain `SKILL.md`, `agents/openai.yaml`, `references/`, and `scripts/`?
4. Was Codex restarted after installation?
5. Is the user invoking `/webgpt-consult` from a new task?
6. Is the Codex Chrome plugin installed and connected?
7. Is ChatGPT Web signed in, with GPT-5.6 Sol Pro or High actually exposed?

Report the first verified blocker. Do not fabricate successful installation or runtime capability.

---

## 1. Project identity

`webgpt-consult` is a Codex-specific Skill for obtaining a verified second opinion from GPT-5.6 Sol Pro or High through ChatGPT Web.

The local Codex session remains authoritative. It owns:

- task understanding;
- initial judgment;
- evidence selection;
- credential and attachment preflight;
- model verification;
- result verification;
- adoption, rejection, or modification of the external advice;
- durable consultation state.

The external model is a reviewer, not the final authority.

The intended chain is:

```text
user task
  -> local Codex judgment
  -> independent or follow-up review
  -> truthful context + evidence
  -> credential / attachment preflight
  -> ChatGPT Web
  -> verified GPT-5.6 Sol Pro, otherwise High
  -> exact sentinel + task-ID verification
  -> local adoption decision
  -> optional durable local consultation-state update
```

This project is useful for difficult architecture, debugging, product, business, risk, and file-grounded review work where an independent strong-model review can materially improve the decision.

---

## 2. Requirements

Before recommending installation or execution, know the runtime requirements:

| Requirement | Why it matters |
|---|---|
| Python 3.10+ | Runtime helper scripts |
| Current Codex | Skill loading and current command/capability support |
| Codex Chrome plugin | Only supported browser transport |
| Chrome signed into ChatGPT Web | Required Web session |
| GPT-5.6 Sol Pro or High available to the account | Required external reviewer tier |

There is no OpenCLI fallback.

If the Chrome plugin is unavailable, the Skill cannot perform the Web consultation.

---

## 3. Installation and activation

### Recommended installation

Use:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult
```

Expected default installation location:

```text
~/.codex/skills/webgpt-consult/
```

After installation:

```text
restart Codex
  -> open a new task
  -> invoke /webgpt-consult
```

`git clone` only downloads source. Do not tell users that cloning alone registers the Skill with Codex.

### Installation verification

When local filesystem access is available, a healthy installed Skill should contain at least:

```text
<SKILL_ROOT>/
├── SKILL.md
├── README_Agent.md
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

Do not require development-only files such as tests or CI configuration. The release repository intentionally contains runtime and user-facing assets only.

### Suggested installation report

When helping a user install or diagnose the Skill, report in a compact form such as:

```text
WebGPT Consult status

Repository: R-jed/webgpt-consult
Install method: /skill-installer
Expected Skill path: ~/.codex/skills/webgpt-consult/
Skill files: present / missing / not checked
Codex restart required: yes / completed
Chrome plugin: connected / missing / not checked
ChatGPT Web login: ready / missing / not checked
GPT-5.6 Sol Pro or High: available / unavailable / not checked
Next command: /webgpt-consult <review request>
```

Only mark a field as ready when it was actually verified.

---

## 4. User-facing invocation

Implicit invocation is disabled in `agents/openai.yaml`.

The supported user-facing entry is:

```text
/webgpt-consult <review request>
```

Representative requests:

```text
/webgpt-consult Deep review this architecture before implementation.
```

```text
/webgpt-consult Review this debugging diagnosis and identify the strongest counterargument.
```

```text
/webgpt-consult Continue the previous consultation using the new implementation evidence.
```

The Agent should preserve the user's actual task rather than replacing it with a generic review prompt.

---

## 5. Review intent

The Skill supports two consultation intents.

### Independent review

Use a fresh ChatGPT Web conversation for:

- deep review;
- milestone review;
- adversarial review;
- architecture reset;
- materially different questions;
- requests for an independent second opinion.

Local Codex forms its own judgment first but normally keeps that conclusion private from Sol to reduce anchoring.

Share the local proposal only when the user explicitly wants Sol to attack, compare, or revise it.

### Follow-up review

Reuse a Web conversation only when the new request clearly continues one existing consultation.

Useful continuity signals include:

- explicit user instruction to continue the previous consultation;
- one unique PR, issue, branch, workstream, or named artifact;
- one unambiguous locally stored consultation state.

If continuity is ambiguous, start fresh.

---

## 6. Durable consultation state

Long-lived consultation state belongs to local Codex, not to the Web conversation.

State lives under:

```text
~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json
```

Project identity includes the canonical checkout path so separate clones or worktrees do not silently share state.

A snapshot may contain locally adopted reusable information such as:

- user intent;
- standing constraints;
- accepted decisions;
- rejected or deferred paths;
- open questions;
- evidence references;
- current project state;
- last verified consultation task;
- current Web conversation URL when useful.

It is not a transcript and is not a copy of Sol's raw answer.

Use `scripts/consult_state.py` only during actual Skill execution or troubleshooting that requires consultation-state inspection.

---

## 7. Web conversation context pressure

Treat a ChatGPT Web conversation as a reusable execution container, not durable memory.

If the stored conversation:

- cannot be opened;
- becomes context-limited;
- visibly forgets material decisions;
- or otherwise becomes unreliable;

stop using it and create a fresh ChatGPT conversation.

Restore continuity with:

```text
locally adopted consultation snapshot
+ current delta
+ current evidence
```

Continue the same local consultation identity where appropriate, then replace the stored Web conversation URL after the replacement result is verified and locally adopted.

Correctness does not depend on `Branch in new chat`, historical message IDs, browser lineage, or a permanently open browser tab.

---

## 8. Safety and evidence integrity

These boundaries fail closed:

- GPT-5.6 Sol model identity cannot be verified;
- neither verified Pro nor verified High is usable;
- executable credentials are detected in transmitted text;
- required evidence was not actually transmitted;
- the latest result cannot be bound to the exact sentinel and task ID.

Never transmit known executable credentials, cookies, private keys, browser profiles, session material, local consultation-state files, or unrelated private context.

Never claim an artifact was reviewed unless its actual contents were transmitted.

Text attachments are scanned before Send. Non-text attachments require explicit local review before the binary confirmation flag may be used. That confirmation cannot override a detected credential finding.

---

## 9. Model policy

The supported model route is fixed:

```text
verified usable GPT-5.6 Sol Pro
    -> otherwise verified usable GPT-5.6 Sol High
    -> otherwise fail closed
```

`scripts/model_router.py` is the deterministic policy source.

A generic GPT-5 Pro label or a DOM locator does not prove GPT-5.6 Sol identity. The selected tier must be verified from fresh browser state.

---

## 10. Result verification and local adoption

The external response must begin with:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

After generation completes, the latest assistant turn is extracted and verified with `scripts/result_verifier.py`.

A verified Sol response is advisory evidence. Local Codex compares it with local facts and its own prior judgment, then decides what to:

- adopt;
- reject;
- modify;
- leave unresolved.

For an independent review, preserve meaningful disagreement between Codex and Sol when it matters. Do not manufacture consensus.

Update durable consultation state only after local adoption.

---

## 11. Runtime file order

When `/webgpt-consult` is actually invoked, read:

```text
1. SKILL.md
2. references/chrome-workflow.md
3. references/context-packet-template.md
```

Supporting runtime files:

| File | Purpose |
|---|---|
| `agents/openai.yaml` | Display metadata and explicit invocation policy |
| `scripts/model_router.py` | Pro -> High routing policy |
| `scripts/submission_preflight.py` | Exact pre-Send safety and attachment checks |
| `scripts/check_packet_safety.py` | Credential and unsafe-packet scanning |
| `scripts/build_attachment_bundle.py` | Faithful bundling of multiple text artifacts |
| `scripts/result_verifier.py` | Exact sentinel and task-ID binding |
| `scripts/consult_state.py` | Durable local consultation-state management |

If this guide and `SKILL.md` ever conflict during execution, `SKILL.md` is authoritative.

---

## 12. Repository layout

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

---

## 13. How to answer common user requests

| User request | Agent response |
|---|---|
| "What is this project?" | Explain the verified GPT-5.6 Sol second-opinion workflow and local Codex authority. |
| "Should I install it?" | Recommend it when the user regularly wants independent WebGPT review from Codex and has the Chrome/model prerequisites. |
| "Install it." | Use or provide `/skill-installer install https://github.com/R-jed/webgpt-consult`, then require Codex restart and a new task. |
| "How do I use it?" | Show `/webgpt-consult <review request>`. |
| "Does it run automatically?" | No. Implicit invocation is disabled. |
| "Does Sol replace Codex?" | No. Sol is an external reviewer; local Codex makes the adoption decision. |
| "What if the Web chat is full?" | Start a fresh Web conversation and restore from locally adopted consultation state plus the current delta and evidence. |
| "Can it use another browser or OpenCLI?" | The supported browser transport is the Codex Chrome plugin; there is no OpenCLI fallback. |
| "Is git clone enough?" | No. Cloning downloads source but does not register the Skill. |

---

## 14. Failure handling

During discovery or installation support, continue helping the user even when the Skill is not yet installed.

During an actual `/webgpt-consult` execution:

- missing `SKILL.md` or required scripts -> stop and report the incomplete installation;
- Chrome plugin unavailable -> stop and report the missing browser capability;
- ChatGPT not signed in -> ask the user to sign in;
- no verified Pro or High -> fail closed;
- preflight failure -> do not Send;
- attachment upload failure -> do not claim the artifact was reviewed;
- result verification failure -> mark the consultation incomplete;
- ambiguous follow-up continuity -> start fresh;
- unavailable or context-limited Web conversation -> restore into a fresh Web conversation from verified local state.

Do not claim success for any installation, model selection, upload, consultation, or verification step that was not actually observed.
