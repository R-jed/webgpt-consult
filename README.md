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

> **如果你是 AI Agent，请先阅读 [README_Agent.md](README_Agent.md)，真正执行时以 [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md) 为规范。**

`webgpt-consult` 让 Codex 通过 ChatGPT Web 调用 GPT-5.6 Sol Pro 或 High，获得一个经过验证的独立第二意见。

本地 Codex 负责理解任务、形成初始判断、筛选证据和最终决策。WebGPT 负责独立审查。外部结果验证完成后，Codex 再结合本地事实决定采纳、拒绝或修改。

```text
用户任务
  → 本地 Codex 先判断
  → 选择 independent / continuation / branch
  → 整理当前问题真正需要的证据
  → credential / attachment preflight
  → ChatGPT Web
  → GPT-5.6 Sol Pro，失败则 High
  → sentinel + task ID 验证
  → 本地 adoption decision
```

为什么需要这个项目：

- 复杂架构、调试、产品和风险决策通常值得一次独立强模型复核
- WebGPT 保持第二意见角色，不承担项目长期记忆
- 每次审查只发送当前问题需要的信息，降低历史结论累积造成的锚定和理解漂移
- 模型身份、凭证安全、附件完整性和结果绑定都有明确验证
- 浏览器资源有明确 ownership 和 cleanup 边界，避免长期积累无用的 Skill-created review tabs

<a id="快速开始"></a>

## 快速开始

### 前置条件

- Node.js / `npx`，用于安装和管理 Skill
- Python 3.10+
- 当前版本 Codex
- Codex Chrome plugin 已安装并连接
- Chrome 中已经登录 ChatGPT Web
- 当前账号实际提供 GPT-5.6 Sol Pro 或 High

### 推荐安装

标准安装入口：

```bash
npx skills add R-jed/webgpt-consult
```

仓库采用标准布局：

```text
skills/webgpt-consult/SKILL.md
```

`npx skills` 会自动发现 `webgpt-consult`。不加 `-g` 时，`skills` CLI 默认使用 project scope。

如果希望跨项目全局安装到 Codex：

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

无交互全局安装：

```bash
npx skills add R-jed/webgpt-consult -g -a codex -y
```

检查或更新已安装 Skill：

```bash
npx skills list
npx skills update webgpt-consult
```

如果是 global 安装，更新时可以加 `-g`。

安装成功后调用：

```text
/webgpt-consult <review request>
```

如果当前 Codex 会话没有刷新 Skill 列表，再新建 Codex 会话或重启客户端。

### Codex-native 备选安装

如果你希望直接从 Codex 内部安装，也可以使用内置 `/skill-installer`：

```text
/skill-installer install https://github.com/R-jed/webgpt-consult/tree/main/skills/webgpt-consult
```

README 的主推荐方式仍是 `npx skills`。

> `git clone` 只用于查看或开发源码，不会自动把 Skill 注册到 Codex。

### 第一次使用

本项目关闭隐式调用。安装后请显式使用 `/webgpt-consult`：

```text
/webgpt-consult 对这个项目做一次独立的 GPT-5.6 Sol 架构审查。
```

或者：

```text
/webgpt-consult 检查这个修复方案有没有遗漏的架构风险，并给出第二意见。
```

本 Skill 没有 OpenCLI fallback。Chrome plugin 不可用时会停止执行。

<a id="使用说明"></a>

## 使用说明

### 三种审查模式

| 模式 | 适用场景 | Web 行为 |
|---|---|---|
| `independent` | deep review、里程碑 review、对抗性审查、架构重审、不同项目或明显不同的问题 | 新建 conversation |
| `continuation` | 明确继续当前同一条审查，并且当前 Codex 会话仍能验证对应 Web conversation | 继续已绑定 conversation |
| `branch` | 同一条审查需要继续，但当前 conversation 上下文已经过长 | 从较早相关消息 `Branch in new chat` |

`independent` 下，本地 Codex 会先形成自己的判断，但默认不把结论告诉 Sol，从而降低锚定。

`continuation` 只用于当前 Codex 会话能够确定并验证的上一条 Web review。绑定丢失、身份验证失败或出现多个候选时直接切换到 `independent`。

`branch` 只解决上下文压力。成功分支并完成结果验证后，当前 Codex 会话的临时绑定会切换到新 branch。

### 会话绑定机制

Skill 不通过 ChatGPT 历史列表去猜“上一次咨询窗口”。第一次成功完成并验证 Web review 后，当前 Codex 会话只临时保留最小的 conversation binding：

```text
Chrome tab/page handle（如果可用）
+ tab 是否由 Skill 在当前 Codex 会话中明确创建
+ 精确 chatgpt.com conversation URL（如果可用）
+ 上一条已验证 Task-ID
+ 上一条已验证 sentinel
```

其中 tab handle 和 conversation URL 只是定位器，上一条 `Task-ID + sentinel` 才是会话身份校验。ownership 只用于决定这个 tab 将来是否允许自动关闭。

再次使用 `continuation` 时固定按下面的顺序执行：

```text
优先复用上次绑定的 Chrome tab/page handle
  ↓ handle 不可用
打开当前 Codex 会话中临时保留的精确 conversation URL
  ↓
fresh DOM 检查上一条相关 assistant result
  ↓
核对 previous Task-ID + previous sentinel
  ↓ 完全匹配
允许 continuation
```

任何一步无法确认，就使用 `independent` 新建 conversation。

Skill 不会根据 ChatGPT sidebar title、最近会话排序、项目名、浏览器历史、大致时间或语义相似度寻找上一条咨询窗口。

这个 binding 只活在当前 Codex conversation 中，不写入文件、仓库、数据库或长期缓存。新开一个 Codex conversation 时默认没有 Web binding，因此默认从 `independent` 开始。

每一次新的咨询调用都会生成新的 Task-ID 和 sentinel，并加入随机 nonce。`continuation` 复用的是 Web conversation，不复用上一轮的调用标识。

`branch` 必须从当前已验证的 binding 出发。新 branch 的结果验证通过后，binding 才从旧 conversation 切换到新 branch。

### Web 会话连续性

`webgpt-consult` 不在本地持久化 review history、conversation URL、项目摘要、accepted decisions 或 reviewer memory。

会话连续性只存在于当前 Codex 会话和当前 ChatGPT Web conversation 的临时绑定中：

- 同一审查的直接继续使用 `continuation`
- 不同项目默认使用 `independent`
- 同一项目但明显不同的问题默认使用 `independent`
- 当前会话上下文过长时使用 `branch`
- 当前 Codex 会话失去 Web binding、当前 Web 会话无法确认或不再可靠时使用 `independent`

`Branch in new chat` 会继承所选消息之前的历史。应选择一个较早、仍然包含必要共享背景的节点，再重新发送当前问题所需的最小证据。

如果没有合适的分支点，直接新建 conversation。

### 浏览器资源生命周期

Skill 会区分 `skill-owned` 和 `user-owned / unknown` browser tabs。

只有由 Skill 在当前 Codex 会话中明确创建、并且仍能通过精确 handle 确认的 tab 才允许自动关闭。这个 ownership 在后续 `continuation` 复用同一 handle 时继续有效。用户原本打开的 ChatGPT tab、普通 Chrome tab、ownership 不明确的 tab 永远不会被自动关闭。

当新的 review 已经验证成功并成为当前 binding 后，如果旧 binding 位于另一个明确由 Skill 创建的 tab，旧 tab 才会被关闭。失败流程产生的临时 tab 也只有在确认没有请求仍在生成时才会清理。

Skill 不使用 `pkill`、`killall`、浏览器进程扫描或后台 cleanup daemon。无法安全判断时直接保留 tab。

这个设计让 WebGPT 始终保持独立 reviewer，同时只在当前 Codex 会话内部维持稳定的短期 Web continuity，并避免 Skill-created review tabs 无限制积累。

<a id="安全与验证"></a>

## 安全与验证

以下边界采用 fail closed：

- GPT-5.6 Sol 模型身份无法验证
- Pro 和 High 都不可用或被禁用
- packet 或文本附件检测到 executable credential
- 必需证据没有真实上传
- packet 内的 Task-ID / sentinel 与 preflight 参数不完全一致
- 最终回复无法通过 sentinel 和 task ID 精确绑定

发送前运行统一 preflight。运行时以实际安装后的 `<SKILL_ROOT>` 为准：

```bash
python3 <SKILL_ROOT>/scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-... \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --attachment ./src/example.py
```

Preflight 会同时确认 packet 中指定的 `Task-ID` 和 `Sentinel` 各自精确出现一次。错配或重复都会 fail closed。

二进制附件需要本地检查后才能显式使用 `--confirm-unscanned-binary`。这个确认不会覆盖已经检测到的凭证。

模型路由固定为：

```text
verified enabled GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
verified enabled GPT-5.6 Sol High
      ↓ unavailable / disabled
fail closed
```

外部回复必须以前两行开始：

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

`result_verifier.py` 会验证最新 assistant turn。sentinel 只在正文里出现不算完成。

<a id="关键文件"></a>

## 关键文件

| 文件 | 用途 |
|---|---|
| [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md) | Skill 的唯一执行规范 |
| [README_Agent.md](README_Agent.md) | AI Agent 发现、安装和支持入口 |
| [skills/webgpt-consult/agents/openai.yaml](skills/webgpt-consult/agents/openai.yaml) | Skill 展示信息与 invocation policy |
| [skills/webgpt-consult/references/chrome-workflow.md](skills/webgpt-consult/references/chrome-workflow.md) | ChatGPT Web 浏览器执行、会话绑定、分支与 tab cleanup 流程 |
| [skills/webgpt-consult/references/context-packet-template.md](skills/webgpt-consult/references/context-packet-template.md) | Web 审查上下文模板 |
| [skills/webgpt-consult/scripts/model_router.py](skills/webgpt-consult/scripts/model_router.py) | Pro → High 模型身份与路由策略 |
| [skills/webgpt-consult/scripts/submission_preflight.py](skills/webgpt-consult/scripts/submission_preflight.py) | 发送前安全、附件和调用标识检查 |
| [skills/webgpt-consult/scripts/result_verifier.py](skills/webgpt-consult/scripts/result_verifier.py) | 外部结果精确绑定验证 |

### 仓库结构

```text
webgpt-consult/
├── README.md
├── README_en.md
├── README_Agent.md
├── LICENSE
├── assets/
│   └── logo.svg
└── skills/
    └── webgpt-consult/
        ├── SKILL.md
        ├── LICENSE
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
