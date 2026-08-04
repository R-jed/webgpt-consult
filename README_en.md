<p align="center">
  <img src="logo.svg" alt="webgpt consult" width="128" />
</p>

<h1 align="center">webgpt consult</h1>

<p align="center">
  <strong>GPT-5.6 Sol Pro/High Second-Opinion Consultation</strong><br/>
  <em>Ask GPT-5.6 Sol when you're not sure</em>
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
  <a href="references/">References</a>
</p>

<br/>

<a id="about"></a>

## About

> **If you are an AI Agent, read [README_Agent.md](README_Agent.md) for bootstrap instructions.**

When your local agent hits a complex problem, call this tool to ask GPT-5.6 Sol. It packs your context, sends the request, gets the reply, and you decide what to adopt.

```
Your judgment
  → Pack context (8K-15K chars)
  → Safety scan (credential check)
  → Chrome plugin
  → Select GPT-5.6 Sol Pro/High
  → Send, wait, verify sentinel
  → You decide: adopt, reject, or modify
```

**Why it exists:**
- Complex decisions need outside perspective, but don't blindly trust external models
- Context packets preserve your judgment, evidence, and constraints
- Sentinel marks confirm complete replies, preventing half-baked results
- Safety scan prevents sensitive data leakage

<p align="right">(<a href="#about">back to top</a>)</p>

<a id="getting-started"></a>

## Getting Started

### Requirements

| Dependency | Purpose | Required |
|------------|---------|----------|
| Python 3.x | Safety scan, file bundling | Yes |
| Codex CLI | AI coding assistant | Yes |
| Chrome plugin | Consultation path | Yes |
| ChatGPT Plus/Pro | GPT-5.6 Sol access | Yes |

### Installation

```bash
git clone https://github.com/R-jed/webgpt-consult.git
cd webgpt-consult
```

### Setup

1. Install Codex CLI
2. Connect Chrome plugin
3. Sign in to ChatGPT Web in Chrome
4. Confirm GPT-5.6 Sol Pro or High is available in model picker

### Verify

```bash
# Safety scanner works
python3 scripts/check_packet_safety.py --help

# Bundle builder works
python3 scripts/build_attachment_bundle.py --help
```

Both pass and you're good. See [SKILL.md](SKILL.md) for issues.

<p align="right">(<a href="#getting-started">back to top</a>)</p>

<a id="usage"></a>

## Usage

| Scenario | Description |
|----------|-------------|
| Architecture review | System design, API design, database schema |
| Business consultation | Strategy, pricing, market analysis |
| Debugging | Complex bugs, performance issues, race conditions |
| Risk review | Security audit, technical debt |
| Planning | Project planning, sprint planning |
| Content strategy | Documentation, marketing, technical writing |

<p align="right">(<a href="#usage">back to top</a>)</p>

<a id="workflow"></a>

## Workflow

### 1. Write your judgment first

Before asking, think through:
- What's the problem, what's success
- What evidence and constraints you have
- What options exist, what each costs
- What you've tried, what's still unknown

### 2. Pack context

Use the [template](references/context-packet-template.md). For many files, bundle:

```bash
python3 scripts/build_attachment_bundle.py /path/to/artifacts -o /tmp/bundle.md
```

### 3. Safety scan

```bash
python3 scripts/check_packet_safety.py packet.md
```

Strip credentials, keep useful project context.

### 4. Send request

Follow the [Chrome workflow](references/chrome-workflow.md).

### 5. Verify and decide

- Confirm `WEBGPT_CONSULT_RESULT_...` sentinel appears
- Compare with your judgment
- Adopt, reject, or modify

<p align="right">(<a href="#workflow">back to top</a>)</p>

<a id="model-routing"></a>

## Model Routing

| Priority | Model | Description |
|----------|-------|-------------|
| 1 | GPT-5.6 Sol Pro | Preferred, strongest reasoning |
| 2 | GPT-5.6 Sol High | Fallback when Pro unavailable |
| - | Extra High/Medium/Instant | Unsupported, fail closed |

After selection, verify:
1. Selected tier appears in `menuitemradio`
2. `aria-checked=true` present
3. GPT-5.6 Sol family evidence in picker

<p align="right">(<a href="#model-routing">back to top</a>)</p>

<a id="repository-layout"></a>

## Repository Layout

```
webgpt-consult/
├── SKILL.md                    # Main docs
├── README.md                   # Chinese README
├── README_en.md                # This file
├── agents/
│   └── openai.yaml            # Agent config
├── references/
│   ├── chrome-workflow.md     # Chrome workflow
│   └── context-packet-template.md  # Packet template
├── scripts/
│   ├── check_packet_safety.py # Credential scan
│   ├── build_attachment_bundle.py  # File bundler
│   └── model_router.py        # Model selection
└── tests/
    └── test_*.py
```

<p align="right">(<a href="#repository-layout">back to top</a>)</p>

<a id="examples"></a>

## Examples

### Pro available

```
Available: Pro, High
Selected: Pro
downgraded: no
```

### Pro unavailable

```
Available: High
Selected: High
downgraded: yes
```

### No supported tier

```
Available: Extra High, Medium, Instant
Result: fail
```

<p align="right">(<a href="#examples">back to top</a>)</p>

<a id="license"></a>

## License

MIT - see [LICENSE](LICENSE).

<p align="right">(<a href="#license">back to top</a>)</p>
