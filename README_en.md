<p align="center">
  <img src="https://img.shields.io/badge/AI-Consultant-blueviolet?style=for-the-badge&logo=openai&logoColor=white" alt="AI Consultant" />
</p>

<h1 align="center">WebGPT Consult</h1>

<p align="center">
  <strong>GPT-5.6 Sol Pro/High Verified Second-Opinion Partner</strong><br/>
  <em>For difficult planning, architecture, debugging, business, product, content-strategy, risk-review, and Skill-design work</em>
</p>

<p align="center">
  <a href="https://github.com/R-jed/webgpt-consult/releases"><img src="https://img.shields.io/badge/release-v1.0.0-blue" alt="release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
</p>

<p align="center">
  <a href="README.md">中文</a> ·
  <a href="#about">About</a> ·
  <a href="#getting-started">Getting Started</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#workflow">Workflow</a> ·
  <a href="references/">References</a> ·
  <a href="#contributing">Contributing</a>
</p>

<br/>

<a id="about"></a>

## About

> **If you are an AI Agent, read [README_Agent.md](README_Agent.md) for bootstrap instructions.**

When your local AI agent (Claude Code, Codex CLI, Cursor, etc.) encounters a difficult problem that needs an outside perspective, WebGPT Consult routes it to the best available GPT-5.6 Sol tier, builds a structured context packet, executes the consultation, and brings back a verified result for local adoption.

```
Local Agent judgment
  → Build context packet (8K-15K chars)
  → Safety scan (credentials check)
  → Chrome plugin (default) or OpenCLI (fallback)
  → Select GPT-5.6 Sol Pro/High
  → Send, wait, extract with sentinel verification
  → Local adoption decision
```

**Why this exists:**
- Local agents need a second opinion on complex decisions but shouldn't blindly trust external models
- Context packets preserve local judgment, evidence, and constraints
- Sentinel-based completion verification prevents incomplete or corrupted results
- Credential hygiene protects sensitive data from leaking to external models

<p align="right">(<a href="#about">back to top</a>)</p>

<a id="getting-started"></a>

## Getting Started

### Prerequisites

- **Codex CLI** with Chrome plugin connected (default path)
- **Chrome profile** logged into ChatGPT Web
- **ChatGPT Plus/Pro** account with GPT-5.6 Sol Pro or High available
- **Python 3.x** (for safety scanner and bundle builder)

### Installation

```bash
git clone https://github.com/R-jed/webgpt-consult.git
```

Add to your Codex skills directory or reference directly.

### Verify setup

```bash
# Check Chrome plugin connection
opencli doctor

# Test safety scanner
python3 scripts/check_packet_safety.py --help
```

<p align="right">(<a href="#getting-started">back to top</a>)</p>

<a id="usage"></a>

## Usage

### Supported consultation types

| Type | Description |
|------|-------------|
| Architecture review | System design, API design, database schema, infrastructure |
| Business consultation | Strategy, pricing, market analysis, competitive positioning |
| Content strategy | Documentation, marketing, technical writing |
| Skill design | AI agent skills, workflow automation, tool integration |
| Risk review | Security audit, compliance, technical debt assessment |
| Debugging | Complex bugs, performance issues, race conditions |
| Planning | Project planning, sprint planning, resource allocation |

### Routing contract

| Condition | Path |
|-----------|------|
| Default | Codex Chrome plugin |
| Chrome unavailable + OpenCLI ready | OpenCLI fallback |
| Neither available | Stop and report missing connection |

<p align="right">(<a href="#usage">back to top</a>)</p>

<a id="workflow"></a>

## Workflow

### 1. Local judgment first

Before consulting, write your best local assessment:

- Decision or problem statement
- Success criteria and user intent
- Evidence and constraints
- Options and tradeoffs
- Attempts and unknowns

### 2. Build context packet

Use the [template](references/context-packet-template.md) to structure your consultation:

```bash
# For many files, build a bundle
python3 scripts/build_attachment_bundle.py /path/to/artifacts -o /tmp/bundle.md
```

### 3. Safety check

```bash
python3 scripts/check_packet_safety.py packet.md
```

Removes credential-like material while preserving useful project context.

### 4. Execute consultation

- **Chrome path**: Follow [Chrome workflow](references/chrome-workflow.md)
- **OpenCLI path**: Follow [OpenCLI fallback](references/opencli-fallback.md) (only when eligible)

### 5. Verify and adopt

- Confirm `WEBGPT_CONSULT_RESULT_...` sentinel appears
- Compare with local evidence
- Decide: adopt, reject, or modify

<p align="right">(<a href="#workflow">back to top</a>)</p>

<a id="model-routing"></a>

## Model Routing

### Selection hierarchy

| Priority | Model | Status |
|----------|-------|--------|
| 1 | GPT-5.6 Sol Pro | Preferred |
| 2 | GPT-5.6 Sol High | Fallback |
| - | Extra High/Medium/Instant | Unsupported (fail closed) |

### Verification

After selecting a tier, verify:
1. Tier name appears in checked `menuitemradio`
2. `aria-checked=true` attribute present
3. GPT-5.6 Sol family evidence in picker

<p align="right">(<a href="#model-routing">back to top</a>)</p>

<a id="repository-layout"></a>

## Repository Layout

```
webgpt-consult/
├── SKILL.md                    # Main skill documentation
├── README.md                   # This file
├── agents/
│   └── openai.yaml            # Agent configuration
├── evals/
│   └── evals.json             # Evaluation prompts
├── references/
│   ├── chrome-workflow.md     # Chrome plugin workflow
│   ├── opencli-fallback.md    # OpenCLI fallback guide
│   └── context-packet-template.md  # Packet template
├── scripts/
│   ├── run_webgpt_consult.py  # Main consultation runner
│   ├── check_packet_safety.py # Credential scanner
│   ├── build_attachment_bundle.py  # File bundler
│   ├── extract_chatgpt_reply.py    # Reply extractor
│   └── model_router.py        # Model selection logic
└── tests/
    └── test_*.py              # Test suite
```

<p align="right">(<a href="#repository-layout">back to top</a>)</p>

<a id="examples"></a>

## Examples

### Pro available (preferred)

```
Available: Pro, High
Selected: Pro
downgraded=false
```

### Pro unavailable (fallback)

```
Available: High
Selected: High
downgraded=true
```

### No supported tier

```
Available: Extra High, Medium, Instant
Result: fail closed
```

<p align="right">(<a href="#examples">back to top</a>)</p>

<a id="contributing"></a>

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<p align="right">(<a href="#contributing">back to top</a>)</p>

<a id="license"></a>

## License

MIT License - see [LICENSE](LICENSE) for details.

<p align="right">(<a href="#license">back to top</a>)</p>

<a id="acknowledgments"></a>

## Acknowledgments

Built on top of:
- [Codex CLI](https://github.com/openai/codex) - AI coding assistant
- ChatGPT Web - GPT-5.6 Sol Pro/High model access
- OpenCLI - Optional browser automation

<p align="right">(<a href="#acknowledgments">back to top</a>)</p>
