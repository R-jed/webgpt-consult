<p align="center">
  <img src="https://img.shields.io/badge/AI-Consultant-blueviolet?style=for-the-badge&logo=openai&logoColor=white" alt="AI Consultant" />
</p>

<h1 align="center">webgpt consult</h1>

<p align="center">
  <strong>GPT-5.6 Sol Pro/High 第二意见咨询</strong><br/>
  <em>拿不准的时候，问问 GPT-5.6 Sol</em>
</p>

<p align="center">
  <a href="https://github.com/R-jed/webgpt-consult/releases"><img src="https://img.shields.io/badge/release-v1.0.0-blue" alt="release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
</p>

<p align="center">
  <a href="README_en.md">English</a> ·
  <a href="#关于">关于</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#使用场景">使用场景</a> ·
  <a href="#工作流程">工作流程</a> ·
  <a href="references/">参考文档</a>
</p>

<br/>

<a id="关于"></a>

## 关于

> **如果你是 AI Agent，请阅读 [README_Agent.md](README_Agent.md) 获取引导指令。**

本地 Agent 遇到复杂问题时，可以调用这个工具去问 GPT-5.6 Sol。它会帮你打包上下文、发请求、拿回复，然后你自己决定采不采纳。

```
你的判断
  → 打包上下文（8K-15K 字符）
  → 安全扫描（防止泄露凭证）
  → Chrome 插件（默认）或 OpenCLI（备选）
  → 选 GPT-5.6 Sol Pro/High
  → 发送、等回复、验证哨兵标记
  → 你来决定采纳、拒绝还是修改
```

**为什么需要它：**
- 复杂决策需要外部视角，但不能盲目信外模型
- 上下文包保留你的判断、证据和约束
- 哨兵标记确认回复完整，防止半截结果
- 安全扫描防泄露敏感信息

<p align="right">(<a href="#关于">返回顶部</a>)</p>

<a id="快速开始"></a>

## 快速开始

### 环境要求

- **Codex CLI** 已连接 Chrome 插件
- **Chrome** 已登录 ChatGPT Web
- **ChatGPT Plus/Pro** 账户，有 GPT-5.6 Sol Pro 或 High
- **Python 3.x**

### 安装

```bash
git clone https://github.com/R-jed/webgpt-consult.git
```

### 验证

```bash
python3 scripts/check_packet_safety.py --help
```

<p align="right">(<a href="#快速开始">返回顶部</a>)</p>

<a id="使用场景"></a>

## 使用场景

| 场景 | 说明 |
|------|------|
| 架构审查 | 系统设计、API 设计、数据库 schema |
| 商业咨询 | 战略、定价、市场分析 |
| 调试 | 复杂 Bug、性能问题、竞态条件 |
| 风险审查 | 安全审计、技术债务 |
| 规划 | 项目规划、Sprint 计划 |
| 内容策略 | 文档、营销、技术写作 |

### 路由

| 条件 | 路径 |
|------|------|
| 默认 | Chrome 插件 |
| Chrome 不可用 + OpenCLI 就绪 | OpenCLI |
| 都不可用 | 停止，报告连接缺失 |

<p align="right">(<a href="#使用场景">返回顶部</a>)</p>

<a id="工作流程"></a>

## 工作流程

### 1. 先写你的判断

别急着问，先想清楚：
- 问题是什么，成功标准是什么
- 你有什么证据和约束
- 有哪些选项，各自代价是什么
- 你试过什么，还有哪些不确定

### 2. 打包上下文

用[模板](references/context-packet-template.md)组织内容。文件多的话打包：

```bash
python3 scripts/build_attachment_bundle.py /path/to/artifacts -o /tmp/bundle.md
```

### 3. 安全扫描

```bash
python3 scripts/check_packet_safety.py packet.md
```

去掉凭证，保留有用的项目上下文。

### 4. 发请求

- **Chrome**：走 [Chrome 工作流](references/chrome-workflow.md)
- **OpenCLI**：走 [OpenCLI 备选](references/opencli-fallback.md)（符合条件时）

### 5. 验证并决策

- 确认 `WEBGPT_CONSULT_RESULT_...` 哨兵出现
- 和你的判断对比
- 采纳、拒绝或修改

<p align="right">(<a href="#工作流程">返回顶部</a>)</p>

<a id="模型路由"></a>

## 模型路由

| 优先级 | 模型 | 说明 |
|--------|------|------|
| 1 | GPT-5.6 Sol Pro | 首选，推理最强 |
| 2 | GPT-5.6 Sol High | Pro 不可用时降级 |
| - | Extra High/Medium/Instant | 不支持，直接失败 |

选完之后验证：
1. 选中的层级名出现在 `menuitemradio`
2. `aria-checked=true` 存在
3. 选择器里有 GPT-5.6 Sol 系列证据

<p align="right">(<a href="#模型路由">返回顶部</a>)</p>

<a id="项目结构"></a>

## 项目结构

```
webgpt-consult/
├── SKILL.md                    # 主文档
├── README.md                   # 本文件
├── agents/
│   └── openai.yaml            # Agent 配置
├── references/
│   ├── chrome-workflow.md     # Chrome 工作流
│   ├── opencli-fallback.md    # OpenCLI 备选
│   └── context-packet-template.md  # 上下文包模板
├── scripts/
│   ├── run_webgpt_consult.py  # 主运行器
│   ├── check_packet_safety.py # 凭证扫描
│   ├── build_attachment_bundle.py  # 文件打包
│   ├── extract_chatgpt_reply.py    # 回复提取
│   └── model_router.py        # 模型选择
└── tests/
    └── test_*.py
```

<p align="right">(<a href="#项目结构">返回顶部</a>)</p>

<a id="执行示例"></a>

## 执行示例

### Pro 可用

```
可用：Pro, High
选择：Pro
降级：否
```

### Pro 不可用

```
可用：High
选择：High
降级：是
```

### 无支持层级

```
可用：Extra High, Medium, Instant
结果：失败
```

<p align="right">(<a href="#执行示例">返回顶部</a>)</p>

<a id="许可证"></a>

## 许可证

MIT - 详见 [LICENSE](LICENSE)。

<p align="right">(<a href="#许可证">返回顶部</a>)</p>
