<p align="center">
  <img src="./skills/webgpt-consult/assets/mobius-white.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

<p align="center">
  <a href="#安装">安装</a> ·
  <a href="#使用">使用</a> ·
  <a href="#一个实际例子">示例</a> ·
  <a href="#隐私与安全">隐私与安全</a> ·
  <a href="README_en.md">English</a>
</p>

`webgpt-consult` 让 Codex 通过 Chrome 使用 ChatGPT Web 里的 GPT-5.6 Sol Pro 或 High。

你只需要告诉 Codex 想咨询什么。Codex 会自己整理问题，按需要带上相关源码、日志或文件，然后把 Web 端的结果带回当前任务。Skill 负责把这条链路跑稳，包括会话连续性、模型确认和基础敏感信息检查。

> **如果你是 AI Agent，请先看 [README_Agent.md](README_Agent.md)。实际执行规则以 [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md) 为准。**

## 安装

需要安装Codex、ChatGPT Chrome拓展插件和登录web端的ChatGPT的Pro 或 Plus订阅账号。

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

简单问题可以直接问。遇到架构、代码审查、复杂排错或需要很多背景的任务时，Codex 会使用内置的标准 `CONTEXT_PACKET_V1`，把任务、背景、用户意图、本地判断、证据、已经尝试过的方法、选项、风险和具体问题整理清楚，再发给 Web 端。代码问题可以上传相关文件，也可以只放关键代码片段。

## 一个实际例子

假设你正在查一个登录 bug：

```text
/webgpt-consult 这个登录问题我已经查了很久，请让 GPT-5.6 Sol 帮我找根因。
```

Codex 会先看当前项目，挑出真正相关的源码和日志，比如 `auth.py`、`session.py` 和报错信息。如果问题比较复杂，它会按标准 context packet 整理这些内容。发送前先在本地检查敏感内容，然后通过 Chrome 打开 ChatGPT Web，优先使用 GPT-5.6 Sol Pro，Pro 不可用时使用 High。

GPT-5.6 Sol 看完这些材料后给出分析，Codex 会确认这确实是本轮咨询的回复，再把结果带回当前任务。如果你继续追问同一个问题，Skill 会复用已经验证过的 Web 会话和模型，不会每一轮都重新打开模型菜单。只有新开会话、Branch、会话身份发生变化，或者页面明确显示模型状态变了，才会重新检查模型。

## 隐私与安全

发送到 Web 之前，Skill 会在本地拦截常见的 API key、密码、访问令牌、cookie/session、private key、验证码和支付卡信息。发现这些内容时会先停止发送，处理后再继续。

与当前问题无关的姓名、邮箱、地址或其他私人信息也应该尽量删掉。这个检查只做基础保护，不会把项目变成一套复杂的隐私审计系统。

## 模型

新建 Web 会话时使用：

```text
GPT-5.6 Sol Pro
  ↓ 不可用
GPT-5.6 Sol High
  ↓ 不可用
停止
```

同一个已经验证过的 ChatGPT Web 会话继续聊天时，会直接复用这个会话已经确认过的模型，不会重复检查菜单。Codex 自己正在使用什么模型或 reasoning level，不影响 Web 端模型选择。

## 项目结构

```text
skills/webgpt-consult/
├── SKILL.md
├── LICENSE
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

详细规则见 [SKILL.md](skills/webgpt-consult/SKILL.md)。

## License

[MIT](LICENSE)
