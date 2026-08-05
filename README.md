<p align="center">
  <img src="./skills/webgpt-consult/assets/mobius.svg" alt="webgpt-consult" width="136" />
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

需要 Codex、已连接的 Codex Chrome plugin、已登录 ChatGPT Web，以及 Web 端可用的 GPT-5.6 Sol Pro 或 High。

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

Skill 没有固定咨询模板。代码问题可以上传相关文件，也可以只放关键代码片段。Codex 会根据当前问题决定需要多少上下文。

## 一个实际例子

假设你正在查一个登录 bug：

```text
/webgpt-consult 这个登录问题我已经查了很久，请让 GPT-5.6 Sol 帮我找根因。
```

Codex 会先看当前项目，挑出真正相关的源码和日志，比如 `auth.py`、`session.py` 和报错信息。发送前先在本地检查敏感内容，然后通过 Chrome 打开 ChatGPT Web，优先使用 GPT-5.6 Sol Pro，Pro 不可用时使用 High。

GPT-5.6 Sol 看完这些材料后给出分析，Codex 会确认这确实是本轮咨询的回复，再把结果带回当前任务。如果你接着问同一个问题，Skill 会尽量继续使用刚才那条 Web 会话；无法可靠确认时就新开一个会话。

## 隐私与安全

发送到 Web 之前，Skill 会在本地拦截常见的 API key、密码、访问令牌、cookie/session、private key、验证码和支付卡信息。发现这些内容时会先停止发送，处理后再继续。

与当前问题无关的姓名、邮箱、地址或其他私人信息也应该尽量删掉。这个检查只做基础保护，不会把项目变成一套复杂的隐私审计系统。

## 模型

Web 端只使用：

```text
GPT-5.6 Sol Pro
  ↓ 不可用
GPT-5.6 Sol High
  ↓ 不可用
停止
```

Codex 自己正在使用什么模型或 reasoning level，不影响 Web 端模型选择。

## 项目结构

```text
skills/webgpt-consult/
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── assets/
│   └── mobius.svg
├── references/
│   └── chrome-workflow.md
└── scripts/
    └── safety_guard.py
```

详细规则见 [SKILL.md](skills/webgpt-consult/SKILL.md)。

## License

[MIT](LICENSE)
