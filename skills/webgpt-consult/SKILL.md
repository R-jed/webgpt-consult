---
name: webgpt-consult
description: Use Codex Chrome to consult ChatGPT Web with GPT-5.6 Sol Pro or High while preserving verified conversation continuity, browser ownership, and basic local secret safety. Codex decides the consultation prompt and evidence from the user's request.
---

# webgpt-consult

`webgpt-consult` is a thin bridge from Codex to ChatGPT Web. It provides reliable browser transport and continuity. It does not prescribe a review methodology, fixed prompt structure, evidence package, or project workflow.

## Product boundary

Codex remains responsible for understanding the user's request and deciding:

- what to ask ChatGPT Web;
- whether to include context, code, logs, screenshots, or files;
- how much evidence is necessary;
- whether the consultation should be independent, comparative, adversarial, exploratory, or something else;
- how to use the returned answer.

Do not add a fixed consultation framework when the current Codex model can perform the task directly from the user's prompt.

The Skill is responsible only for:

1. Chrome transport to ChatGPT Web;
2. GPT-5.6 Sol model selection;
3. temporary conversation binding and continuity;
4. browser-resource ownership and cleanup;
5. exact request/result association;
6. a small local safety guard for secrets, authentication material, and payment credentials.

## Hard boundaries

- Use the Codex Chrome capability only.
- Use verified GPT-5.6 Sol `Pro` when available; otherwise verified GPT-5.6 Sol `High`; otherwise stop.
- Codex UI model/reasoning labels are unrelated to Web model verification.
- Do not transmit API keys, passwords, access/refresh tokens, cookies, session material, private keys, OTP/recovery codes, card numbers, CVV/CVC, or payment PINs.
- Remove unrelated personal or private information before transmission. Keep task-relevant context only.
- Never claim a file or source was reviewed unless it was actually present in the Web prompt or uploaded successfully.
- Send a request once. Do not duplicate it while generation may still be active.
- Never guess a previous Web conversation from sidebar titles, history order, project name, timestamps, or semantic similarity.
- Automatically close only browser tabs/pages proven to have been created by this Skill in the current Codex conversation.
- Do not persist Web conversation bindings, reviewer history, project summaries, or decision memory.

## Execution

Read `references/chrome-workflow.md` before browser work.

For each consultation:

1. Decide whether the user's request clearly continues the currently bound Web conversation. Reuse it only when the binding can be verified. Otherwise use a fresh ChatGPT conversation.
2. If the bound Web conversation is context-heavy and continuation still matters, use `Branch in new chat` when useful; otherwise start fresh.
3. Generate a fresh random request ID such as `wgpt-<random>`.
4. Build the consultation prompt freely from the user's request. There is no required packet template or review format.
5. Include only the context and evidence Codex judges useful. For code tasks, selected source files or relevant excerpts may be uploaded directly when helpful. Do not upload a broad repository merely for convenience.
6. Before sending text that may contain secrets, run `scripts/safety_guard.py` on the exact text files or prompt material. If it blocks, remove or redact the sensitive value locally and scan again. Do not weaken or bypass the guard.
7. For binary or non-text attachments, inspect them locally before upload and avoid sending material that may expose secrets or unrelated private data.
8. Through Chrome, select and re-verify GPT-5.6 Sol `Pro`; fall back only to GPT-5.6 Sol `High`.
9. Put `Request-ID: <request-id>` in the prompt and instruct ChatGPT Web to begin its response with the same line.
10. Verify the composer and required attachment chips, then Send once.
11. After generation completes, inspect only the latest assistant turn. The first non-empty line must exactly equal `Request-ID: <request-id>` and the response must contain substantive content after it.
12. Only after that verification may the current Codex conversation establish or refresh its temporary Web binding.
13. Return the consultation result to the user's task and use it according to the user's request. The Skill itself does not impose an adoption or second-opinion workflow.

## Temporary conversation binding

Keep only this information in the current Codex conversation:

```text
review_tab_handle: <exact browser handle when available>
review_tab_owned_by_skill: true | false
review_conversation_url: <exact canonical ChatGPT conversation URL when available>
last_request_id: <verified request ID>
```

The handle and URL are locators. `last_request_id` is the identity check for the immediately relevant prior consultation.

A binding is valid for continuation only when the bound page can be opened and the prior assistant result can be verified against `last_request_id`.

If the binding is missing, stale, ambiguous, or unverifiable, start a fresh Web conversation. A new Codex conversation starts with no binding.

## Browser ownership

A browser tab/page is Skill-owned only when this Skill created it during the current Codex conversation and the exact handle still identifies that resource. Proven ownership survives later reuse of the same handle.

After a new result is verified:

```text
verify result
  -> establish new binding
  -> confirm new binding
  -> close the superseded old tab only if it is distinct and proven Skill-owned
```

Never close user-opened, pre-existing, unrelated, or ownership-unknown tabs. Never use process-wide Chrome termination, process scanning, a background cleanup daemon, or a persistent tab registry.

If generation or ownership is uncertain, leave the tab alone.

## Safety guard

`scripts/safety_guard.py` is intentionally narrow. It blocks high-confidence secrets, authentication material, and payment credentials in UTF-8 text. It is not a general DLP or PII-classification system.

Example:

```bash
python3 "<SKILL_ROOT>/scripts/safety_guard.py" prompt.txt src/example.py
```

Use `-` to scan stdin.

Personal information that is unrelated to the consultation should be removed or generalized by Codex before sending. Do not build persistent pseudonym maps or another privacy subsystem into this Skill.

## Failure handling

- Chrome unavailable or disconnected: stop and report the missing capability.
- ChatGPT not signed in: ask the user to sign in.
- GPT-5.6 Sol Pro and High cannot be verified: stop.
- Safety guard blocks the payload: redact/remove the sensitive value locally; do not send until clean.
- Required attachment upload fails: do not claim it was reviewed.
- Generation is active: do not resend, refresh, or close that tab.
- Request-ID verification fails: treat the consultation as incomplete and do not refresh the binding.
- Continuation binding cannot be verified: start fresh.
- Current Web conversation is too context-heavy: branch when useful, otherwise start fresh.
- Browser ownership is uncertain: leave the resource open.
