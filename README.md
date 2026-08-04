<p align="center">
  <img src="https://img.shields.io/badge/AI-Consultant-blueviolet?style=for-the-badge&logo=openai&logoColor=white" alt="AI Consultant" />
</p>

<h1 align="center">WebGPT Consult</h1>

<p align="center">
  <strong>GPT-5.6 Sol Pro/High 专业第二意见伙伴</strong><br/>
  <em>为复杂规划、架构设计、调试、商业、产品、内容策略、风险审查和技能设计提供深度咨询</em>
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
  <a href="references/">参考文档</a> ·
  <a href="#参与贡献">参与贡献</a>
</p>

<br/>

<a id="关于"></a>

## 关于

> **如果你是 AI Agent，请阅读 [README_Agent.md](README_Agent.md) 获取引导指令。**

当本地 AI Agent（Claude Code、Codex CLI、Cursor 等）遇到复杂问题需要外部视角时，WebGPT Consult 会将其路由到最佳的 GPT-5.6 Sol 层级，构建结构化上下文包，执行咨询，并带回经过验证的结果供本地采纳。

```
本地 Agent 判断
  → 构建上下文包（8K-15K 字符）
  → 安全扫描（凭证检查）
  → Chrome 插件（默认）或 OpenCLI（备选）
  → 选择 GPT-5.6 Sol Pro/High
  → 发送、等待、提取并验证哨兵标记
  → 本地采纳决策
```

**为什么需要这个工具：**
- 本地 Agent 需要对复杂决策获得第二意见，但不应盲目信任外部模型
- 上下文包保留了本地判断、证据和约束条件
- 基于哨兵的完成验证防止了不完整或损坏的结果
- 凭证卫生保护敏感数据不泄露给外部模型

<p align="right">(<a href="#关于">返回顶部</a>)</p>

<a id="快速开始"></a>

## 快速开始

### 环境要求

- **Codex CLI** 已连接 Chrome 插件（默认路径）
- **Chrome 配置文件** 已登录 ChatGPT Web
- **ChatGPT Plus/Pro** 账户，可用 GPT-5.6 Sol Pro 或 High
- **Python 3.x**（用于安全扫描和文件打包）

### 安装

```bash
git clone https://github.com/R-jed/webgpt-consult.git
```

添加到 Codex 技能目录或直接引用。

### 验证设置

```bash
# 检查 Chrome 插件连接
opencli doctor

# 测试安全扫描器
python3 scripts/check_packet_safety.py --help
```

<p align="right">(<a href="#快速开始">返回顶部</a>)</p>

<a id="使用场景"></a>

## 使用场景

### 支持的咨询类型

| 类型 | 说明 |
|------|------|
| 架构审查 | 系统设计、API 设计、数据库 schema、基础设施 |
| 商业咨询 | 战略、定价、市场分析、竞争定位 |
| 内容策略 | 文档、营销、技术写作 |
| 技能设计 | AI Agent 技能、工作流自动化、工具集成 |
| 风险审查 | 安全审计、合规性、技术债务评估 |
| 调试支持 | 复杂 Bug、性能问题、竞态条件 |
| 规划建议 | 项目规划、Sprint 计划、资源分配 |

### 路由策略

| 条件 | 路径 |
|------|------|
| 默认 | Codex Chrome 插件 |
| Chrome 不可用 + OpenCLI 就绪 | OpenCLI 备选 |
| 两者都不可用 | 停止并报告连接缺失 |

<p align="right">(<a href="#使用场景">返回顶部</a>)</p>

<a id="工作流程"></a>

## 工作流程

### 1. 本地判断优先

咨询前，先写出本地的最佳评估：

- 决策或问题陈述
- 成功标准和用户意图
- 证据和约束条件
- 选项和权衡
- 已尝试的方案和未知因素

### 2. 构建上下文包

使用[模板](references/context-packet-template.md)组织咨询内容：

```bash
# 多文件时，构建打包文件
python3 scripts/build_attachment_bundle.py /path/to/artifacts -o /tmp/bundle.md
```

### 3. 安全检查

```bash
python3 scripts/check_packet_safety.py packet.md
```

移除类凭证材料，保留有用的项目上下文。

### 4. 执行咨询

- **Chrome 路径**：遵循 [Chrome 工作流](references/chrome-workflow.md)
- **OpenCLI 路径**：遵循 [OpenCLI 备选](references/opencli-fallback.md)（仅在符合条件时）

### 5. 验证并采纳

- 确认 `WEBGPT_CONSULT_RESULT_...` 哨兵标记出现
- 与本地证据对比
- 决策：采纳、拒绝或修改

<p align="right">(<a href="#工作流程">返回顶部</a>)</p>

<a id="模型路由"></a>

## 模型路由

### 选择优先级

| 优先级 | 模型 | 状态 |
|--------|------|------|
| 1 | GPT-5.6 Sol Pro | 首选 |
| 2 | GPT-5.6 Sol High | 备选 |
| - | Extra High/Medium/Instant | 不支持（失败关闭） |

### 验证流程

选择层级后，验证：
1. 层级名称出现在已选中的 `menuitemradio`
2. `aria-checked=true` 属性存在
3. 选择器中有 GPT-5.6 Sol 系列证据

<p align="right">(<a href="#模型路由">返回顶部</a>)</p>

<a id="项目结构"></a>

## 项目结构

```
webgpt-consult/
├── SKILL.md                    # 主技能文档
├── README.md                   # 英文说明
├── README_zh.md                # 中文说明
├── agents/
│   └── openai.yaml            # Agent 配置
├── evals/
│   └── evals.json             # 评估提示词
├── references/
│   ├── chrome-workflow.md     # Chrome 插件工作流
│   ├── opencli-fallback.md    # OpenCLI 备选指南
│   └── context-packet-template.md  # 上下文包模板
├── scripts/
│   ├── run_webgpt_consult.py  # 主咨询运行器
│   ├── check_packet_safety.py # 凭证扫描器
│   ├── build_attachment_bundle.py  # 文件打包器
│   ├── extract_chatgpt_reply.py    # 回复提取器
│   └── model_router.py        # 模型选择逻辑
└── tests/
    └── test_*.py              # 测试套件
```

<p align="right">(<a href="#项目结构">返回顶部</a>)</p>

<a id="执行示例"></a>

## 执行示例

### Pro 可用（首选）

```
可用：Pro, High
选择：Pro
降级：否
```

### Pro 不可用（备选）

```
可用：High
选择：High
降级：是
```

### 无支持层级

```
可用：Extra High, Medium, Instant
结果：失败关闭
```

<p align="right">(<a href="#执行示例">返回顶部</a>)</p>

<a id="参与贡献"></a>

## 参与贡献

欢迎贡献！请：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 提交 Pull Request

<p align="right">(<a href="#参与贡献">返回顶部</a>)</p>

<a id="许可证"></a>

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)。

<p align="right">(<a href="#许可证">返回顶部</a>)</p>

<a id="致谢"></a>

## 致谢

基于以下项目构建：
- [Codex CLI](https://github.com/openai/codex) - AI 编程助手
- ChatGPT Web - GPT-5.6 Sol Pro/High 模型访问
- OpenCLI - 可选的浏览器自动化

<p align="right">(<a href="#致谢">返回顶部</a>)</p>
