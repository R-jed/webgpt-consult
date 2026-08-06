<p align="center">
  <img src="./skills/webgpt-consult/assets/mobius-white.svg" alt="webgpt-consult" width="136" />
</p>

<h1 align="center">webgpt-consult</h1>
<p align="center">Codex → Chrome → ChatGPT Web</p>

<p align="center">
  <a href="#安装">安装</a> ·
  <a href="#怎么用">怎么用</a> ·
  <a href="#它会做什么">它会做什么</a> ·
  <a href="#文件和安全">文件和安全</a> ·
  <a href="README_en.md">English</a>
</p>

## 关于项目

`webgpt-consult` 做的事情很简单：让 Codex 打开 ChatGPT 网页，把你正在处理的问题和真正需要的资料交给 GPT-5.6 Sol，再把回答带回当前任务。

它适合用在这些场景：代码或排错卡住了，想让另一个模型找遗漏；准备定架构或产品方案，想再听一个独立意见；改完一轮以后，想继续在同一个 Web 对话里追问；或者最终提交前想再做一次严格检查。

简单问题直接问。复杂问题会把背景、证据、已经试过的方法、当前判断和风险整理好再发过去。后续追问会尽量继续使用同一个 ChatGPT Web 对话，所以不用每一轮都重新交代全部背景，也不用反复打开模型菜单。

> **如果你是 AI Agent，请先看 [README_Agent.md](README_Agent.md)。真正的运行规则写在 [skills/webgpt-consult/SKILL.md](skills/webgpt-consult/SKILL.md)。**

## 安装

你需要：

- Codex
- 能被 Codex 控制的 Chrome
- 已经登录 ChatGPT Web 的账号
- 账号里能使用 GPT-5.6 Sol Pro 或 High

安装到当前项目：

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

全局安装的更新命令加 `-g`。

## 怎么用

直接调用：

```text
/webgpt-consult <你想让 ChatGPT Web 帮忙看的问题>
```

例如：

```text
/webgpt-consult 这个登录问题我已经排查很久了，请让 GPT-5.6 Sol 帮我找根因，需要的话看相关源码和日志。
```

你不需要自己整理浏览器步骤，也不需要手动复制来回复制去。Codex 会决定哪些资料值得带过去，然后负责把 Web 端的结果带回来。

## 它会做什么

一次正常咨询大致是这样：

```text
你的问题
  ↓
Codex 先理解任务，并挑出真正相关的资料
  ↓
在本地检查敏感信息
  ↓
继续已有的 ChatGPT Web 对话，或开一个新的对话
  ↓
新对话优先使用 GPT-5.6 Sol Pro，Pro 没有就用 High
  ↓
上传需要的真实文件并确认消息内容正确
  ↓
只发送一次，等待完整回答
  ↓
Codex 再用本地源码、日志和事实核对 Web 端建议
  ↓
把有用的结论带回当前任务
```

如果你继续追问同一个问题，Skill 会尽量沿用已经确认过的 Web 对话和模型。例如第一轮让它审架构，第二轮告诉它“我已经改完了，再看一次”，第三轮再补一份失败日志，都可以留在同一个咨询上下文里。

如果原来的 Chrome 连接中断，Skill 会先找回原来的对话。尤其是在点击 Send 前后发生断线时，它不会为了省事再发送一份相同请求，从而避免重复咨询。

复杂任务会使用 `CONTEXT_PACKET_V1`。可以把它理解成一份整理好的咨询说明，把问题、背景、证据、已经做过什么、当前判断和风险分开写清楚。普通小问题不会强行套这个格式。

## 文件和安全

ChatGPT Web 看不到你电脑上的本地路径。写一句 `/Users/me/project/auth.py` 并不等于已经把文件交给它。真正需要看的源码、日志或文档必须实际上传、粘贴，或者整理成附件。

文件少时优先直接上传原文件。文件很多时，Skill 带有一个 bundle 工具，可以把选中的文本文件整理成一份 Markdown 附件，并保留文件名、大小和内容校验信息。它不会默认偷偷截断超大文件；如果资料会变得不完整，会先停下来，除非明确允许生成 partial bundle。

Bundle 支持普通 UTF-8 文本，也支持带明确 Unicode 编码标记的 UTF-16/UTF-32 文本。无法可靠判断编码时会停止，不会靠猜测改写内容。

发送前还会在本地检查常见的 API key、密码、访问令牌、cookie/session、private key、验证码和支付卡信息。发现这类内容时会先拦下来。普通项目背景如果确实会影响判断，可以保留；与问题无关的私人信息应尽量删掉。

## 模型和限制

新开一个 ChatGPT Web 对话时，模型顺序是：

```text
GPT-5.6 Sol Pro
  ↓ 不可用
GPT-5.6 Sol High
  ↓ 不可用
停止
```

同一个已经确认过的 Web 对话会继续使用原来的模型，不会每发一条消息都重新检查。

这个 Skill 只走 Codex 控制的 Chrome。它不会在磁盘上保存长期咨询记忆，也不会自动把整个仓库全部上传。ChatGPT Web 给出的内容始终是一份外部意见，最终结果仍由 Codex 结合本地事实判断。

## 给想看源码的人

核心文件在：

```text
skills/webgpt-consult/
├── SKILL.md                         # 整体规则
├── references/
│   ├── chrome-workflow.md           # Chrome 的实际执行流程
│   └── context-packet-template.md   # 复杂咨询的上下文格式
├── scripts/
│   ├── build_attachment_bundle.py   # 多文件打包
│   └── safety_guard.py              # 本地敏感信息检查
├── evals/evals.json                 # 浏览器场景验收用例
└── tests/                            # 自动测试
```

AI Agent 的入口说明见 [README_Agent.md](README_Agent.md)。详细运行规则见 [SKILL.md](skills/webgpt-consult/SKILL.md)。

## License

项目使用 [MIT License](LICENSE)。第三方版权与许可声明见 [THIRD_PARTY_NOTICES.md](skills/webgpt-consult/THIRD_PARTY_NOTICES.md)。
