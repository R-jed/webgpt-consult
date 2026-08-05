# WebGPT Consult: AI Agent Bootstrap

> **For AI agents.** Human readers should use [README.md](README.md) or [README_en.md](README_en.md).

This file is the discovery, installation-support, and bootstrap guide for AI agents handling `webgpt-consult` on behalf of a user.

A user should be able to give an Agent this repository URL and receive an accurate explanation, installation path, activation steps, invocation example, troubleshooting path, and runtime handoff.

Reading this file alone does not authorize installation, environment changes, or an external Web review.

The repository root is the project/discovery surface. The canonical installable Skill package is:

```text
skills/webgpt-consult/
```

`<SKILL_ROOT>` means the installed copy of that directory, normally `~/.codex/skills/webgpt-consult/`.

---

## 0. First instruction for the Agent

Classify the user's intent and follow exactly one path.

### A. The user is asking what this project is

Explain the project from this file. Do not install anything and do not start a Web review.

Minimum explanation:

> `webgpt-consult` is a Codex Skill that lets local Codex obtain a verified GPT-5.6 Sol Pro or High second opinion through ChatGPT Web. Codex prepares the current evidence, verifies the returned result, and remains responsible for the final decision.

Mention the Codex Chrome plugin dependency and explicit `/webgpt-consult` invocation when relevant.

### B. The user is asking to install the project

Use the canonical Skill path, not the repository root:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

This path maps directly to the installable Skill directory and installs under the path basename `webgpt-consult`.

Expected default destination:

```text
~/.codex/skills/webgpt-consult/
```

After a successful installation, tell the user to try `/webgpt-consult` on the next turn. Restart Codex or open a new task only if the current client has not refreshed its Skill list.

If the Agent cannot issue the Codex slash command in the current environment, give the exact command to the user. Never claim installation succeeded when it was not executed and verified.

If `/skill-installer` is unavailable, recommend updating Codex first. Do not invent a legacy installer.

If the destination already exists, do not claim that running the installer again updated the Skill. The current installer is expected to stop rather than silently overwrite an existing Skill directory. Report the existing installation and let the user decide whether to replace/update it.

### C. The user is asking how to use the project

Show the explicit entry point:

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

Do not treat ordinary discussion about the repository as an invocation.

### D. The user actually invokes `/webgpt-consult`

Enter the runtime workflow. Read from the installed Skill root in this order:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md
```

Then execute the review contract defined there.

### E. The user is troubleshooting installation or invocation

Check the smallest relevant set of facts first:

1. Is the current Codex version recent enough to expose `/skill-installer` and the required Chrome capability?
2. Is `~/.codex/skills/webgpt-consult/` present?
3. Does the installed directory contain `SKILL.md`, `LICENSE`, `agents/openai.yaml`, `references/`, and `scripts/`?
4. If just installed, has the user tried the next turn before assuming a restart is required?
5. Is the user invoking `/webgpt-consult` explicitly?
6. Is the Codex Chrome plugin installed and connected?
7. Is ChatGPT Web signed in, with GPT-5.6 Sol Pro or High actually exposed?

Report the first verified blocker. Do not fabricate installation or runtime capability.

---

## 1. Project identity

`webgpt-consult` is a Codex-specific Skill for obtaining a verified independent second opinion from GPT-5.6 Sol Pro or High through ChatGPT Web.

Local Codex remains authoritative. It owns task understanding, initial judgment, evidence selection, preflight, model verification, result verification, and the final adoption decision.

WebGPT is an external reviewer. It does not maintain a long-lived model of the user's project and is not a second project manager.

The intended chain is:

```text
user task
  -> local Codex judgment
  -> choose independent / continuation / branch
  -> current truthful context + evidence
  -> credential / attachment preflight
  -> ChatGPT Web
  -> verified GPT-5.6 Sol Pro, otherwise High
  -> exact sentinel + task-ID verification
  -> local adoption decision
```

Use this project for difficult architecture, debugging, product, business, risk, and file-grounded review work where a strong independent second opinion can improve the decision.

---

## 2. Requirements

| Requirement | Why it matters |
|---|---|
| Python 3.10+ | Runtime helper scripts |
| Current Codex | Skill loading and current command/capability support |
| Codex Chrome plugin | Only supported browser transport |
| Chrome signed into ChatGPT Web | Required Web session |
| GPT-5.6 Sol Pro or High available to the account | Required external reviewer tier |

There is no OpenCLI fallback.

---

## 3. Installation contract

### Canonical source

The installable unit is exactly:

```text
R-jed/webgpt-consult
└── skills/
    └── webgpt-consult/
```

Use this URL:

```text
https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

Do not use the repository root URL as the preferred install target. The canonical path makes the Skill directory explicit and lets the installer derive the correct destination name from the path basename.

### Recommended command

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

### Expected installed shape

```text
<SKILL_ROOT>/
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

`README_Agent.md`, the public READMEs, and the repository logo are project/discovery files. The MIT license is mirrored into the canonical Skill package so the installed copy carries its license text.

### Activation

Preferred activation flow:

```text
install
  -> next Codex turn
  -> /webgpt-consult <review request>
```

Fallback only when the client does not refresh the Skill list:

```text
restart Codex or open a new task
  -> /webgpt-consult <review request>
```

### Installation report

When useful, report:

```text
WebGPT Consult status

Repository: R-jed/webgpt-consult
Skill source: skills/webgpt-consult/
Install method: /skill-installer
Expected Skill path: ~/.codex/skills/webgpt-consult/
Skill files: present / missing / not checked
Skill refresh: available next turn / restart needed / not checked
Chrome plugin: connected / missing / not checked
ChatGPT Web login: ready / missing / not checked
GPT-5.6 Sol Pro or High: available / unavailable / not checked
Next command: /webgpt-consult <review request>
```

Only mark a field as ready when it was actually verified.

`git clone` downloads source for reading or development. It does not register the Skill with Codex.

---

## 4. User-facing invocation

Implicit invocation is disabled in `<SKILL_ROOT>/agents/openai.yaml`.

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
/webgpt-consult Continue the current Web review using the new implementation evidence.
```

Preserve the user's actual task rather than replacing it with a generic review prompt.

---

## 5. Review modes

The Skill uses one mode field with three possible values.

### `independent`

Start a fresh ChatGPT Web conversation for deep reviews, milestone reviews, adversarial reviews, architecture resets, different projects, materially different questions, or any request that benefits from an unanchored second opinion.

Local Codex forms its own judgment first but normally keeps that conclusion private from Sol to reduce anchoring.

### `continuation`

Continue the current Web conversation only when the new request clearly continues the same review and the current Codex session can resolve and verify the bound Web conversation.

If the relationship is ambiguous, the session binding is unavailable, the project changed, or the question changed materially, use `independent`.

### `branch`

Use `Branch in new chat` when the same review should continue but the bound Web conversation has accumulated enough history to create context pressure.

After branching:

```text
confirm branch
  -> re-verify GPT-5.6 Sol tier
  -> send current task + minimum evidence
  -> verify the result
  -> bind the current Codex session to the new branch
```

If no useful branch point exists or the branch is unreliable, use `independent`.

---

## 6. How the same Web conversation is found

The Skill does not search ChatGPT history for a conversation that merely looks related.

Instead, it uses a temporary binding that exists only inside the current Codex conversation.

After a Web review succeeds and the returned result passes exact Task-ID and sentinel verification, retain the smallest browser identity currently available:

```text
review_tab_handle: <Chrome tab/page handle when available>
review_conversation_url: <exact chatgpt.com conversation URL when available>
last_task_id: <verified prior Task-ID>
last_sentinel: <verified prior sentinel>
```

For `continuation`, resolve in this order:

```text
previous bound Chrome tab/page handle
  -> exact previously observed ChatGPT conversation URL
  -> fresh DOM inspection
  -> match previous Task-ID + sentinel
  -> continuation allowed
```

The handle and URL locate the candidate page. The previous Task-ID and sentinel verify that it is the correct review conversation.

If the tab is gone, the URL is unavailable, the prior Task-ID/sentinel cannot be matched, or multiple candidate conversations exist, use `independent`.

Never choose a previous Web review based only on sidebar title, recent-chat ordering, browser history, project name, approximate time, or semantic similarity.

A successful `independent` review establishes the current binding. A successful `continuation` refreshes it. A successful `branch` replaces it with the new branch.

The binding lives only for the current Codex conversation. Starting a new Codex conversation means there is no prior Web binding, so the safe default is `independent`.

---

## 7. No local reviewer memory

Do not create local review-history files, conversation registries, project summaries, accepted-decision caches, stored ChatGPT conversation URLs, or review IDs for future reuse.

The Web model receives what is needed for the current review. Historical conclusions are reintroduced only when they remain factual inputs required by the current question.

An open Web tab and the current Codex session binding may provide temporary continuity. They are not project memory.

---

## 8. Context pressure and branching

Use `continuation` while the bound Web review remains compact and useful.

Move to `branch` when the same review should continue but the active conversation has accumulated too much history.

```text
resolve and verify current binding
  -> identify an earlier useful branch point
  -> Branch in new chat
  -> re-verify GPT-5.6 Sol Pro / High
  -> send current task + minimum necessary evidence
  -> verify result
  -> replace binding with new branch
```

If no suitable branch point exists, start fresh with `independent`.

---

## 9. Safety and evidence integrity

These boundaries fail closed:

- GPT-5.6 Sol model identity cannot be verified;
- neither verified Pro nor verified High is usable;
- executable credentials are detected in transmitted text;
- required evidence was not actually transmitted;
- the latest result cannot be bound to the exact sentinel and task ID.

Never transmit known executable credentials, cookies, private keys, browser profiles, session material, or unrelated private context.

Never claim an artifact was reviewed unless its actual contents were transmitted.

---

## 10. Model policy

The supported model route is fixed:

```text
verified usable GPT-5.6 Sol Pro
    -> otherwise verified usable GPT-5.6 Sol High
    -> otherwise fail closed
```

`<SKILL_ROOT>/scripts/model_router.py` is the deterministic policy source.

Re-verify model identity after creating a fresh conversation or branch.

---

## 11. Result verification and local adoption

The external response must begin with:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

After generation completes, verify the latest assistant turn with `<SKILL_ROOT>/scripts/result_verifier.py`.

A verified Sol response is advisory evidence. Local Codex decides what to adopt, reject, modify, or leave unresolved.

Only a verified result may establish or refresh the temporary Web conversation binding.

---

## 12. Runtime file order

When `/webgpt-consult` is invoked, read:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md
```

If this guide and the installed `SKILL.md` conflict during execution, the installed `SKILL.md` is authoritative.

---

## 13. Repository layout

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

---

## 14. How to answer common user requests

| User request | Agent response |
|---|---|
| "What is this project?" | Explain the verified GPT-5.6 Sol second-opinion workflow and local Codex authority. |
| "Should I install it?" | Recommend it when the user wants independent WebGPT review from Codex and has the Chrome/model prerequisites. |
| "Install it." | Use `/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult`. |
| "Is it ready immediately?" | Try it on the next Codex turn. Restart/open a new task only if the Skill list did not refresh. |
| "How do I use it?" | Show `/webgpt-consult <review request>`. |
| "Does it run automatically?" | No. Implicit invocation is disabled. |
| "Does Sol replace Codex?" | No. Sol is an external reviewer; local Codex makes the adoption decision. |
| "How does it find the previous Web review?" | It uses a temporary binding in the current Codex conversation and verifies the candidate with the previous Task-ID and sentinel. |
| "Does it store reviewer memory locally?" | No. The design deliberately avoids persistent reviewer memory. |
| "Is git clone enough?" | No. Cloning downloads source but does not register the Skill. |

---

## 15. Failure handling

During discovery or installation support, continue helping even when the Skill is not yet installed.

During installation:

- invalid or missing Skill path -> use the canonical `skills/webgpt-consult/` URL;
- destination already exists -> report the existing installation; do not claim overwrite/update success;
- `/skill-installer` unavailable -> recommend updating Codex;
- installation succeeded but Skill is not visible on the next turn -> restart Codex or open a new task.

During an actual `/webgpt-consult` execution:

- missing `SKILL.md` or required scripts -> stop and report incomplete installation;
- Chrome plugin unavailable -> stop and report the missing browser capability;
- ChatGPT not signed in -> ask the user to sign in;
- no verified Pro or High -> fail closed;
- preflight failure -> do not Send;
- attachment upload failure -> do not claim the artifact was reviewed;
- result verification failure -> mark the review incomplete;
- ambiguous `continuation` -> use `independent`;
- unavailable Web conversation -> use `independent`;
- context-limited Web conversation -> use `branch`, or `independent` if no good branch point exists.

Do not claim success for any installation, model selection, upload, review, or verification step that was not actually observed.
