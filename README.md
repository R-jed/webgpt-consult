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

`webgpt-consult` 让 Codex 通过 Chrome 把问题和真正相关的资料交给 ChatGPT Web 的 GPT-5.6 Sol，再把结果带回当前任务。

简单问题可以直接问。复杂的架构、代码、排错、产品或风险问题会使用标准 `CONTEXT_PACKET_V1`，把背景、证据、已经尝试过的方法、当前判断、选项和风险整理清楚。连续追问会尽量沿用同一个 Web 对话和已经确认过的模型，避免一遍遍重传背景、检查模型菜单或重复提交。

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

Codex 会自己判断哪些材料真正有用。ChatGPT Web 不能直接读取你电脑上的路径，所以源码、日志或文档只有真正上传、粘贴或整理成附件后，才会被当成已经提供给 Web 端的证据。

如果需要的文本文件很多，Skill 自带一个 bundle 工具，可以把选中的文件整理成一份带文件名和 SHA-256 清单的 Markdown 附件。它支持能够明确识别的 Unicode 文本：UTF-8，以及带 BOM 的 UTF-16/UTF-32。无法可靠解码时会直接停止，不会猜编码或用替换字符悄悄修改内容。超大文件默认也不会被静默截断；资料不完整时会停下来，除非明确允许生成 partial bundle。

## 工作方式

第一次进入一个新的 ChatGPT Web 对话时，Skill 会确认 GPT-5.6 Sol Pro；Pro 不可用时使用 High。确认以后，同一个 Web 对话里的正常后续咨询直接复用这个模型。

只要原来的 tab 和对话身份一直没有变化，后续轮次会走 fast path，直接继续聊天。发生 Chrome 重连、tab 丢失或需要重新打开对话时，Skill 才会用上一轮的 Sentinel 重新确认找回的是同一个会话。

复杂任务会使用 `CONTEXT_PACKET_V1`。如果这是一次架构、风险、产品或其他“第二意见”式审查，Codex 会在已有本地判断时把它和事实分开写清楚，让 GPT-5.6 Sol 真正去挑战这个判断。Web 端的回答始终是咨询意见，Codex 还会结合本地源码和事实决定哪些建议采用、修改或放弃。

同一个问题继续追问时，只发送新的进展、证据和问题，已经存在于 Web 对话里的背景不会整包重复发送。

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
核对 Web 意见和本地证据
  ↓
带回当前任务
```

例如你正在排查一个登录问题：

```text
/webgpt-consult 这个登录问题我已经查了很久，请让 GPT-5.6 Sol 帮我找根因。
```

Codex 可以选择 `auth.py`、`session.py` 和实际报错作为证据。如果相关源码很多，可以上传选中的原文件，或生成一个 review bundle。你随后说“我按它的建议改了，但这个测试还是失败”，下一轮只需要补充新代码、测试结果和新的问题。

浏览器如果恰好在点击 Send 时断开，Skill 会把状态区分成 `NOT_SENT`、`SENT` 或 `UNKNOWN`。结果不确定时优先找回原对话，不会为了省事再发一份相同请求。

## 隐私与安全

发送前会在本地拦截常见的 API key、密码、访问令牌、cookie/session、private key、验证码和支付卡信息。

普通的项目或业务背景如果确实影响判断，可以保留；与当前问题无关的姓名、邮箱、地址等私人信息应该尽量删掉。安全检查的目标是拦住凭据和无关隐私，同时保留解决问题真正需要的上下文。

## 模型

新建 Web 会话时：

```text
GPT-5.6 Sol Pro
  ↓ 不可用
GPT-5.6 Sol High
  ↓ 不可用
停止
```

同一个已经验证过的 Web 对话会复用确认过的模型。只有新会话、Branch、会话身份变化、模型状态异常或明确要求重新检查时才会再次打开模型菜单。

Codex 自己正在使用什么模型或 reasoning level，不影响 Web 端模型选择。

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
├── scripts/
│   ├── build_attachment_bundle.py
│   └── safety_guard.py
├── evals/
│   └── evals.json
└── tests/
    ├── test_attachment_bundle.py
    ├── test_safety_guard.py
    └── test_skill_contract.py
```

详细运行规则见 [SKILL.md](skills/webgpt-consult/SKILL.md)。

## License

项目使用 [MIT License](LICENSE)。`CONTEXT_PACKET_V1`、Chrome consultation workflow 和多文件证据处理思路吸收自 `zjp1997720/zhijian-skills` 的 `gpt56-sol-pro-consult`，许可信息见 [THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md)。