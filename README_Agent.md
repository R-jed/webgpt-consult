# WebGPT Consult: AI Agent Bootstrap

> **For AI agents.** Human readers should use [README.md](README.md) or [README_en.md](README_en.md).

This file is the discovery, installation-support, and bootstrap guide for AI agents handling `webgpt-consult` on behalf of a user.

A user should be able to provide this repository URL and receive an accurate explanation, installation path, verification steps, invocation example, troubleshooting path, and runtime handoff.

Reading this file alone does not authorize installation, environment changes, or an external Web review.

The repository root is the project and discovery surface. The canonical installable Skill package is:

```text
skills/webgpt-consult/
```

`<SKILL_ROOT>` means the actual installed location of that Skill as resolved by the installer or Codex environment. Do not hard-code `~/.codex/skills/webgpt-consult/` when the Skill was installed through `npx skills`, because the CLI may use an agent-specific or shared Agent Skills location.

---

## 0. First instruction for the Agent

Classify the user's intent and follow exactly one path.

### A. The user is asking what this project is

Explain the project from this file. Do not install anything and do not start a Web review.

Minimum explanation:

> `webgpt-consult` is a Codex Skill that lets local Codex obtain a verified GPT-5.6 Sol Pro or High second opinion through ChatGPT Web. Codex prepares the current evidence, verifies the returned result, and remains responsible for the final decision.

Mention the Codex Chrome plugin dependency and explicit `/webgpt-consult` invocation when relevant.

### B. The user is asking to install the project

Use the open Agent Skills CLI as the primary public installation path:

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

For a non-interactive install:

```bash
npx skills add R-jed/webgpt-consult -g -a codex -y
```

The repository uses the standard `skills/<name>/SKILL.md` layout, so the CLI can discover `webgpt-consult` from the repository root.

Do not invent a project-specific installer, `setup.sh`, symlink script, or package format.

After installation, verify through the same lifecycle tool when possible:

```bash
npx skills list -g -a codex
```

Then tell the user to try `/webgpt-consult` on the next turn. Start a new Codex session or restart the client only if the current session has not refreshed its Skill list.

If the Agent cannot run terminal commands in the current environment, provide the exact command. Never claim installation succeeded when it was not actually executed or verified.

### C. The user wants the Codex-native installer

The supported Codex-native alternative is:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

This points directly to the canonical Skill package.

Treat `/skill-installer` as an alternative for users who specifically want installation from inside Codex. Do not present it as the primary public installation path while `npx skills` is available.

### D. The user is asking how to update the Skill

If the Skill was installed with `npx skills`, use its lifecycle command:

```bash
npx skills update webgpt-consult -g
```

Do not claim that re-running Codex `/skill-installer` upgrades an existing installation. The Codex installer may stop when the destination already exists.

### E. The user is asking how to use the project

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

### F. The user actually invokes `/webgpt-consult`

Enter the runtime workflow. Resolve the installed `<SKILL_ROOT>`, then read in this order:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md
```

Then execute the review contract defined there.

### G. The user is troubleshooting installation or invocation

Check the smallest relevant set of facts first:

1. Is Node.js / `npx` available if the user chose the recommended installer?
2. Does `npx skills list -g -a codex` show `webgpt-consult` when it was installed globally for Codex?
3. Can the actual installed `<SKILL_ROOT>` be resolved?
4. Does that Skill root contain `SKILL.md`, `LICENSE`, `agents/openai.yaml`, `references/`, and `scripts/`?
5. If just installed, has the user tried the next turn before assuming a restart is required?
6. Is the user invoking `/webgpt-consult` explicitly?
7. Is the Codex Chrome plugin installed and connected?
8. Is ChatGPT Web signed in, with GPT-5.6 Sol Pro or High actually exposed?

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
| Node.js / `npx` | Recommended Skill installation and lifecycle management |
| Python 3.10+ | Runtime helper scripts |
| Current Codex | Skill loading and current command/capability support |
| Codex Chrome plugin | Only supported browser transport |
| Chrome signed into ChatGPT Web | Required Web session |
| GPT-5.6 Sol Pro or High available to the account | Required external reviewer tier |

There is no OpenCLI fallback.

---

## 3. Installation contract

### Canonical source

The repository contains exactly one installable runtime source:

```text
skills/webgpt-consult/
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

Repository-level README files and `assets/` are discovery/documentation surfaces and are not runtime duplicates.

### Recommended public install

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

The `-g` flag is appropriate because `webgpt-consult` is designed as a reusable Codex capability across projects. The `-a codex` flag targets Codex explicitly.

The installer may manage the Skill through an agent-specific directory or a shared Agent Skills location depending on its current implementation. Therefore:

- use `npx skills list -g -a codex` for installation verification;
- resolve the actual `<SKILL_ROOT>` at runtime;
- do not make correctness depend on one hard-coded filesystem path.

### Update

```bash
npx skills update webgpt-consult -g
```

### Inspect before installing

```bash
npx skills add R-jed/webgpt-consult --list
```

### Codex-native alternative

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

This remains useful when the user explicitly wants to perform installation from inside Codex.

### Installation report

When useful, report:

```text
WebGPT Consult status

Repository: R-jed/webgpt-consult
Canonical package: skills/webgpt-consult/
Primary installer: npx skills
Target agent: codex
Scope: global
Installed: yes / no / not checked
Skill root: <verified path> / not resolved
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
/webgpt-consult Continue the current Web review using the new implementation evidence.
```

Preserve the user's actual task rather than replacing it with a generic review prompt.

---

## 5. Review modes

The Skill uses one mode field with three possible values.

### `independent`

Start a fresh ChatGPT Web conversation for deep reviews, milestone reviews, adversarial reviews, architecture resets, different projects, materially different questions, or any request that benefits from an unanchored second opinion.

Local Codex forms its own judgment first but normally keeps that conclusion private from Sol to reduce anchoring.

Share the local proposal only when the user explicitly wants Sol to attack, compare, or revise it.

### `continuation`

Continue the current Web conversation only when the new request clearly continues the same review and the current Codex session can resolve and verify the bound Web conversation.

Useful signals include an explicit request to continue, new evidence directly following the immediately preceding review, or the same artifact or decision being examined one step further.

If the relationship is ambiguous, the session binding is unavailable, the project changed, or the question changed materially, use `independent`.

### `branch`

Use `Branch in new chat` when the same review should continue but the bound Web conversation has accumulated enough history to create context pressure.

Choose an earlier still-relevant message as the branch point. The new branch inherits all conversation history before that message.

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

After a Web review succeeds and the returned result passes exact Task-ID and sentinel verification, the Agent retains the smallest browser identity currently available:

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

The handle and URL only locate the candidate page. The previous Task-ID and sentinel verify that it is the correct review conversation.

If the tab is gone, the URL is unavailable, the prior Task-ID/sentinel cannot be matched, or multiple candidate conversations exist, use `independent`.

Never choose a previous Web review based only on:

- ChatGPT sidebar title;
- recent-chat ordering;
- browser history;
- project name;
- approximate time;
- semantic similarity to the current task.

A successful `independent` review establishes the current binding. A successful `continuation` refreshes it. A successful `branch` replaces it with the new branch.

The binding lives only for the current Codex conversation. Starting a new Codex conversation means there is no prior Web binding, so the safe default is `independent`.

---

## 7. No local reviewer memory

Do not create or maintain local review-history files, conversation registries, project summaries, accepted-decision caches, stored ChatGPT conversation URLs, or review IDs for future reuse.

The Web model should receive what is needed for the current review. Historical conclusions should be reintroduced only when they remain factual inputs required by the current question.

An open Web tab and the current Codex session binding may provide temporary continuity. They are not project memory.

---

## 8. Context pressure and branching

Use `continuation` while the bound Web review remains compact and useful.

Move to `branch` when the same review should continue but the active conversation has accumulated too much history.

Branching procedure:

```text
resolve and verify the current binding
  -> identify an earlier useful branch point
  -> Branch in new chat
  -> confirm the new branch is active
  -> re-verify GPT-5.6 Sol Pro / High
  -> send the current task + minimum necessary evidence
  -> verify the result
  -> replace the binding with the new branch
```

If no suitable branch point exists, start fresh with `independent`.

Do not build a local summary system to compensate for a lost Web conversation. Rebuild the current review from the current task and evidence.

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

Text attachments are scanned before Send. Non-text attachments require explicit local review before the binary confirmation flag may be used. That confirmation cannot override a detected credential finding.

---

## 10. Model policy

The supported model route is fixed:

```text
verified usable GPT-5.6 Sol Pro
    -> otherwise verified usable GPT-5.6 Sol High
    -> otherwise fail closed
```

`scripts/model_router.py` is the deterministic policy source inside `<SKILL_ROOT>`.

A generic GPT-5 Pro label or a DOM locator does not prove GPT-5.6 Sol identity. The selected tier must be verified from fresh browser state.

Re-verify model identity after creating a fresh conversation or branch.

---

## 11. Result verification and local adoption

The external response must begin with:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

After generation completes, the latest assistant turn is extracted and verified with `<SKILL_ROOT>/scripts/result_verifier.py`.

A verified Sol response is advisory evidence. Local Codex compares it with local facts and its own prior judgment, then decides what to adopt, reject, modify, or leave unresolved.

For an independent review, preserve meaningful disagreement between Codex and Sol when it matters. Do not manufacture consensus.

Only a verified result may establish or refresh the temporary Web conversation binding.

---

## 12. Runtime file order

When `/webgpt-consult` is actually invoked, read:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md
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

If this guide and `SKILL.md` ever conflict during execution, the installed `<SKILL_ROOT>/SKILL.md` is authoritative.

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
| "Should I install it?" | Recommend it when the user regularly wants independent WebGPT review from Codex and has the Chrome/model prerequisites. |
| "Install it." | Prefer `npx skills add R-jed/webgpt-consult -g -a codex`. |
| "Can I install it from Codex?" | Yes. Use the explicit `/skill-installer` GitHub skill-path command as the Codex-native alternative. |
| "How do I update it?" | Use `npx skills update webgpt-consult -g` when installed through the `skills` CLI. |
| "How do I check installation?" | Use `npx skills list -g -a codex` and verify the installed Skill root when filesystem access is available. |
| "How do I use it?" | Show `/webgpt-consult <review request>`. |
| "Does it run automatically?" | No. Implicit invocation is disabled. |
| "Does Sol replace Codex?" | No. Sol is an external reviewer; local Codex makes the adoption decision. |
| "How does it find the previous Web review?" | It uses a temporary binding in the current Codex conversation, then verifies the candidate Web conversation with the previous Task-ID and sentinel. |
| "What if the Web chat is full?" | Use `branch` from an earlier useful point and resend the current minimum evidence. If no useful branch point exists, use `independent`. |
| "Does it store reviewer memory locally?" | No. The design deliberately avoids persistent reviewer memory. |
| "Can it use another browser or OpenCLI?" | The supported browser transport is the Codex Chrome plugin; there is no OpenCLI fallback. |
| "Is git clone enough?" | No. Cloning downloads source but does not register the Skill. |

---

## 15. Failure handling

During discovery or installation support, continue helping the user even when the Skill is not yet installed.

During an actual `/webgpt-consult` execution:

- unresolved or incomplete `<SKILL_ROOT>` -> stop and report the installation problem;
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
