<p align="center">
  <img src="./assets/logo.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<h3 align="center">GPT-5.6 Sol Pro / High second-opinion Skill for Codex</h3>

<p align="center">本地先判断 · Web 独立审查 · 结果验证 · 本地采纳</p>

<p align="center">
  <img src="https://img.shields.io/badge/Codex-Skill-111827" alt="Codex Skill" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB" alt="Python 3.10+" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2EA44F" alt="MIT License" /></a>
  <a href="https://github.com/R-jed/webgpt-consult/stargazers"><img src="https://img.shields.io/github/stars/R-jed/webgpt-consult?style=flat&logo=github" alt="GitHub stars" /></a>
</p>

<p align="center">
  <a href="#关于项目">关于项目</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#使用说明">使用说明</a> ·
  <a href="#安全与验证">安全与验证</a> ·
  <a href="#关键文件">关键文件</a> ·
  <a href="README_en.md">English</a>
</p>

<a id="关于项目"></a>

## 关于项目

> **如果你是 AI Agent，请先阅读 [README_Agent.md](README_Agent.md)，再以 [SKILL.md](SKILL.md) 为执行规范。**

`webgpt-consult` 让 Codex 在处理复杂问题时，通过 ChatGPT Web 调用 GPT-5.6 Sol Pro 或 High 获取一个经过验证的独立第二意见。

本地 Codex 负责理解任务、筛选证据和形成初始判断。WebGPT 负责独立审查。外部结果返回后，Codex 再结合本地事实决定采纳、拒绝或修改。

```text
用户任务
  → 本地 Codex 先判断
  → 选择 independent / follow-up
  → 整理当前问题真正需要的证据
  → credential / attachment preflight
  → ChatGPT Web
  → GPT-5.6 Sol Pro，失败则 High
  → sentinel + task ID 验证
  → 本地 adoption decision
```

为什么需要这个项目：

- 复杂架构、调试、产品和风险决策通常值得一次独立强模型复核
- WebGPT 保持第二意见角色，避免变成项目长期记忆或第二个项目管理器
- 发送内容按当前问题重新整理，减少历史结论持续累积造成的锚定和理解漂移
- 模型身份、凭证安全、附件完整性和结果绑定都需要明确验证

<a id="快速开始"></a>

## 快速开始

### 前置条件

- Python 3.10+
- 当前版本 Codex
- Codex Chrome plugin 已安装并连接
- Chrome 中已经登录 ChatGPT Web
- 当前账号实际提供 GPT-5.6 Sol Pro 或 High

### 推荐安装

当前 Codex 自带 `/skill-installer`。直接在 Codex 中运行：

```text
/skill-installer install https://github.com/R-jed/webgpt-consult
```

安装器会把完整 Skill 放入 Codex 的 Skill 目录。默认 `CODEX_HOME` 下，通常是：

```text
~/.codex/skills/webgpt-consult/
```

安装完成后重启 Codex，再新建一个任务，让新的 Skill 被重新加载。

如果当前 Codex 中没有 `/skill-installer`，优先升级 Codex。`webgpt-consult` 本身依赖 Codex Chrome plugin，因此不为旧版 Codex 维护另一套安装器。

> `git clone` 只用于查看或开发源码，不会自动把 Skill 注册到 Codex。

### 第一次使用

本项目关闭隐式调用。安装后请显式使用 `/webgpt-consult`：

```text
/webgpt-consult 对这个项目做一次独立的 GPT-5.6 Sol 架构审查。
```

也可以把具体目标直接接在 Skill 名后面：

```text
/webgpt-consult 检查这个修复方案有没有遗漏的架构风险，并给出第二意见。
```

本 Skill 没有 OpenCLI fallback。Chrome plugin 不可用时会停止执行。

<a id="使用说明"></a>

## 使用说明

### 审查模式

| 模式 | 适用场景 | Web 会话 |
|---|---|---|
| `independent` | deep review、里程碑 review、对抗性审查、架构重审、不同项目或明显不同的问题 | 新建 conversation |
| `follow-up` | 明确继续当前同一条咨询 | 复用当前 conversation |

`independent` 模式下，本地 Codex 会先形成自己的判断，但默认不把结论告诉 Sol，从而降低锚定。

`follow-up` 只在连续性非常明确、当前 Web conversation 仍然可用时复用。存在歧义时直接新建 conversation。

### Web 会话连续性

`webgpt-consult` 不在本地保存 consultation history、conversation URL、项目摘要或长期咨询状态。

会话连续性只存在于当前 ChatGPT Web conversation：

- 同一问题的明确 follow-up 可以继续当前会话
- 不同项目默认新建会话
- 同一项目但明显不同的独立问题默认新建会话
- 当前 Web 会话丢失、无法确认或不再可靠时直接 fresh

如果频繁咨询导致当前 Web conversation 出现明显上下文压力，优先使用 ChatGPT Web 的 `Branch in new chat`，从一个较早且仍然相关的消息节点创建分支，然后针对当前问题重新发送最小必要证据。

分支会继承所选节点之前的历史，因此不要机械地从已经接近上下文上限的最后一条消息分支。如果没有合适的分支点，直接新建 conversation。

这个设计让 WebGPT 保持独立 reviewer。Codex 每次只发送当前审查真正需要的信息，不依赖本地长期咨询记忆恢复 WebGPT 的项目认知。

<a id="安全与验证"></a>

## 安全与验证

以下边界采用 fail closed：

- GPT-5.6 Sol 模型身份无法验证
- Pro 和 High 都不可用
- packet 或文本附件检测到 executable credential
- 必需证据没有真实上传
- 最终回复无法通过 sentinel 和 task ID 精确绑定

发送前运行统一 preflight：

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-... \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --attachment ./src/example.py
```

二进制附件需要本地检查后才能显式使用 `--confirm-unscanned-binary`。这个确认不会覆盖已经检测到的凭证。

模型路由固定为：

```text
verified GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
verified GPT-5.6 Sol High
      ↓ unavailable
fail closed
```

外部回复必须以前两行开始：

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

`scripts/result_verifier.py` 会验证最新 assistant turn。sentinel 只在正文里出现不算完成。

<a id="关键文件"></a>

## 关键文件

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | Skill 的唯一执行规范 |
| [README_Agent.md](README_Agent.md) | AI Agent 发现、安装和支持入口 |
| [agents/openai.yaml](agents/openai.yaml) | Skill 展示信息与 invocation policy |
| [references/chrome-workflow.md](references/chrome-workflow.md) | ChatGPT Web 浏览器执行与分支流程 |
| [references/context-packet-template.md](references/context-packet-template.md) | Web 咨询上下文模板 |
| [scripts/model_router.py](scripts/model_router.py) | Pro → High 模型身份与路由策略 |
| [scripts/submission_preflight.py](scripts/submission_preflight.py) | 发送前安全和附件检查 |
| [scripts/result_verifier.py](scripts/result_verifier.py) | 外部结果精确绑定验证 |

### 仓库结构

```text
webgpt-consult/
├── README.md
├── README_en.md
├── README_Agent.md
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

## License

[MIT](./LICENSE)
