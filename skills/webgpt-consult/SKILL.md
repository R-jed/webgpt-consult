---
name: webgpt-consult
description: Use Codex Chrome to consult ChatGPT Web with GPT-5.6 Sol Pro or High while preserving verified multi-turn continuity, structured context handoff, real evidence, safe send recovery, efficient model reuse, and local secret safety.
---

# webgpt-consult

`webgpt-consult` is a verified ChatGPT Web consultation layer for Codex. It combines structured handoff for difficult work with reliable multi-turn Chrome transport.

Codex owns task understanding, evidence selection, local verification, and final delivery. ChatGPT Web is an external reasoning partner whose answer remains advisory until checked against the local evidence and the user's request.

## Runtime sources

Read `references/chrome-workflow.md` before browser work.

For substantial consultations, also read `references/context-packet-template.md`.

Use `scripts/build_attachment_bundle.py` only when several selected text files are genuinely needed and individual upload is impractical or an archive is rejected.

## Product boundary

Codex decides:

- what to ask ChatGPT Web;
- whether the request needs a compact prompt or `CONTEXT_PACKET_V1`;
- which facts, code, logs, screenshots, documents, or files materially affect the answer;
- whether an existing local judgment should be challenged or an independent first view is more useful;
- how to verify and use the returned advice.

The Skill owns:

1. Chrome transport to ChatGPT Web;
2. GPT-5.6 Sol model verification and conversation-scoped model reuse;
3. temporary Web conversation binding and continuity;
4. exact submission/result association and duplicate-send prevention;
5. real attachment/composer verification;
6. `CONTEXT_PACKET_V1` for substantial consultations;
7. safe multi-file text bundling when needed;
8. browser-resource ownership and cleanup;
9. local blocking of secrets, authentication material, and payment credentials.

## Hard boundaries

- Use the Codex Chrome capability only. This project does not include the upstream OpenCLI fallback.
- For a new Web conversation, use verified GPT-5.6 Sol `Pro`; otherwise verified GPT-5.6 Sol `High`; otherwise stop.
- Reuse the verified model tier on normal follow-ups in the same verified Web conversation. Do not reopen the model picker per message.
- Re-verify after a fresh conversation or branch, an identity change, a missing/invalid model cache, visible contradictory model state, a model error, or an explicit tier-change request.
- A Chrome runtime reset invalidates browser locators and pending promises. It does not by itself invalidate a model cache when the same conversation is recovered and verified.
- Codex model names and reasoning levels are not evidence of the Web model.
- Reject GPT-5.5 Pro, `Pro Extended`, base-Sol `Extra High`, ambiguous bare `Pro`, and unrelated model labels.
- Never send known API keys, passwords, access/refresh tokens, cookies, session material, private keys, OTP/recovery codes, card numbers, CVV/CVC, or payment PINs.
- Do not over-sanitize context that materially affects the judgment. Task-relevant user-owned project or business facts may be included after credential checks; unrelated private information should be removed or generalized.
- A local filename or path is never evidence by itself. Upload the actual file, paste the content, or provide a faithful excerpt/bundle.
- Never claim ChatGPT Web reviewed a file unless the actual file or faithful content was successfully delivered.
- Never Send an empty or unverified composer.
- Submit once. If Send outcome becomes uncertain, recover the original conversation rather than issuing a replacement.
- Never infer a prior conversation from sidebar titles, recent order, approximate timestamps, project names, or semantic similarity.
- Only automatically close browser resources proven to have been created by this Skill during the current Codex conversation.
- Do not persist conversation bindings, model caches, reviewer history, project summaries, or consultation memory to disk.

## Consultation flow

For each Web submission:

1. Resolve continuity first. Reuse the current verified Web conversation when the request clearly continues it. If the expected answer may already be visible, inspect that conversation before preparing anything new.
2. If the same consultation still matters but the Web thread is too context-heavy, use `Branch in new chat` from a useful point when available. A branch is a new conversation and gets a new model verification.
3. Generate a fresh `task_id` and sentinel, for example `webgpt-consult-YYYYMMDD-HHMMSS-<nonce>` and `WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS_<same-nonce>`.
4. Choose the handoff form:
   - simple question: compact prompt plus the fresh sentinel;
   - substantial first consultation: full `CONTEXT_PACKET_V1`;
   - same-conversation follow-up: compact delta packet unless prior context is stale or ambiguous.
5. For review, architecture, risk, product, business, or other second-opinion work, record the local judgment before consulting when one already exists. Keep it separate from facts and unknowns. Omit `LOCAL_JUDGMENT` when the user explicitly wants an independent first view.
6. Select the smallest evidence set that still preserves the truth. Prefer original human-readable files when reliable upload is practical. Use `scripts/build_attachment_bundle.py` when many selected UTF-8 text files would otherwise be awkward to deliver.
7. Run `scripts/safety_guard.py` on the exact outgoing prompt/packet and every UTF-8 text attachment. The bundle helper performs an additional blocking scan on its generated output. Remove or redact blocking findings before Send.
8. Inspect binary/non-text attachments locally before upload. Avoid unrelated private material and known secrets.
9. Follow `references/chrome-workflow.md` for model resolution, file chooser handling, composer verification, dispatch state, waiting, recovery, result verification, binding replacement, and cleanup.
10. After the verified Web result returns, compare it with local evidence. For review/decision work, explicitly decide what to adopt, reject, or modify when that helps the user's task. For other work, integrate the answer in the form the user requested.

## Context handoff

`references/context-packet-template.md` is the canonical substantial-consultation format. It retains the upstream `CONTEXT_PACKET_V1` structure:

```text
task_id
sentinel
task_type
context_strategy
credential_status
context_hash
required_output

TASK
BACKGROUND
USER_INTENT
LOCAL_JUDGMENT
EVIDENCE
ATTEMPTS_SO_FAR
OPTIONS
RISKS
ASK
RETURN_FORMAT
```

The structure is there to preserve causal detail and make facts, judgment, evidence, risks, and unknowns distinguishable. It is not permission to fill empty sections with boilerplate.

For genuinely difficult work, a detailed packet in roughly the 8,000 to 15,000 character range can be appropriate when shortening it would remove causal details. This is guidance, not a length target or gate. A smaller packet is better when it carries the complete truth.

For second and later turns in the same verified Web conversation, use the delta form with a fresh identity and only the changed evidence/current ask unless older context must be corrected or restated.

## Attachment bundle

Prefer original selected files first. Use a bundle when ChatGPT Web rejects an archive or when many relevant small text files make individual uploads unreliable.

```bash
python3 "<SKILL_ROOT>/scripts/build_attachment_bundle.py" \
  /path/to/selected/source \
  -o /tmp/webgpt-consult-bundle.md
```

The helper:

- skips common dependency/cache/build directories;
- accepts selected text extensions and strict UTF-8 only;
- records relative provenance labels, source byte counts, and SHA-256 hashes;
- fails closed when a selected text file exceeds the configured file/total limit;
- permits truncation/omission only with explicit `--allow-partial`, and marks partial evidence in the bundle;
- runs the local blocking safety scan before writing the bundle.

A partial bundle changes the evidence set. Use `--allow-partial` only when the omission is understood and acceptable for the user's question. If completeness matters, select fewer files, provide targeted excerpts, or upload originals separately.

## Temporary conversation binding

A verified Web conversation may retain only session-scoped state in the current Codex conversation:

```text
review_tab_handle: <exact browser handle when available>
review_tab_owned_by_skill: true | false
review_conversation_url: <exact canonical ChatGPT conversation URL when available>
last_task_id: <verified task id>
last_sentinel: <verified result sentinel>
verified_web_model: GPT-5.6 Sol Pro | GPT-5.6 Sol High
model_verified_conversation_url: <canonical URL when available>
```

`last_sentinel` verifies the immediately relevant completed consultation. `verified_web_model` belongs to the verified conversation identity, not to the browser runtime or individual request.

Invalidate the model cache when the conversation changes, cannot be proven to be the same, visibly shows another tier, reports a model error, or the user requests a tier change/check. Do not invalidate it merely because browser tooling restarted if the exact conversation can be recovered and verified.

## Transient submission record

While one submission is in progress, keep enough state in the current Codex conversation to recover safely:

```text
current_task_id
current_sentinel
current_context_strategy
current_attachment_names
current_dispatch_state: NOT_SENT | SENT | UNKNOWN
current_conversation_url
```

This is execution state, not durable history. Clear it after the submission is verified complete or deliberately marked failed/incomplete.

The purpose is recovery: after a reset, Codex should know which sentinel and attachments belong to the in-flight request and whether resending is safe. `SENT` and `UNKNOWN` must never create a replacement submission until the original outcome is resolved or the consultation is marked incomplete.

## Browser ownership

A tab/page is Skill-owned only when this Skill created it during the current Codex conversation and the exact handle remains known. Navigation does not change ownership.

After a result is verified, establish and confirm the replacement binding before considering cleanup. Close a superseded resource only when it is distinct and proven Skill-owned. Leave user-created or ownership-unknown resources alone.

Never use process-wide Chrome termination, process scanning, a cleanup daemon, or a persistent tab registry.

## Safety guard

Run:

```bash
python3 "<SKILL_ROOT>/scripts/safety_guard.py" packet.md src/example.py
```

on the exact outgoing prompt/packet and every UTF-8 text attachment. Blocking findings stop transmission. Privacy warnings are reviewed contextually; a warning does not automatically mean task-relevant business/project context must be removed.

## Completion and integration

A submission is complete only when the Chrome workflow verifies the intended conversation/model state, actual attachments and composer text, a single dispatch, stopped generation, the latest assistant turn, and the expected sentinel.

The Web result is advisory. Before final delivery, Codex should check claims that matter against the available local evidence. For a second-opinion review, an `Adopt / Reject / Modify` summary is useful when it makes the final decision clearer. It is not a mandatory output wrapper for every consultation.

## Failure handling

- Chrome unavailable/disconnected: stop and report the missing capability. Do not invent an OpenCLI route.
- ChatGPT not signed in: ask the user to sign in.
- Fresh conversation cannot verify Pro or High: stop.
- Cached model state is contradicted or uncertain: re-verify before Send.
- Safety guard blocks: remove/redact locally and scan again.
- Bundle helper fails completeness/safety checks: select fewer files, use faithful excerpts, or upload originals; do not hide missing evidence.
- Required attachment fails: do not claim it was reviewed.
- Composer is empty/unverified: do not Send.
- `NOT_SENT`: recovery may rebuild and submit after fresh verification.
- `SENT`: recover the original conversation and wait/extract; never resend.
- `UNKNOWN`: recover the original conversation and look for submission/generation evidence; never send a replacement while uncertain.
- Generation active: stay in the same conversation; do not resend, refresh, close it, or send `continue`.
- Sentinel verification fails after one complete re-read: mark incomplete and do not refresh the binding.
- Continuation identity cannot be verified: start fresh only when no unresolved `SENT`/`UNKNOWN` submission remains attached to the old conversation.
- Browser ownership uncertain: leave the resource open.
