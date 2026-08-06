---
name: webgpt-consult
description: Use Codex Chrome to consult ChatGPT Web with GPT-5.6 Sol Pro or High while preserving verified multi-turn continuity, structured context handoff, real evidence, safe send recovery, efficient model reuse, and local secret safety.
---

# webgpt-consult

`webgpt-consult` is a verified ChatGPT Web consultation layer for Codex. It combines structured handoff for difficult work with reliable multi-turn Chrome transport.

Codex owns task understanding, evidence selection, local verification, and final delivery. ChatGPT Web is an external reasoning partner whose answer remains advisory until checked against local evidence and the user's request.

## Runtime sources

Use these files as the runtime source-of-truth stack:

1. `SKILL.md` defines product boundaries, consultation policy, evidence discipline, and completion semantics.
2. `references/chrome-workflow.md` defines the canonical browser state machine, including continuity, model reuse, upload, dispatch recovery, result verification, ownership, and cleanup.
3. `references/context-packet-template.md` defines the canonical `CONTEXT_PACKET_V1` full and follow-up formats.

Read `references/chrome-workflow.md` before browser work. For substantial consultations, also read `references/context-packet-template.md`.

Use `scripts/build_attachment_bundle.py` only when several selected text files are genuinely needed and individual upload is impractical or an archive is rejected.

## Routing and requirements

Use the Codex Chrome capability only. This project does not include the upstream OpenCLI fallback.

The selected Chrome profile must be signed in to ChatGPT Web. A new or branched Web conversation must expose an eligible GPT-5.6 Sol tier before submission:

```text
GPT-5.6 Sol Pro
  -> otherwise GPT-5.6 Sol High
  -> otherwise stop
```

`Pro -> High` is intentional so the Skill can serve accounts where Pro is unavailable but High is available.

Normal follow-ups in the same verified Web conversation reuse the previously verified tier. Do not reopen the model picker per message. Re-verification is required only when the Chrome workflow determines the conversation/model binding is new, invalid, contradicted, or explicitly being changed.

## Hard gates

### Model truthfulness

Codex model names and reasoning levels are not evidence of the Web model.

For a fresh or branched conversation, verify the eligible GPT-5.6 Sol tier in the current ChatGPT Web UI. Reject GPT-5.5 Pro, `Pro Extended`, base-Sol `Extra High`, ambiguous bare `Pro`, and unrelated model labels.

A Chrome runtime reset invalidates browser locators, element references, and pending promises. It does not by itself invalidate a verified model tier if the Chrome workflow can recover and prove the same conversation identity.

### Artifact truthfulness

A local filename or path is never evidence by itself. Upload the actual file, paste the content, or provide a faithful excerpt or bundle.

Never claim ChatGPT Web reviewed a file unless the actual file or faithful content was successfully delivered. Never Send an empty or unverified composer.

Choose the smallest evidence set that still preserves the truth. Do not upload an entire repository merely because it is available.

### Credential hygiene

Never send known API keys, passwords, access or refresh tokens, cookies, session material, private keys, OTP or recovery codes, card numbers, CVV/CVC, or payment PINs.

Do not over-sanitize context that materially affects the judgment. Task-relevant user-owned project or business facts may remain after credential checks. Remove or generalize unrelated private information.

Run `scripts/safety_guard.py` on the exact outgoing prompt or packet and every UTF-8 text attachment before Send. Blocking findings must be removed or redacted locally and scanned again.

### Exactly-once submission

Submit once. If the Send outcome becomes uncertain, recover the original conversation rather than issuing a replacement.

The exact `NOT_SENT`, `SENT`, and `UNKNOWN` state machine lives in `references/chrome-workflow.md`. `SENT` and `UNKNOWN` must never create a replacement submission while the original outcome is unresolved.

### Session-scoped state and ownership

Conversation bindings, model caches, and in-flight recovery state exist only in the current Codex conversation. Do not persist reviewer history, project summaries, browser state, consultation memory, or model bindings to disk.

A browser resource is Skill-owned only when this Skill created the exact resource during the current Codex conversation and still knows its handle. Never infer ownership from URL, title, content, or history. Leave user-created and ownership-unknown resources alone.

## Workflow

For each consultation:

1. **Form the local view.** Understand the task, success condition, evidence, constraints, attempts, unknowns, and meaningful options before asking the Web model. For review or decision work, record an existing local judgment when one is useful to challenge. Omit it when the user wants an independent first view.
2. **Resolve continuity.** Reuse the current verified Web conversation when the request clearly continues it. If the expected answer may already be visible, inspect that conversation before preparing another submission.
3. **Choose the handoff form.** Use a compact prompt for simple work, full `CONTEXT_PACKET_V1` for substantial first-turn work, and the delta form for same-conversation follow-ups unless prior context is stale, ambiguous, or contradicted.
4. **Create a fresh identity.** Every Web submission gets a fresh `task_id` and sentinel. The canonical formats are defined in `references/context-packet-template.md`.
5. **Select real evidence.** Prefer original human-readable files when reliable upload is practical. Use faithful excerpts when only a small section matters. Use `scripts/build_attachment_bundle.py` when many selected UTF-8 text files would otherwise be awkward to deliver.
6. **Apply safety checks.** Scan the exact outgoing text and all UTF-8 text attachments. Inspect binary or non-text attachments locally before upload. Remove unrelated private material and blocked credentials.
7. **Execute the Chrome protocol.** Follow `references/chrome-workflow.md` for conversation binding, model resolution and reuse, file chooser handling, composer verification, in-flight state, Send recovery, waiting, result verification, and cleanup.
8. **Verify completion.** Accept only the latest completed assistant turn whose identity matches the current submission and whose substantive response is complete.
9. **Integrate locally.** Compare important Web claims with local source, evidence, and user constraints. For review or decision work, explicitly adopt, reject, or modify advice when that helps the final deliverable.

## Context assembly

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

The structure exists to preserve causal detail and keep facts, judgment, evidence, risks, and unknowns distinguishable. It is not permission to fill empty sections with boilerplate.

For genuinely difficult work, a detailed packet around 8,000 to 15,000 characters can be appropriate when shortening it would remove important constraints, evidence, attempts, or tradeoffs. This is guidance, not a quota or hard limit. A smaller packet is better when it still carries the complete truth.

Preserve verbatim errors, measurements, source details, and exact constraints when wording or structure matters. Separate assumptions from evidence.

For second and later turns in the same verified Web conversation, use the delta form with a fresh identity and only the changed state, evidence, and ask unless older context needs correction or restatement.

## Attachments

Use attachments when the answer depends on source files, local Skills, logs, screenshots, documents, spreadsheets, slides, PDFs, datasets, or rendered output.

Evidence preference:

1. original selected human-readable files when reliable upload is practical;
2. faithful excerpts when only a small section matters;
3. `scripts/build_attachment_bundle.py` when many selected UTF-8 text files are awkward to upload individually or an archive is rejected.

Bundle example:

```bash
python3 "<SKILL_ROOT>/scripts/build_attachment_bundle.py" \
  /path/to/selected/source \
  -o /tmp/webgpt-consult-bundle.md
```

The helper skips common dependency, cache, and build directories; accepts selected text extensions using strict UTF-8; records relative provenance labels, byte counts, and SHA-256 integrity metadata; fails closed when configured size limits would make evidence incomplete; allows truncation or omission only with explicit `--allow-partial`; and runs the local blocking safety scan before writing the bundle.

A partial bundle changes the evidence set. Use `--allow-partial` only when the omission is understood and acceptable for the user's question. Never describe partial evidence as complete.

## Conversation continuity

Treat one verified ChatGPT Web conversation as a temporary consultation session for the current Codex conversation.

Normal same-conversation follow-ups should use the Chrome workflow's live fast path: reuse the verified conversation and cached model without reopening the model picker or re-proving the previous result when the live binding remains unambiguous.

If browser tooling resets, a handle is lost, or the exact conversation must be reopened, use the Chrome workflow's recovery path. Recovery must prove the immediately relevant prior conversation identity before continuing. Never guess from sidebar titles, recent-chat order, approximate timestamps, project names, or semantic similarity.

If the same work should continue but the Web thread has become too context-heavy, use `Branch in new chat` from a useful earlier point when available. A branch is a new conversation identity and requires fresh model verification.

The exact binding fields, cache invalidation rules, in-flight submission record, and cleanup order belong exclusively to `references/chrome-workflow.md`.

## Completion contract

A consultation is complete only when all relevant conditions are satisfied:

- the intended conversation identity is valid;
- the Web model is freshly verified or validly reused from that conversation's cache;
- every required attachment is visibly delivered;
- the rendered composer contains the intended request identity and substantive prompt or packet text before Send;
- blocking safety checks have passed;
- the submission is sent once;
- generation has stopped;
- the complete latest assistant turn is extracted;
- the expected sentinel verifies the current result.

If any required condition cannot be established, mark the consultation incomplete rather than inventing success or risking a duplicate submission.

## Local integration

The Web answer is advisory. Codex remains responsible for important factual verification and final delivery.

For a strict review or decision consultation, an explicit `Adopt / Reject / Modify` integration is useful when it clarifies what changed after external challenge. Do not force that wrapper onto ordinary debugging, exploratory work, or follow-up questions when the user requested another form of output.

## Failure handling

- **Chrome unavailable or disconnected:** stop and report the missing capability. Do not invent an OpenCLI route.
- **ChatGPT not signed in:** ask the user to sign in to ChatGPT Web in the selected profile.
- **Fresh or branched conversation cannot verify Pro or High:** stop.
- **Cached model state is contradicted or conversation identity becomes uncertain:** follow the Chrome recovery and re-verification rules before Send.
- **Safety guard blocks:** remove or redact the blocked material locally and scan again.
- **Bundle completeness or safety check fails:** select fewer files, use faithful excerpts, or upload originals. Do not hide missing evidence.
- **Required attachment fails:** stop or adapt the evidence set explicitly. Do not claim it was reviewed.
- **Composer is empty or unverified:** do not Send. Use only the recovery action allowed by the Chrome workflow.
- **Send outcome is `NOT_SENT`:** recovery may rebuild and submit after fresh verification.
- **Send outcome is `SENT`:** recover the original conversation and wait or extract. Never resend.
- **Send outcome is `UNKNOWN`:** recover the original conversation and look for submission, generation, or result evidence. Never send a replacement while uncertainty remains.
- **Generation is active:** stay in the same conversation. Do not resend, refresh, close it, or send `continue`.
- **Sentinel verification fails after the permitted complete re-read:** mark the consultation incomplete and do not refresh the binding.
- **Continuation identity cannot be verified:** start fresh only when no unresolved `SENT` or `UNKNOWN` submission remains attached to the old conversation.
- **Browser ownership is uncertain:** leave the resource open.
