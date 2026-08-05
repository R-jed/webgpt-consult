# WebGPT Consult: AI Agent Bootstrap

> **For AI agents.** Human readers should use [README.md](README.md) or [README_en.md](README_en.md).

This file tells an AI Agent how to explain, install, verify, troubleshoot, and hand off into `webgpt-consult` without inventing behavior that the project does not support.

Reading this file does not authorize installation, environment changes, or a Web consultation.

The canonical installable Skill package is:

```text
skills/webgpt-consult/
```

`<SKILL_ROOT>` means the actual installed location resolved by the current Agent Skills/Codex environment.

---

## 0. Route the user's intent first

### Explain the project

Explain only. Do not install anything and do not start a Web review.

Minimum accurate description:

> `webgpt-consult` is a Codex Skill that obtains a verified GPT-5.6 Sol Pro or High second opinion through ChatGPT Web. Local Codex prepares the current evidence, verifies the external result, and remains responsible for the final decision.

### Install the project

Standard public install:

```bash
npx skills add R-jed/webgpt-consult
```

The `skills` CLI defaults to project scope when `-g` is omitted. If the user explicitly wants the Skill available across projects in Codex, use:

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

For the same global Codex install without prompts:

```bash
npx skills add R-jed/webgpt-consult -g -a codex -y
```

Codex-native alternative:

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

Do not invent `setup.sh`, a symlink installer, a second package format, or a legacy installer.

If you cannot actually execute or verify installation, provide the command and say that execution was not verified.

For an installation created through `npx skills`, use `npx skills list` to inspect installed Skills and `npx skills update webgpt-consult` to update it. Add `-g` to lifecycle commands when the installation is global.

### Use the project

The user-facing entry point is:

```text
/webgpt-consult <review request>
```

Ordinary discussion about the repository is not an invocation.

### Execute `/webgpt-consult`

Resolve `<SKILL_ROOT>` and read, in order:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md
```

`SKILL.md` is authoritative if any support document conflicts with it.

---

## 1. Product boundary

Local Codex owns:

- task understanding;
- initial judgment;
- evidence selection;
- credential and attachment preflight;
- model verification;
- result verification;
- adoption, rejection, or modification of the external advice.

WebGPT is an external reviewer. It is not a second project manager and does not maintain durable project memory.

The intended chain is:

```text
user task
  -> local Codex judgment
  -> choose independent / continuation / branch
  -> current truthful evidence
  -> preflight
  -> ChatGPT Web
  -> verified GPT-5.6 Sol Pro, otherwise High
  -> exact sentinel + Task-ID verification
  -> local adoption decision
```

---

## 2. Requirements and installation verification

Runtime requirements:

- Python 3.10+;
- current Codex;
- Codex Chrome plugin connected;
- Chrome signed into ChatGPT Web;
- GPT-5.6 Sol Pro or High actually available.

There is no OpenCLI fallback.

The repository uses the standard Agent Skills layout:

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

Do not hard-code one install path when the Skill was installed through `npx skills`. Resolve the actual `<SKILL_ROOT>` from the current environment.

After installation, ask the user to try `/webgpt-consult` on the next turn. Start a new Codex conversation or restart the client only if the current session has not refreshed its Skill list.

---

## 3. Review modes

Choose exactly one mode.

### `independent`

Use a fresh ChatGPT conversation for a new project, materially different question, architecture reset, deep review, milestone review, adversarial review, or any task that benefits from an unanchored second opinion.

Local Codex forms its own judgment first but normally keeps that conclusion private from Sol to reduce anchoring.

### `continuation`

Continue the same Web review only when:

- the new request clearly continues the immediately relevant review;
- the current Codex conversation still has a valid Web conversation binding;
- the previous review can be verified by its prior Task-ID and sentinel;
- the Web conversation remains useful and is not context-limited.

If any condition is unclear, use `independent`.

### `branch`

Use `Branch in new chat` when the same review should continue but the current Web conversation has accumulated too much context.

Choose an earlier still-relevant message. After branching, re-verify the GPT-5.6 Sol tier and resend the current task plus the minimum evidence needed now.

If no useful branch point exists, use `independent`.

---

## 4. Session-scoped Web conversation binding

Do not search ChatGPT history for a conversation that merely looks related.

After a Web review completes and exact result verification passes, retain only this temporary binding inside the current Codex conversation:

```text
review_tab_handle: <exact browser handle when available>
review_tab_owned_by_skill: true | false
review_conversation_url: <exact canonical chatgpt.com conversation URL when available>
last_task_id: <verified prior Task-ID>
last_sentinel: <verified prior sentinel>
```

The tab handle and URL are locators. The prior `Task-ID + sentinel` are the conversation identity check.

For `continuation`:

```text
bound tab handle
  -> exact retained conversation URL if handle is stale
  -> fresh DOM inspection
  -> match previous Task-ID + sentinel
  -> continuation allowed
```

Never identify a previous review from sidebar title, recent-chat order, browser history, project name, approximate time, or semantic similarity alone.

The binding is temporary and lives only in the current Codex conversation. Do not persist it to files, repository state, a database, or a long-lived cache.

Every new consultation invocation must generate a fresh Task-ID and sentinel with a fresh random nonce. `continuation` reuses the conversation binding, not the previous invocation identifiers.

---

## 5. Browser ownership and cleanup

Browser-resource ownership is part of correctness because Codex uses the user's real Chrome environment.

A tab/page is `skill-owned` only when this Skill created it during the current Codex conversation and its exact handle still identifies the same resource. Proven ownership persists when that same handle is reused by later `continuation` invocations.

A tab/page is `unowned` when:

- it existed before the Skill used it;
- the user supplied or opened it;
- it was merely discovered;
- ownership is uncertain.

Never infer ownership from a ChatGPT URL, title, conversation contents, or project name.

### Cleanup order

When a new review replaces the current binding:

```text
verify new Web result
  -> establish new binding
  -> confirm new binding
  -> inspect old tab ownership
  -> close old tab only if it is distinct and skill-owned
```

Never close the old bound tab before the new review is verified.

If old and new conversation URLs use the same tab handle, there is no old tab to close.

### Failed candidates

A temporary candidate tab may be closed only when:

- the Skill explicitly created it;
- it did not become the verified binding;
- its exact handle is still known;
- no request is still generating there.

If generation state or ownership is uncertain, leave the tab open.

### Never-touch boundary

Never automatically close:

- user-opened ChatGPT tabs;
- pre-existing Chrome tabs;
- tabs with uncertain ownership;
- unrelated Chrome windows or tabs.

Never use `pkill`, `killall`, broad Chrome termination, process scanning, a background cleanup daemon, or a persistent tab registry.

Cleanup is best-effort. A cleanup failure does not invalidate an otherwise verified consultation result.

---

## 6. No local reviewer memory

Do not maintain local review-history files, project summaries, accepted-decision caches, conversation registries, or stored WebGPT memory for future consultations.

Each invocation should be grounded in the user's current task and the evidence that currently matters.

For `continuation` and `branch`, carry only the current delta and evidence required for the next review. Do not create a hidden long-term project summary just to preserve WebGPT continuity.

---

## 7. Evidence, model, and result verification

Fail closed when:

- GPT-5.6 Sol identity cannot be verified;
- neither verified Pro nor verified High is usable;
- the selected tier is disabled;
- executable credentials are detected in transmitted text;
- required evidence was not actually transmitted;
- packet Task-ID/sentinel do not exactly match the preflight arguments;
- the latest result cannot be bound to the exact sentinel and Task-ID.

Never transmit known executable credentials, cookies, private keys, browser profiles, session material, or unrelated private context.

Model route:

```text
verified usable GPT-5.6 Sol Pro
  -> otherwise verified usable GPT-5.6 Sol High
  -> otherwise fail closed
```

The external response must begin with the fresh identifiers for this invocation:

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

Only after exact result verification may the current Codex conversation establish or refresh the Web conversation binding.

---

## 8. Failure handling

During an actual `/webgpt-consult` execution:

- unresolved `<SKILL_ROOT>` -> report the installation problem;
- Chrome plugin unavailable -> stop;
- ChatGPT not signed in -> ask the user to sign in;
- no verified Pro or High -> fail closed;
- selected tier disabled -> fail closed or use the valid fallback;
- preflight failure or identifier mismatch -> do not Send;
- attachment upload failure -> do not claim the artifact was reviewed;
- generation active -> do not duplicate Send or close that tab;
- result verification failure -> mark the review incomplete;
- ambiguous or unverifiable continuation -> use `independent`;
- context-limited conversation -> use `branch`, otherwise `independent`;
- unknown tab ownership -> leave it open;
- failed cleanup -> keep the verified review result and report cleanup only if it causes a meaningful user-visible issue.

Do not claim success for installation, model selection, upload, consultation, binding, or cleanup that was not actually observed.

---

## 9. Common user questions

| User request | Correct Agent response |
|---|---|
| "Install it." | `npx skills add R-jed/webgpt-consult` and note that the CLI defaults to project scope. |
| "Install globally for Codex." | `npx skills add R-jed/webgpt-consult -g -a codex` |
| "Install globally for Codex without prompts." | `npx skills add R-jed/webgpt-consult -g -a codex -y` |
| "Can I install from Codex?" | Use the documented `/skill-installer` path as an alternative. |
| "How do I update it?" | `npx skills update webgpt-consult`; add `-g` for a global install. |
| "How do I use it?" | `/webgpt-consult <review request>` |
| "Does Sol replace Codex?" | No. Sol is advisory; local Codex makes the final decision. |
| "How does it find the previous review?" | Current-session binding plus prior Task-ID and sentinel verification. |
| "What if the Web chat is too long?" | Use `branch` from an earlier useful point, or `independent` if no useful branch point exists. |
| "Does it store project memory locally?" | No. |
| "Will it close my Chrome tabs?" | It may close only superseded tabs that the Skill created in the current Codex conversation and can identify exactly. User/pre-existing/unknown tabs are left alone. |
| "Does it kill browser processes?" | No. Process-level browser cleanup is outside this Skill. |

---

## 10. Source of truth

Repository discovery files:

```text
README.md
README_en.md
README_Agent.md
```

Runtime source of truth:

```text
skills/webgpt-consult/SKILL.md
skills/webgpt-consult/references/chrome-workflow.md
skills/webgpt-consult/references/context-packet-template.md
```

If this file and `SKILL.md` conflict during execution, follow `SKILL.md`.
