<h1 align="center">webgpt consult</h1>

<p align="center">
  <strong>让 Codex 用 GPT-5.6 Sol Pro/High 获得一个可验证的第二意见</strong><br/>
  Web 会话可以丢，本地判断与项目状态不能丢
</p>

<p align="center">
  <a href="README_en.md">English</a> ·
  <a href="SKILL.md">Skill 规范</a> ·
  <a href="README_Agent.md">AI Agent 指引</a>
</p>

## 核心作用

`webgpt-consult` 是一个 Codex Skill。它让本地 Codex 在遇到复杂架构、调试、产品、商业、风险或文件审查问题时，把经过整理的真实证据交给 ChatGPT Web 的 GPT-5.6 Sol 做第二意见，再由本地 Codex 决定采纳、拒绝或修改。

核心流程保持很窄：

```text
local Codex judgment
  -> independent or follow-up review
  -> truthful context + evidence
  -> fail-closed preflight
  -> verified GPT-5.6 Sol Pro, then High
  -> exact result verification
  -> local adoption decision
  -> optional durable local state update
```

外部模型始终是 reviewer，本地 Codex 始终拥有最终判断权。

## 独立审查和跟进审查

`independent` 用于完整 deep review、里程碑 review、对抗性审查、架构重审或明显不同的问题。它会创建新的 ChatGPT 会话。Codex 仍然会先在本地形成判断，但默认不把这个结论告诉 Sol，减少锚定。

`follow-up` 只用于明确接着同一条咨询链继续工作。用户明确说“继续上次咨询”，或者存在唯一明确 anchor，例如某个 PR、issue、branch 或命名 artifact 时，可以复用旧 Web 会话。

匹配有歧义时直接 fresh。重复少量上下文的代价小于串错 consultation 的代价。

## 会话连续性

长期状态保存在本地，而不是依赖 ChatGPT conversation 记住一切：

```text
~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json
```

每个 consultation snapshot 只保存已经由本地 Codex 采纳、仍然有复用价值的状态，例如用户目标、长期约束、已接受决策、已否决路径、未决问题、证据引用和当前真实状态。

它不是聊天记录，也不是 Sol 回复的备份。

查看当前项目的 consultation：

```bash
python3 scripts/consult_state.py --project-root . list
```

单个 state 文件损坏只会被跳过并产生 warning，不会阻断整个 Skill。

项目 identity 包含当前 checkout 路径，因此同一远端仓库的两个 clone/worktree 默认不会静默共享咨询状态。

## Web ChatGPT 上下文满时

Web ChatGPT 会话只是可复用的执行容器。

如果旧会话打不开、上下文过长、明显忘记关键决策，或继续使用会降低可靠性：

```text
old Web chat
   ↓ stop using it
fresh Web chat
   ↓
durable local snapshot
+ current delta
+ current evidence
   ↓
continue same local consult-id
```

不再依赖 `Branch in new chat`、历史 message ID、rollover counter、root task、branch base 或 continuity capsule。

恢复能力来自本地 adopted state，因此浏览器 UI 改版或旧 ChatGPT 会话丢失不会破坏核心 correctness。

## 安全和真实性

以下边界继续 fail closed：

- GPT-5.6 Sol 模型身份无法验证
- Pro 和 High 都不可用
- packet 或文本附件发现 executable credential
- 必需附件没有真实上传
- 结果 sentinel / task ID 无法精确绑定

发送前运行：

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-... \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --attachment ./src/example.py
```

二进制附件需要本地人工确认后才能通过 `--confirm-unscanned-binary`。这个确认不会覆盖已经检测到的凭证。

## 模型路由

```text
verified usable GPT-5.6 Sol Pro
      ↓ unavailable / disabled / ambiguous / not actionable
verified usable GPT-5.6 Sol High
      ↓ unavailable
fail closed
```

`model_router.py` 是 deterministic policy source。DOM ref 只用于点击，普通 GPT-5 Pro selector 不能证明它属于 GPT-5.6 Sol。

## 结果验证

外部回复必须以前两行开始：

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

然后由 `scripts/result_verifier.py` 做本地验证。sentinel 只是在正文中出现不算完成。

## 环境要求

- Python >= 3.10
- Codex
- Codex Chrome plugin 已安装并连接
- Chrome 中已登录 ChatGPT Web
- 账号实际暴露 GPT-5.6 Sol Pro 或 High

当前没有 OpenCLI fallback。

## 开发验证

```bash
git clone https://github.com/R-jed/webgpt-consult.git
cd webgpt-consult
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile scripts/*.py
```

`git clone` 只是获取源码，不等于已经在 Codex 环境中完成 Skill 安装。

## 项目结构

```text
webgpt-consult/
├── SKILL.md
├── README.md
├── README_en.md
├── README_Agent.md
├── agents/openai.yaml
├── references/
│   ├── chrome-workflow.md
│   └── context-packet-template.md
├── scripts/
│   ├── build_attachment_bundle.py
│   ├── check_packet_safety.py
│   ├── consult_state.py
│   ├── model_router.py
│   ├── result_verifier.py
│   └── submission_preflight.py
├── tests/
└── VALIDATION.md
```

如果你是 AI Agent，请从 [README_Agent.md](README_Agent.md) 开始，并以 [SKILL.md](SKILL.md) 为唯一执行规范。

## License

MIT
