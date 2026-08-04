<h1 align="center">webgpt consult</h1>

<p align="center">
  <strong>让 Codex 把复杂问题交给 GPT-5.6 Sol Pro/High 做第二意见审查</strong><br/>
  保留项目上下文，也保留本地 Agent 的最终判断权
</p>

<p align="center">
  <a href="README_en.md">English</a> ·
  <a href="SKILL.md">Skill 规范</a> ·
  <a href="README_Agent.md">AI Agent 指引</a>
</p>

## 它解决什么

`webgpt-consult` 是一个 Codex Skill。Codex 遇到复杂架构、调试、产品、商业或风险问题时，可以通过 Chrome 将经过整理的证据交给 ChatGPT Web 的 GPT-5.6 Sol 做第二意见审查，再由本地 Codex 判断哪些意见值得采用。

当前只支持这一条执行路径：

```text
Codex local judgment
  -> project/workstream conversation routing
  -> context packet + exact attachments
  -> fail-closed preflight
  -> Codex Chrome plugin
  -> GPT-5.6 Sol Pro, then High
  -> exact result verification
  -> local adoption decision
```

它不会把外部模型的结果直接当成最终答案。

## 会话连续性

同一个项目不再每次都盲目新建 ChatGPT 对话，也不会把整个项目永久塞进同一个超长会话。

Skill 在本地维护一个项目级 conversation registry：

```text
~/.codex/webgpt-consult/conversations.json
```

每个项目可以有多个 workstream，例如：

```text
Subtap
  architecture-routing  -> ChatGPT conversation A
  tui-performance       -> ChatGPT conversation B
  release-risk          -> ChatGPT conversation C
```

直接跟进同一个决策、Bug、PR、分支、架构议题或实现计划时，Codex 会优先接回原会话。主题已经明显改变、需要独立第二意见、旧上下文可能造成锚定，或项目不同，则创建新会话。

关闭浏览器标签页不会丢失连续性，因为 registry 保存的是 ChatGPT conversation URL，而不是 tab 状态。

## 会话上下文满时

如果同一个 workstream 的 Web ChatGPT 会话已经出现 context/conversation length 压力，Skill 不会继续在原会话里反复重试，也不会从最新一条消息直接分支。

原因很简单：`Branch in new chat` 会继承所选消息之前的历史。从最新消息分支，长历史仍然会被完整带过去，基本没有完成真正的上下文压缩。

每个 workstream 第一次成功咨询时会同时建立两个锚点：`root_task_id` 永久表示整条咨询链的起点，`branch_base_task_id` 表示当前 ChatGPT 会话里实际可用于下一次分支的紧凑基线。正常情况下两者一开始相同。

后续需要 rollover 时：

```text
current long conversation
        ↓
locate active branch-base assistant result
        ↓
Branch in new chat from that older compact point
        ↓
CONTINUITY_CAPSULE_V1
  accepted decisions
  rejected paths
  standing constraints
  open questions
  evidence index
  current state
  current ask
        ↓
continue same workstream in bounded context
```

Codex 会先在本地根据项目证据和已验证的咨询结果整理累计 `CONTINUITY_CAPSULE_V1`。它是状态迁移包，不是简单聊天摘要，也不会让已经接近上限的 Web ChatGPT 自己负责总结自己。capsule 必须把从 active branch base 到当前为止仍有复用价值的决策、事实、约束、死路和未决问题带过去，并经过本地校验。

如果 `Branch in new chat` 成功，新分支仍然包含原 active branch base，因此 `branch_base_task_id` 保持不变。

如果当前 ChatGPT UI 无法可靠执行 Branch、原 branch-base 消息无法唯一定位、父会话已经打不开，或分支继承内容不正确，则退化为 `rollover_fresh`：创建一个全新 ChatGPT 会话，发送同一个可独立恢复上下文的 capsule，并重新上传当前仍然必要的证据。全新会话里不存在旧 branch base，所以第一次成功回复会成为新的 active `branch_base_task_id`，而最初的 `root_task_id` 永久保留。

registry 会保留当前 URL、最近的父会话 URL、root task、active branch base、rollover 次数、rollover mode 和 capsule hash，因此整个 workstream 的 lineage 仍然可追踪。

## 安全和真实性

发送之前必须运行统一 preflight：

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-20260804-220000 \
  --sentinel WEBGPT_CONSULT_RESULT_20260804_220000 \
  --attachment ./src/example.py
```

文本 packet 和文本附件都会扫描 credential-like 内容。发现 token、cookie、API key、private key、Authorization header 等内容时直接失败。

二进制附件默认标记为 `manual_review_required`。确认它确实是用户希望上传且已经做过本地检查后，才可以显式确认。这个确认不会覆盖已经检测到的凭证。

文件 bundle 现在对以下情况默认失败：

- 明确指定的输入文件不存在
- 没有任何可打包文本
- 支持的文本文件会被静默截断
- 总大小限制导致支持的文本文件被静默漏掉
- bundle 内检测到 credential-like 内容

## 模型路由

只支持：

```text
GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
GPT-5.6 Sol High
      ↓ unavailable
fail closed
```

`model_router.py` 是模型选择的 deterministic policy source。DOM ref 只用于点击，不作为模型身份依据。普通 `GPT-5 Pro` selector 不能证明它属于 GPT-5.6 Sol。

## 结果验证

外部模型回复必须以前两行开始：

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

之后使用：

```bash
python3 scripts/result_verifier.py /tmp/assistant-reply.txt \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --task-id webgpt-consult-...
```

sentinel 只是在正文中出现不算成功。

## 环境要求

- Python >= 3.10
- Codex
- Codex Chrome plugin 已安装并连接
- Chrome 中已登录 ChatGPT Web
- 账号实际提供 GPT-5.6 Sol Pro 或 High

Plugin 是否可安装还可能受方案、workspace policy、角色和 supported surface 影响。如果 Chrome plugin 本身不可用，本 Skill 会停止，不会改走其他浏览器 transport。

## 安装

如果你通过 Codex / ChatGPT 的 Skills 或 Plugin 机制使用本项目，请将整个 Skill 目录作为一个完整单元安装，确保 `SKILL.md`、`scripts/`、`references/` 和 `agents/` 一起存在。

如果你是在开发或审查源码：

```bash
git clone https://github.com/R-jed/webgpt-consult.git
cd webgpt-consult
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

仅 `git clone` 只是获取源码，不等于已经在你的 Codex 环境中完成 Skill 安装。

## 项目结构

```text
webgpt-consult/
├── SKILL.md
├── README.md
├── README_en.md
├── README_Agent.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── chrome-workflow.md
│   ├── continuity-capsule-template.md
│   └── context-packet-template.md
├── scripts/
│   ├── build_attachment_bundle.py
│   ├── check_packet_safety.py
│   ├── continuity_capsule.py
│   ├── conversation_registry.py
│   ├── model_router.py
│   ├── result_verifier.py
│   └── submission_preflight.py
├── tests/
│   └── test_*.py
└── VALIDATION.md
```

如果你是 AI Agent，请从 [README_Agent.md](README_Agent.md) 开始，然后以 [SKILL.md](SKILL.md) 为唯一执行规范。

## License

MIT
