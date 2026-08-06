# webgpt-consult: AI Agent bootstrap

This file is for AI agents that discover or support the project. Human users should read [README.md](README.md) or [README_en.md](README_en.md).

`webgpt-consult` is a Codex Skill for verified, multi-turn consultation with GPT-5.6 Sol Pro or High through ChatGPT Web in Chrome.

## Install

Project scope:

```bash
npx skills add R-jed/webgpt-consult
```

Global Codex install:

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

Update:

```bash
npx skills update webgpt-consult
```

Add `-g` for a global installation. Do not invent another installer, setup script, package format, or symlink workflow.

## Invoke

User-facing entry point:

```text
/webgpt-consult <consultation request>
```

Implicit invocation is disabled.

## Read order

Resolve the installed Skill root, then read:

```text
1. <SKILL_ROOT>/SKILL.md
2. <SKILL_ROOT>/references/chrome-workflow.md
3. <SKILL_ROOT>/references/context-packet-template.md   when the consultation is substantial
```

Do not reconstruct runtime behavior from this bootstrap file. The canonical responsibilities are:

| Source | Authority |
| --- | --- |
| `SKILL.md` | Product boundaries, routing, consultation policy, evidence discipline, completion semantics, failure policy |
| `references/chrome-workflow.md` | Browser state machine, conversation binding, live fast path, recovery, model cache, upload, dispatch state, result verification, ownership, cleanup |
| `references/context-packet-template.md` | Full `CONTEXT_PACKET_V1`, adaptation rules, follow-up delta form, packet integrity rules |
| `scripts/safety_guard.py` | Local blocking and warning behavior for outgoing UTF-8 text |
| `scripts/build_attachment_bundle.py` | Canonical multi-file UTF-8 text-bundle behavior |

## Critical boundaries

Keep these boundaries intact when explaining or modifying the project:

- Runtime transport is Codex Chrome only. There is no OpenCLI fallback in this project.
- New or branched Web conversations use verified GPT-5.6 Sol Pro when available, otherwise verified High, otherwise stop.
- Normal follow-ups in the same verified Web conversation reuse the confirmed model and conversation state. Do not reopen the model picker per message.
- Simple consultations may use a compact prompt. Substantial first-turn work uses `CONTEXT_PACKET_V1`. Same-conversation follow-ups should use the delta form when the earlier context remains valid.
- A local path or filename is not evidence. Deliver the real file, faithful content, or a generated bundle.
- Prefer original selected human-readable files. Use the bundle helper when many selected UTF-8 text files are awkward to upload individually or an archive is rejected.
- Never send blocked credentials, authentication material, or payment secrets.
- Submit once. An ambiguous Send outcome must recover the original conversation rather than create a duplicate.
- Conversation bindings, model caches, and in-flight recovery state are session-scoped. Do not persist reviewer or project memory to disk.
- Only close browser resources proven to have been created by this Skill in the current Codex conversation.
- ChatGPT Web is advisory. Codex owns local verification and final delivery.

## Consultation discipline

For difficult review, architecture, business, product, risk, or similar second-opinion work, preserve enough causal context for the Web model to challenge the real problem rather than a stripped-down summary.

When a useful local judgment already exists, keep it separate from facts and unknowns in the context packet. Omit it when the user wants an independent first view.

For genuinely difficult work, a packet around 8,000 to 15,000 characters can be appropriate when shortening it would remove important evidence, attempts, constraints, or tradeoffs. This is guidance, not a target.

Later turns in the same verified conversation should reuse valid prior context and send only the new state, evidence, and ask unless earlier material needs correction.

## Evidence helper

When many relevant UTF-8 text files are awkward to upload individually:

```bash
python3 "<SKILL_ROOT>/scripts/build_attachment_bundle.py" \
  /path/to/selected/source \
  -o /tmp/webgpt-consult-bundle.md
```

The helper is fail-closed by default when size limits would make the evidence incomplete. `--allow-partial` is an explicit opt-in and must never be presented as complete evidence.

Do not automatically bundle or upload an entire repository. Codex selects the evidence first.

## Validation assets

The installed package includes lightweight deterministic tests and manual Chrome eval scenarios:

```text
<SKILL_ROOT>/tests/
<SKILL_ROOT>/evals/evals.json
```

The tests cover safety behavior, bundle integrity, and runtime-contract invariants. The evals preserve real Chrome failure modes such as empty-composer recovery, ambiguous Send recovery, multi-turn model reuse, runtime reset recovery, and existing-result extraction.

These assets validate protocol behavior. They do not prescribe how Codex should reason about the user's task.

## Unsupported claims

Do not claim that the Skill:

- provides an OpenCLI fallback;
- stores durable reviewer or project memory;
- automatically packages or uploads an entire repository;
- requires the full context packet for every request;
- reopens the model picker on every follow-up;
- can recover a conversation by guessing from sidebar titles, recent-chat order, timestamps, project names, or semantic similarity;
- owns or closes user-created browser tabs;
- supports Web models outside GPT-5.6 Sol Pro or High.

## Attribution

The `CONTEXT_PACKET_V1` structure, Chrome consultation and recovery workflow, multi-file evidence approach, and related reliability scenarios were informed by `gpt56-sol-pro-consult` in `zjp1997720/zhijian-skills`.

See [skills/webgpt-consult/THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md).
