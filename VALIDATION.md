# Validation

## Deterministic policy validation

Baseline for the v1.1 closure:

```text
python -m unittest discover -s tests -p 'test_*.py' -v
python -m py_compile scripts/*.py
```

Local review run on 2026-08-04:

```text
13 tests passed
Python syntax compilation passed
```

Coverage added for:

- common credential blocking;
- corrected absolute-path matching;
- disabled/non-actionable Pro fallback to High;
- rejection of generic GPT-5 Pro as GPT-5.6 evidence;
- exact sentinel and task-ID binding;
- direct text-attachment credential blocking;
- binary manual-review gate;
- multiple project workstreams in the conversation registry;
- canonical git-root identity across project subdirectories;
- conversation rollover history when a workstream moves to a new ChatGPT URL;
- missing bundle input failure;
- Markdown fence collision handling.

The registry implementation also uses atomic writes and a cross-process lock to avoid lost updates when multiple Codex sessions write local conversation state concurrently.

GitHub Actions runs the deterministic suite on Python 3.10 and 3.12.

## Real browser validation

The repository tests cannot prove ChatGPT Web DOM compatibility. Before calling a release browser-validated, run a real Codex + Chrome pass and record:

```text
Codex version:
Chrome plugin version:
macOS version:
ChatGPT locale:
Pro selection and confirmation: pending
High fallback and confirmation: pending
Fresh conversation creation: pending
Same-workstream continuation: pending
Different-workstream isolation: pending
Text attachment preflight/upload: pending
Binary manual-review path: pending
Exact result verification: pending
Registry record/reopen after tab closure: pending
Concurrent registry update smoke test: pending
```

A Web UI change can require workflow adaptation even when all deterministic tests remain green.
