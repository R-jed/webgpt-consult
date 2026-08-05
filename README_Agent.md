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

Do not invent `setup.sh`, a symlink installer, a second package format, or a legacy installer.

If you cannot actually execute or verify installation, provide the command and say that execution was not verified.

Use `npx skills list` to inspect installed Skills and `npx skills update webgpt-consult` to update this Skill. Add `-g` to lifecycle commands when the installation is global.

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

Local Codex owns task understanding, initial judgment, evidence selection, preflight, model verification, result verification, and the final adoption decision.

WebGPT is an external reviewer. It is not a second project manager and does not maintain durable project memory.

```text
user task
  -> local Codex judgment
  -> independent / continuation / branch
  -> current truthful evidence
  -> preflight
  -> ChatGPT Web
  -> verified GPT-5.6 Sol Pro, otherwise High
  -> exact sentinel + Task-ID verification
  -> local adoption decision
```

---

## 2. Runtime requirements

- Python 3.10+;
- current Codex;
- Codex Chrome plugin connected;
- Chrome signed into ChatGPT Web;
- GPT-5.6 Sol Pro or High actually available.

There is no OpenCLI fallback.

The installable package contains:

```text
skills/webgpt-consult/
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
    ├── model_router.py
    ├── result_verifier.py
    └── submission_preflight.py
```

Do not hard-code one install path when the Skill was installed through `npx skills`. Resolve the actual `<SKILL_ROOT>` from the current environment.

---

## 3. Review modes

### `independent`

Use a fresh ChatGPT conversation for a new project, materially different question, architecture reset, deep review, milestone review, adversarial review, or any task that benefits from an unanchored second opinion.

Local Codex forms its own judgment first but normally keeps that conclusion private from Sol.

### `continuation`

Continue the same Web review only when the new request clearly continues the immediately relevant review, the current Codex conversation still has a valid binding, the previous review can be verified by Task-ID + sentinel, and the Web conversation remains useful.

If any condition is unclear, use `independent`.

### `branch`

Use `Branch in new chat` when the same review should continue but the current Web conversation has accumulated too much context.

Choose an earlier still-relevant message, re-verify the GPT-5.6 Sol tier, and resend the current task plus the minimum evidence needed now. If no useful branch point exists, use `independent`.

---

## 4. Session-scoped Web conversation binding

Do not search ChatGPT history for a conversation that merely looks related.

After exact result verification passes, retain only this temporary binding inside the current Codex conversation:

```text
review_tab_handle: <exact browser handle when available>
review_tab_owned_by_skill: true | false
review_conversation_url: <exact canonical chatgpt.com conversation URL when available>
last_task_id: <verified prior Task-ID>
last_sentinel: <verified prior sentinel>
```

The handle and URL are locators. The prior `Task-ID + sentinel` are the conversation identity check.

For `continuation`:

```text
bound tab handle
  -> retained exact conversation URL if handle is stale
  -> fresh DOM inspection
  -> previous Task-ID + sentinel match
  -> continuation allowed
```

Never identify a previous review from sidebar title, recent-chat order, browser history, project name, approximate time, or semantic similarity alone.

The binding lives only in the current Codex conversation. Do not persist it.

Every new consultation invocation generates a fresh Task-ID and sentinel with a fresh random nonce. `continuation` reuses the Web conversation, not previous invocation identifiers.

---

## 5. Browser ownership and cleanup

A tab/page is `skill-owned` only when this Skill created it during the current Codex conversation and its exact handle still identifies the same resource. Proven ownership persists when the same handle is reused by later `continuation` invocations.

Everything else is `unowned`, including user-opened, pre-existing, merely discovered, or uncertain tabs.

When a new review replaces the binding:

```text
verify new result
  -> establish and confirm new binding
  -> close old tab only if it is distinct and skill-owned
```

A failed temporary candidate may be closed only when it is skill-owned, did not become the verified binding, its exact handle is known, and no request is still generating there.

Never close user/pre-existing/unknown tabs. Never use `pkill`, `killall`, broad Chrome termination, process scanning, a background cleanup daemon, or a persistent tab registry.

Cleanup is best-effort and never invalidates a verified review.

---

## 6. No local reviewer memory

Do not maintain local review-history files, project summaries, accepted-decision caches, conversation registries, or stored WebGPT memory for future consultations.

Each invocation should be grounded in the current task and current evidence. For `continuation` and `branch`, carry only the delta and evidence needed now.

---

## 7. Evidence, model, and result verification

Fail closed when:

- GPT-5.6 Sol identity cannot be verified;
- neither verified Pro nor verified High is usable and enabled;
- executable credentials are detected in transmitted text;
- required evidence was not actually transmitted;
- V7 Task-ID/sentinel format is invalid or the nonce pair does not match;
- packet Task-ID/sentinel do not exactly match the preflight arguments;
- the latest result cannot be bound to the exact sentinel and Task-ID;
- the returned review has no substantive body after its two binding headers.

Never transmit known executable credentials, cookies, private keys, browser profiles, session material, or unrelated private context.

Model route:

```text
verified enabled GPT-5.6 Sol Pro
  -> otherwise verified enabled GPT-5.6 Sol High
  -> otherwise fail closed
```

The external response must begin with the fresh identifiers for this invocation and contain review content afterward.

Only after exact result verification may the current Codex conversation establish or refresh the Web conversation binding.

---

## 8. Failure handling

During an actual `/webgpt-consult` execution:

- unresolved `<SKILL_ROOT>` -> report the installation problem;
- Chrome plugin unavailable -> stop;
- ChatGPT not signed in -> ask the user to sign in;
- no verified enabled Pro or High -> fail closed;
- preflight failure or identifier mismatch -> do not Send;
- attachment upload failure -> do not claim the artifact was reviewed;
- generation active -> do not duplicate Send or close that tab;
- result verification failure -> mark the review incomplete;
- ambiguous or unverifiable continuation -> use `independent`;
- context-limited conversation -> use `branch`, otherwise `independent`;
- unknown tab ownership -> leave it open.

Do not claim success for installation, model selection, upload, consultation, binding, or cleanup that was not actually observed.

---

## 9. Common user questions

| User request | Correct Agent response |
|---|---|
| "Install it." | `npx skills add R-jed/webgpt-consult` and note that the CLI defaults to project scope. |
| "Install globally for Codex." | `npx skills add R-jed/webgpt-consult -g -a codex` |
| "Install globally for Codex without prompts." | `npx skills add R-jed/webgpt-consult -g -a codex -y` |
| "How do I update it?" | `npx skills update webgpt-consult`; add `-g` for a global install. |
| "How do I use it?" | `/webgpt-consult <review request>` |
| "Does Sol replace Codex?" | No. Sol is advisory; local Codex makes the final decision. |
| "How does it find the previous review?" | Current-session binding plus prior Task-ID and sentinel verification. |
| "What if the Web chat is too long?" | Use `branch` from an earlier useful point, or `independent` if no useful branch point exists. |
| "Does it store project memory locally?" | No. |
| "Will it close my Chrome tabs?" | Only superseded tabs created by this Skill in the current Codex conversation and still identified exactly. |
| "Does it kill browser processes?" | No. |

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
skills/webgpt-consult/scripts/
```

If this file and `SKILL.md` conflict during execution, follow `SKILL.md`.
