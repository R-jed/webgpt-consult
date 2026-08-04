# WebGPT Consult — AI Agent Bootstrap

> ⚡ **For AI agents only.** If you are a human reader, go back to [README.md](README.md) (中文) or [README_en.md](README_en.md) (English).

This file contains bootstrap instructions, routing strategy, and behavior chain for AI agents. If you are an AI agent (Claude Code, Codex CLI, Cursor, etc.), **execute section 0 immediately** after finishing this file.

---

## 0. First Instruction for the AI (Execute Immediately After Reading This File)

> **After the AI finishes reading this file, it must automatically execute the following configuration process and then report what was changed. The user does not need to operate manually.**

### Automatic Configuration Process

```text
1. Detect the actual installation path of this package (derived from the location of this file, i.e., the directory containing README.md)
2. Detect the local environment:
   - Operating system type
   - Python version
   - Chrome plugin availability
3. Read SKILL.md → execute all instructions inside it
4. Execute user task
```

### Example Report Format

```markdown
✅ **WebGPT Consult Configured Successfully**

**Installation path**: /path/to/webgpt-consult
**System**: macOS / Linux / Windows
**Python version**: 3.x.x
**Chrome plugin**: available / unavailable
**Model**: GPT-5.6 Sol Pro / High
**Status**: ready, awaiting user task
```

---

## What Is This

This is not a regular Skill — it is a **structured second-opinion consultation system** built specifically for Codex. It solves two problems:

1. **Local agents need outside perspective**: complex decisions, architecture design, debugging challenges require a second opinion
2. **Preserve local judgment**: context packets retain local evidence, constraints, and judgment; the external model only provides advice

---

## Core Workflow

```
User task
  → Local Agent judgment (write it first)
  → Build context packet (8K-15K chars)
  → Safety scan (credentials check)
  → Chrome plugin
  → Select GPT-5.6 Sol Pro/High
  → Send, wait, extract with sentinel verification
  → Local adoption decision (adopt/reject/modify)
```

---

## File List

If you only read three files, read them in this order:

| Order | File | Purpose |
|-------|------|---------|
| 1 | [SKILL.md](SKILL.md) | Main skill documentation, complete workflow and rules |
| 2 | [references/context-packet-template.md](references/context-packet-template.md) | Context packet template |
| 3 | [references/chrome-workflow.md](references/chrome-workflow.md) | Chrome plugin workflow |

### Complete File Structure

```text
webgpt-consult/
├── SKILL.md                    # Main skill documentation (must read)
├── README.md                   # Chinese README (human readers)
├── README_en.md                # English README (human readers)
├── README_Agent.md             # This file (AI Agent)
├── agents/
│   └── openai.yaml            # Agent configuration
├── evals/
│   └── evals.json             # Evaluation prompts
├── references/
│   ├── chrome-workflow.md     # Chrome plugin workflow (must read)
│   └── context-packet-template.md  # Context packet template (must read)
├── scripts/
│   ├── check_packet_safety.py # Credential scanner
│   ├── build_attachment_bundle.py  # File bundler
│   └── model_router.py        # Model selection logic
└── tests/
    └── test_*.py              # Test suite
```

---

## Routing Strategy

### Model Selection Priority

| Priority | Model | Status | Description |
|----------|-------|--------|-------------|
| 1 | GPT-5.6 Sol Pro | Preferred | Strongest reasoning capability |
| 2 | GPT-5.6 Sol High | Fallback | Used when Pro is unavailable |
| - | Extra High/Medium/Instant | Unsupported | Fail closed |

### Verification

After selecting a tier, verify:
1. Tier name appears in checked `menuitemradio`
2. `aria-checked=true` attribute present
3. GPT-5.6 Sol family evidence in picker

---

## Safety Rules

### Credential Hygiene

**Do not send**:
- Tokens, cookies, passwords
- API keys, private keys
- OAuth headers, browser profiles
- Session dumps

**May send**:
- Normal user business and project context
- Code snippets, architecture design
- Error logs, debugging information

### Safety Scan

Must run before every consultation:

```bash
SKILL_DIR="<path-to-installed-webgpt-consult>"
python3 "$SKILL_DIR/scripts/check_packet_safety.py" packet.md
```

---

## Completion Conditions

A consultation is **complete only when all conditions are met**:

1. ✅ Verified supported GPT-5.6 Sol tier (Pro or High)
2. ✅ Prompt and all required attachments visible before sending
3. ✅ Assistant stopped generating
4. ✅ Complete assistant reply extracted
5. ✅ `WEBGPT_CONSULT_RESULT_...` sentinel appears in the reply

**If user says result is already visible**: re-extract the existing conversation, do not resubmit.

---

## Failure Handling

| Scenario | Handling |
|----------|----------|
| Chrome plugin unavailable | Stop and report missing connection |
| Not logged in | Ask user to sign in to ChatGPT Web in Chrome profile |
| No Pro or High | Stop and report GPT-5.6 Sol Pro or High not found |
| Post-selection verification failed | Stop and report which tier was selected but could not be confirmed |
| Attachment failed | Retry through Chrome's real file chooser, paste content, or use Markdown bundle |
| Still generating | Continue waiting in the same conversation |
| Missing sentinel after completion | Extract complete assistant reply again; otherwise mark incomplete |
| Low-quality answer | Use only supported parts; local Agent retains final judgment |

---

## Quick Start

### Requirements

- **Codex CLI** with Chrome plugin connected
- **Chrome profile** logged into ChatGPT Web
- **ChatGPT Plus/Pro** account with GPT-5.6 Sol Pro or High available
- **Python 3.x**

### Verify Setup

```bash
# Safety scanner works
python3 scripts/check_packet_safety.py --help

# Bundle builder works
python3 scripts/build_attachment_bundle.py --help
```

---

## Dependency Table

### Core Dependencies

| Component | Required | Purpose |
|-----------|----------|---------|
| Python 3.x | Yes | Safety scan, file bundling, reply extraction |
| Codex CLI | Yes | AI coding assistant |
| Chrome plugin | Yes | Consultation path |
| ChatGPT Plus/Pro | Yes | GPT-5.6 Sol access |

### Python Scripts

| Script | Purpose |
|--------|---------|
| `check_packet_safety.py` | Credential scan, prevent sensitive data leakage |
| `build_attachment_bundle.py` | Bundle multiple files into single Markdown |
| `model_router.py` | Model selection logic |

---

## FAQ

**Q1: Chrome plugin is unavailable, what should I do?**
A: Stop and report missing connection. This skill requires the Codex Chrome plugin.

**Q2: Why does it show downgrade after selecting Pro?**
A: This is expected behavior. When Pro is unavailable, the system automatically falls back to High and reports `downgraded=true` in metadata.

**Q3: How large should the context packet be?**
A: 8K-15K characters. Too short loses causal details; too long dilutes key information.

**Q4: What is the sentinel?**
A: A marker in `WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS` format used to verify consultation completion.

**Q5: Can I send code?**
A: Yes. Code is normal project context, not credentials. But do not send config files containing secrets.

---

## Behavior Chain Summary

The complete AI Agent behavior chain:

1. **Read this file** → understand overall structure
2. **Execute section 0** → auto-configure and report
3. **Read SKILL.md** → understand complete workflow
4. **Build context packet** → use template
5. **Run safety scan** → credentials check
6. **Execute consultation** → send via Chrome, wait, extract
7. **Verify sentinel** → confirm completion
8. **Local adoption decision** → adopt/reject/modify
9. **Return result** → formatted output

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Back

- [README.md](README.md) - Chinese README
- [README_en.md](README_en.md) - English README
