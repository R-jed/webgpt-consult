<h1 align="center">webgpt-consult-skill</h1>

<p align="center">
  <strong>让 Codex 用 WEB GPT-5.6 Sol Pro/High 拿个第二意见</strong><br/>
  
</p>

<p align="center">
  <a href="README_en.md">English</a> ·
  <a href="SKILL.md">Skill 规范</a> ·
  <a href="README_Agent.md">AI Agent 指引</a>
</p>

## 这东西干什么

`webgpt-consult` 是个 Codex Skill。本地 Codex 碰到架构、调试、产品、商业、风险或文件审查这类复杂问题时，把整理好的证据发给 ChatGPT Web 的 GPT-5.6 Sol 看看，拿个第二意见回来。最后本地 Codex 决定采不采纳。

流程很窄：

```text
本地判断
  → 独立或跟进审查
  → 真实上下文 + 证据
  → 发送前检查
  → GPT-5.6 Sol Pro，不行就 High
  → 结果验证
  → 本地决定采不采纳
  → 可选：更新本地状态
```

外部模型始终是 reviewer，本地 Codex 说了算。

## 独立审查和跟进审查

`independent` 用于完整 deep review、里程碑 review、对抗性审查、架构重审，或者明显不同的问题。会创建新的 ChatGPT 会话。Codex 会先在本地形成判断，但默认不告诉 Sol，减少锚定。

`follow-up` 只用于明确接着同一条咨询链继续的情况。用户说"继续上次咨询"，或者有唯一明确的 anchor（PR、issue、branch 等），可以复用旧会话。

有歧义就 fresh。重复少量上下文的代价比串错 consultation 小。

## 会话连续性

长期状态保存在本地，不依赖 ChatGPT conversation：

```text
~/.codex/webgpt-consult/state/<project-id>/<consult-id>.json
```

每个 snapshot 只保存本地 Codex 已采纳、还有复用价值的状态：用户目标、长期约束、已接受决策、已否决路径、未决问题、证据引用。

不是聊天记录，也不是 Sol 回复的备份。

查看当前项目的 consultation：

```bash
python3 scripts/consult_state.py --project-root . list
```

单个 state 文件损坏只会跳过并 warning，不会阻断整个 Skill。

项目 identity 包含当前 checkout 路径，所以同一仓库的两个 clone/worktree 不会静默共享状态。

## Web ChatGPT 上下文满了怎么办

Web ChatGPT 会话只是可复用的执行容器。

旧会话打不开、上下文过长、明显忘了关键决策，或者继续用会降低可靠性时：

```text
旧会话
   ↓ 别用了
新会话
   ↓
本地快照 + 当前增量 + 当前证据
   ↓
继续同一个本地 consult-id
```

不再依赖 `Branch in new chat`、历史 message ID、rollover counter 这些东西。

恢复能力来自本地 adopted state，浏览器改版或旧会话丢了不影响正确性。

## 安全和真实性

以下情况直接 fail closed：

- GPT-5.6 Sol 模型身份无法验证
- Pro 和 High 都不可用
- packet 或附件发现 executable credential
- 必需附件没有真实上传
- 结果 sentinel / task ID 无法精确绑定

发送前运行：

```bash
python3 scripts/submission_preflight.py packet.md \
  --task-id webgpt-consult-... \
  --sentinel WEBGPT_CONSULT_RESULT_... \
  --attachment ./src/example.py
```

二进制附件需要本地人工确认后才能通过 `--confirm-unscanned-binary`。这个确认不会覆盖已检测到的凭证。

## 模型路由

```text
GPT-5.6 Sol Pro 可用
      ↓ 不可用 / 禁用 / 模糊 / 无法操作
GPT-5.6 Sol High 可用
      ↓ 不可用
fail closed
```

`model_router.py` 是策略源。DOM ref 只用于点击，普通 GPT-5 Pro selector 不能证明它属于 GPT-5.6 Sol。

## 结果验证

外部回复必须以前两行开始：

```text
WEBGPT_CONSULT_RESULT_<unique-id>
Task-ID: <task-id>
```

然后由 `scripts/result_verifier.py` 做本地验证。sentinel 只在正文出现不算完成。

## 环境要求

- Python >= 3.10
- Codex
- Codex Chrome plugin 已安装并连接
- Chrome 中已登录 ChatGPT Web
- 账号实际暴露 GPT-5.6 Sol Pro 或 High

没有 OpenCLI fallback。

## 开发验证

```bash
git clone https://github.com/R-jed/webgpt-consult.git
cd webgpt-consult
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile scripts/*.py
```

`git clone` 只是获取源码，不等于在 Codex 环境中完成了 Skill 安装。

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

AI Agent 请从 [README_Agent.md](README_Agent.md) 开始，以 [SKILL.md](SKILL.md) 为执行规范。

## License

MIT
