---
name: webgpt-consult
description: Use Codex Chrome to consult ChatGPT Web with GPT-5.6 Sol Pro or High while preserving verified conversation continuity, browser ownership, safe send recovery, efficient model reuse, structured context handoff, and basic local secret safety.
---

# webgpt-consult

`webgpt-consult` is a bridge from Codex to ChatGPT Web. It provides reliable browser transport, context handoff, and conversation continuity without forcing every request into the same workflow.

## Product boundary

Codex remains responsible for understanding the user's request and deciding:

- what to ask ChatGPT Web;
- whether a short prompt or the standard context packet is more useful;
- whether to include context, code, logs, screenshots, or files;
- how much evidence is necessary;
- how to use the returned answer.

The Skill is responsible for:

1. Chrome transport to ChatGPT Web;
2. GPT-5.6 Sol model verification and efficient reuse inside the same verified Web conversation;
3. temporary conversation binding and continuity;
4. browser-resource ownership and cleanup;
5. exact submission/result association and duplicate-send prevention;
6. reliable attachment/composer handling;
7. the `CONTEXT_PACKET_V1` format for substantial consultations;
8. a small local safety guard for secrets, authentication material, payment credentials, and obvious privacy warnings.

## Hard boundaries

- Use the Codex Chrome capability only.
- For a new Web conversation, use verified GPT-5.6 Sol `Pro` when available; otherwise verified GPT-5.6 Sol `High`; otherwise stop.
- Once a Web conversation has a verified model binding, do not reopen the model picker on every follow-up. Reuse the cached verified tier while the same conversation identity remains valid.
- Re-verify the model when starting a fresh conversation or branch, when the conversation identity changes, when no valid model cache exists, or when fresh UI/error evidence contradicts the cached tier.
- A Chrome runtime reset alone does not invalidate the model cache when the same bound conversation is recovered and verified.
- Codex UI model/reasoning labels are unrelated to Web model verification.
- Reject legacy GPT-5.5 Pro, `Pro Extended`, base-Sol `Extra High`, and ambiguous model labels.
- Do not transmit API keys, passwords, access/refresh tokens, cookies, session material, private keys, OTP/recovery codes, card numbers, CVV/CVC, or payment PINs.
- Remove unrelated personal or private information before transmission. Keep task-relevant context only.
- Never claim a file or source was reviewed unless it was actually present in the Web prompt or uploaded successfully.
- Never click Send with an empty or unverified composer.
- Send a submission once. If the Send outcome becomes uncertain, recover the existing conversation instead of sending a replacement.
- Treat browser resets as invalidating old locators, element references, and pending browser promises.
- Never guess a previous Web conversation from sidebar titles, history order, project name, timestamps, or semantic similarity.
- Automatically close only browser tabs/pages proven to have been created by this Skill in the current Codex conversation.
- Do not persist Web conversation bindings, reviewer history, project summaries, or decision memory.

## Execution

Read `references/chrome-workflow.md` before browser work. Use `references/context-packet-template.md` for substantial consultations.

For each Web submission:

1. Decide whether the user's request clearly continues the currently bound Web conversation. Reuse it only when the binding can be verified. Otherwise use a fresh ChatGPT conversation.
2. If the expected answer may already be visible, inspect the existing conversation before preparing another submission.
3. If the bound Web conversation is context-heavy and continuation still matters, use `Branch in new chat` when useful; otherwise start fresh.
4. Generate a fresh `task_id` and sentinel such as `webgpt-consult-YYYYMMDD-HHMMSS-<nonce>` and `WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>`.
5. For a substantial consultation, use the standard `CONTEXT_PACKET_V1` format from `references/context-packet-template.md`. For a simple question, keep the prompt compact but still include the fresh sentinel and require ChatGPT Web to begin its response with it. In an established conversation, use the template's compact delta form instead of resending old context.
6. Include only the context and evidence Codex judges useful. For code tasks, selected source files or relevant excerpts may be uploaded directly when helpful. Do not upload a broad repository merely for convenience.
7. Run `scripts/safety_guard.py` on the exact outgoing prompt/packet text and every UTF-8 text attachment. Remove or redact blocking findings before continuing. Review non-blocking privacy warnings when relevant.
8. For binary or non-text attachments, inspect them locally before upload and avoid sending material that may expose secrets or unrelated private data.
9. Resolve the Web model efficiently:
   - fresh conversation or branch: open the picker, verify GPT-5.6 Sol `Pro`, otherwise `High`, and remember that verified tier for this conversation;
   - verified continuation in the same conversation: reuse the cached tier without reopening the picker;
   - if conversation identity or model state is uncertain or contradicted by fresh evidence: re-open the picker and verify again.
10. Upload files through the real file chooser. Keep any pending chooser lifecycle inside one browser-tool invocation, then reacquire the composer from fresh state.
11. Verify required attachment chips and the actual rendered composer text, including the current sentinel and enough distinctive packet/prompt text to prove the intended submission is present. If the composer is empty or unverified, do not Send.
12. Track dispatch state as `NOT_SENT`, `SENT`, or `UNKNOWN`. Send once. If the click outcome is ambiguous, recover the same conversation and never duplicate the submission.
13. While generation is active, stay in the same conversation and do not resend, refresh, close the tab, or send `continue`.
14. After generation completes, inspect only the latest assistant turn. Its first non-empty line must exactly equal the current sentinel, and the response must contain substantive content after it.
15. Only after verification may the current Codex conversation establish or refresh its temporary Web binding, including the verified model tier and latest task identity for that conversation.
16. Return the consultation result to the user's task and use it according to the user's request.

## Temporary conversation binding

Keep only this information in the current Codex conversation:

```text
review_tab_handle: <exact browser handle when available>
review_tab_owned_by_skill: true | false
review_conversation_url: <exact canonical ChatGPT conversation URL when available>
last_task_id: <verified task id>
last_sentinel: <verified result sentinel>
verified_web_model: GPT-5.6 Sol Pro | GPT-5.6 Sol High
model_verified_conversation_url: <canonical URL when available>
```

The handle and URL are locators. `last_sentinel` verifies the immediately relevant prior consultation. `verified_web_model` is a conversation-scoped cache that prevents unnecessary model-picker checks during normal multi-turn use.

A continuation binding is valid only when the bound page can be recovered and the immediately relevant prior assistant result can be verified against `last_sentinel`.

The cached Web model may be reused when the continuation resolves to the same verified conversation by exact handle or exact canonical URL and no fresh evidence contradicts the cached tier.

Invalidate the model cache when:

- a fresh conversation is created;
- `Branch in new chat` creates a new conversation;
- the canonical conversation identity changes;
- the binding is recovered without enough evidence to prove it is the same conversation;
- the current UI explicitly shows a different model/tier;
- ChatGPT reports a model availability or model-switch error;
- the user explicitly asks to re-check or change the Web tier.

Do not invalidate the model cache merely because the Chrome runtime, locator set, or browser-tool session restarted. Recover the same conversation, verify its identity, and keep the cached tier when those checks pass.

If the binding is missing, stale, ambiguous, or unverifiable, start a fresh Web conversation only when no unresolved `SENT` or `UNKNOWN` submission remains attached to it. A new Codex conversation starts with no binding or model cache.

The current submission's dispatch state is transient execution state only. Do not persist it after the consultation finishes.

## Context handoff

`references/context-packet-template.md` contains the canonical `CONTEXT_PACKET_V1` format used for substantial consultations. It preserves the structured metadata and sections that help GPT-5.6 Sol review complex work consistently.

Use the full packet when the task has substantial background, several constraints, source artifacts, prior attempts, options, risks, or a decision that benefits from explicit framing.

The packet keeps the proven `task_id`, `sentinel`, `task_type`, `context_strategy`, `credential_status`, `context_hash`, `required_output`, `TASK`, `BACKGROUND`, `USER_INTENT`, `LOCAL_JUDGMENT`, `EVIDENCE`, `ATTEMPTS_SO_FAR`, `OPTIONS`, `RISKS`, `ASK`, and `RETURN_FORMAT` structure. Adapt task-specific values to the user's actual request.

For second and later turns in the same verified Web conversation, avoid repeating the full packet unless earlier context is stale or ambiguous. Use a fresh `task_id` and sentinel with the compact delta form from the template. This preserves the packet protocol while reducing context-window and browser-token waste.

## Browser ownership

A browser tab/page is Skill-owned only when this Skill created it during the current Codex conversation and the exact handle still identifies that resource. Proven ownership survives later reuse of the same handle.

After a new result is verified:

```text
verify result
  -> establish new binding
  -> confirm new binding
  -> close the superseded old tab only if it is distinct and proven Skill-owned
```

Never close user-opened, pre-existing, unrelated, or ownership-unknown tabs. Never close a tab whose send state is uncertain. Never use process-wide Chrome termination, process scanning, a background cleanup daemon, or a persistent tab registry.

If generation or ownership is uncertain, leave the tab alone.

## Safety guard

`scripts/safety_guard.py` blocks high-confidence secrets, authentication material, and payment credentials in UTF-8 text. It may also warn about obvious personal/private identifiers without blocking the consultation.

Example:

```bash
python3 "<SKILL_ROOT>/scripts/safety_guard.py" packet.md src/example.py
```

Use `-` to scan stdin. Personal information unrelated to the consultation should be removed or generalized before sending.

## Failure handling

- Chrome unavailable or disconnected: stop and report the missing capability.
- ChatGPT not signed in: ask the user to sign in.
- A fresh conversation cannot verify GPT-5.6 Sol Pro or High: stop.
- Cached model state is contradicted or uncertain: re-verify the picker before sending.
- Browser runtime reset before Send: reacquire fresh state and rebuild only when Send definitely did not occur.
- Browser reset during/after Send with unknown outcome: recover the same conversation; never send a replacement while the outcome remains uncertain.
- Safety guard blocks the payload: redact/remove the sensitive value locally; do not send until clean.
- Required attachment upload fails: do not claim it was reviewed.
- Composer is empty or cannot be verified: do not Send.
- Generation is active: do not resend, refresh, close that tab, or send `continue`.
- Sentinel verification fails: treat the consultation as incomplete and do not refresh the binding.
- Continuation binding cannot be verified: start fresh only when there is no unresolved `SENT`/`UNKNOWN` submission attached to it.
- Current Web conversation is too context-heavy: branch when useful, otherwise start fresh.
- Browser ownership is uncertain: leave the resource open.
