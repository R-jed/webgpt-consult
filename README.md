<p align="center">
  <img src="./skills/webgpt-consult/assets/mobius-white.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

<p align="center">
  <a href="#安装">安装</a> ·
  <a href="#使用">使用</a> ·
  <a href="#工作方式">工作方式</a> ·
  <a href="#隐私与安全">隐私与安全</a> ·
  <a href="README_en.md">English</a>
</p>

`webgpt-consult` 让 Codex 通过 Chrome 把问题、相关源码和文件交给 ChatGPT Web 的 GPT-5.6 Sol，再把结果带回当前任务。

你只需要告诉 Codex 想咨询什么。简单问题可以直接问；复杂任务会使用标准 `CONTEXT_PACKET_V1` 整理背景、证据、已经尝试过的方法、风险和具体问题。连续追问会尽量沿用同一个 Web 对话和已经确认过的模型，减少重复操作和上下文浪费。

> **如果你是 AI Agent，请先看 [README_Agent.md](README_Agent.md)。实际执行规则以 [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md) 为准。**

## 安装

需要 Codex、已连接的 Codex Chrome 插件，以及已经登录 ChatGPT Web 并能使用 GPT-5.6 Sol Pro 或 High 的账号。

项目内安装：

```bash
npx skills add R-jed/webgpt-consult
```

全局安装到 Codex：

```bash
npx skills add R-jed/webgpt-consult -g -a codex
```

更新：

```bash
npx skills update webgpt-consult
```

全局安装时加 `-g`。

## 使用

```text
/webgpt-consult <你的咨询请求>
```

例如：

```text
/webgpt-consult 请让 GPT-5.6 Sol 看一下这个登录 bug，需要的话读取相关源码和日志。
```

Codex 会自己判断需要哪些上下文。代码问题可以上传相关文件，也可以只发送关键代码片段。文件如果没有真正上传成功，Skill 不会把它当成已经被 Web 端读取。

## 工作方式

第一次进入一个新的 ChatGPT Web 对话时，Skill 会确认 GPT-5.6 Sol Pro；Pro 不可用时使用 High。完成确认后，同一个对话里的后续咨询会直接复用已经验证过的模型，只有新开对话、Branch、会话身份发生变化或页面明确显示模型状态异常时才重新检查。

复杂任务会使用标准 `CONTEXT_PACKET_V1`。同一个问题继续追问时，只发送新的进展、证据和问题，已有背景留在原来的 Web 对话里，不重复整包发送。

```text
你的请求
  ↓
Codex 选择真正相关的上下文和文件
  ↓
本地敏感信息检查
  ↓
复用已验证会话，或新建 ChatGPT Web 会话
  ↓
GPT-5.6 Sol Pro / High
  ↓
只发送一次并等待完整回答
  ↓
核对本轮结果后带回当前任务
```

例如你正在排查一个登录问题：

```text
/webgpt-consult 这个登录问题我已经查了很久，请让 GPT-5.6 Sol 帮我找根因。
```

Codex 可以选择 `auth.py`、`session.py` 和实际报错作为证据。第一次咨询会带上完整上下文；如果你接着说“我按它的建议改了，但这个测试还是失败”，下一轮只需要补充新代码、测试结果和新的问题。

浏览器在发送过程中如果出现断开或状态不确定，Skill 会优先恢复原来的会话，避免把同一个请求重复发两次。

## 隐私与安全

发送前会在本地拦截常见的 API key、密码、访问令牌、cookie/session、private key、验证码和支付卡信息。与当前问题无关的姓名、邮箱、地址等私人信息也应该尽量删掉。

这层检查只提供基础保护。真正需要发送什么，仍由 Codex 根据当前任务做最小化选择。

## 模型

新建 Web 会话时：

```text
GPT-5.6 Sol Pro
  ↓ 不可用
GPT-5.6 Sol High
  ↓ 不可用
停止
```

同一个已经验证过的 Web 对话会复用确认过的模型。Codex 自己正在使用什么模型或 reasoning level，不影响 Web 端模型选择。

## 项目结构

```text
skills/webgpt-consult/
├── SKILL.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── mobius-white.svg
├── references/
│   ├── chrome-workflow.md
│   └── context-packet-template.md
└── scripts/
    └── safety_guard.py
```

详细运行规则见 [SKILL.md](skills/webgpt-consult/SKILL.md)。

## License

项目使用 [MIT License](LICENSE)。`CONTEXT_PACKET_V1` 和部分 Chrome consultation workflow 设计吸收自 `zjp1997720/zhijian-skills` 的 `gpt56-sol-pro-consult`，许可信息见 [THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md)。
