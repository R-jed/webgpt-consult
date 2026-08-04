# WebGPT Consult — AI Agent Bootstrap

> ⚡ **仅限 AI Agent 阅读。** 如果你是人类读者，请返回 [README.md](README.md)（中文）或 [README_en.md](README_en.md)（English）。

本文件包含 AI Agent 的引导指令、路由策略和行为链。如果你是 AI Agent（Claude Code、Codex CLI、Cursor 等），**读完本文件后立即执行第 0 节**。

---

## 0. AI Agent 首要指令（读完本文件后立即执行）

> **AI 读完本文件后，必须自动执行以下配置流程并报告结果。用户无需手动操作。**

### 自动配置流程

```text
1. 检测本包的实际安装路径（从本文件位置推导，即包含 README.md 的目录）
2. 检测本地环境：
   - 操作系统类型
   - Python 版本
   - Chrome 是否可用
   - OpenCLI 是否可用
3. 读取 SKILL.md → 执行其中的所有指令
4. 根据路由策略选择咨询路径：
   - Chrome 插件可用 → 使用 Chrome 工作流
   - Chrome 不可用 + OpenCLI 就绪 → 使用 OpenCLI 备选
   - 两者都不可用 → 停止并报告连接缺失
5. 执行用户任务
```

### 示例报告格式

```markdown
✅ **WebGPT Consult 配置完成**

**安装路径**: /path/to/webgpt-consult
**系统环境**: macOS / Linux / Windows
**Python 版本**: 3.x.x
**Chrome 插件**: 可用 / 不可用
**OpenCLI**: 可用 / 不可用
**咨询路径**: Chrome 工作流 / OpenCLI 备选 / 无可用路径
**模型**: GPT-5.6 Sol Pro / High
**状态**: 就绪，等待用户任务
```

---

## 这是什么

这不是一个普通的 Skill，而是一个**结构化第二意见咨询系统**。它解决两个问题：

1. **本地 Agent 需要外部视角**：复杂决策、架构设计、调试难题需要第二意见
2. **保护本地判断**：上下文包保留本地证据、约束和判断，外部模型仅提供建议

---

## 核心工作流

```
用户任务
  → 本地 Agent 判断（先写出来）
  → 构建上下文包（8K-15K 字符）
  → 安全扫描（凭证检查）
  → Chrome 插件（默认）或 OpenCLI（备选）
  → 选择 GPT-5.6 Sol Pro/High
  → 发送、等待、提取并验证哨兵标记
  → 本地采纳决策（采纳/拒绝/修改）
```

---

## 文件清单

如果你只读三个文件，按这个顺序：

| 顺序 | 文件 | 用途 |
|------|------|------|
| 1 | [SKILL.md](SKILL.md) | 主技能文档，完整工作流和规则 |
| 2 | [references/context-packet-template.md](references/context-packet-template.md) | 上下文包模板 |
| 3 | [references/chrome-workflow.md](references/chrome-workflow.md) | Chrome 插件工作流 |

### 完整文件结构

```text
webgpt-consult/
├── SKILL.md                    # 主技能文档（必须阅读）
├── README.md                   # 中文说明（人类读者）
├── README_en.md                # 英文说明（人类读者）
├── README_Agent.md             # 本文件（AI Agent）
├── agents/
│   └── openai.yaml            # Agent 配置
├── evals/
│   └── evals.json             # 评估提示词
├── references/
│   ├── chrome-workflow.md     # Chrome 插件工作流（必须阅读）
│   ├── opencli-fallback.md    # OpenCLI 备选指南
│   └── context-packet-template.md  # 上下文包模板（必须阅读）
├── scripts/
│   ├── run_webgpt_consult.py  # 主咨询运行器
│   ├── check_packet_safety.py # 凭证扫描器
│   ├── build_attachment_bundle.py  # 文件打包器
│   ├── extract_chatgpt_reply.py    # 回复提取器
│   └── model_router.py        # 模型选择逻辑
└── tests/
    └── test_*.py              # 测试套件
```

---

## 路由策略

### 模型选择优先级

| 优先级 | 模型 | 状态 | 说明 |
|--------|------|------|------|
| 1 | GPT-5.6 Sol Pro | 首选 | 最强推理能力 |
| 2 | GPT-5.6 Sol High | 备选 | Pro 不可用时使用 |
| - | Extra High/Medium/Instant | 不支持 | 失败关闭 |

### 路径选择

| 条件 | 路径 | 操作 |
|------|------|------|
| 默认 | Codex Chrome 插件 | 遵循 [chrome-workflow.md](references/chrome-workflow.md) |
| Chrome 不可用 + OpenCLI 就绪 | OpenCLI 备选 | 遵循 [opencli-fallback.md](references/opencli-fallback.md) |
| 两者都不可用 | 停止 | 报告连接缺失，等待用户配置 |

---

## 安全规则

### 凭证卫生

**禁止发送**：
- Token、Cookie、密码
- API Key、私钥
- OAuth Header、浏览器配置文件
- Session Dump

**允许发送**：
- 普通用户业务和项目上下文
- 代码片段、架构设计
- 错误日志、调试信息

### 安全扫描

每次咨询前必须运行：

```bash
SKILL_DIR="<path-to-installed-webgpt-consult>"
python3 "$SKILL_DIR/scripts/check_packet_safety.py" packet.md
```

---

## 咨询完成条件

一个咨询**只有满足以下所有条件**才算完成：

1. ✅ 已验证支持的 GPT-5.6 Sol 层级（Pro 或 High）
2. ✅ 发送前提示词和所有必需附件已可见
3. ✅ 助手已停止生成
4. ✅ 已提取完整的助手回复
5. ✅ `WEBGPT_CONSULT_RESULT_...` 哨兵标记出现在回复中

**如果用户说结果已经可见**：重新提取现有对话，不要重复提交。

---

## 失败处理

| 场景 | 处理方式 |
|------|----------|
| Chrome 插件不可用 | 仅在 OpenCLI 预检成功时使用；否则停止并报告 |
| 未登录 | 请用户在 Chrome 配置文件中登录 ChatGPT Web |
| 无 Pro 或 High | 停止并报告未找到 GPT-5.6 Sol Pro 或 High |
| 选择后验证失败 | 停止并报告选择了哪个层级但无法确认 |
| 附件失败 | 通过 Chrome 真实文件选择器重试、粘贴内容或使用 Markdown 打包 |
| 仍在生成 | 在同一对话中继续等待 |
| 完成后缺少哨兵 | 再次提取完整助手回复；否则标记咨询未完成 |
| 低质量回答 | 仅使用支持的部分，本地 Agent 保留最终判断 |

---

## 快速开始

### 环境要求

- **Codex CLI** 已连接 Chrome 插件（默认路径）
- **Chrome 配置文件** 已登录 ChatGPT Web
- **ChatGPT Plus/Pro** 账户，可用 GPT-5.6 Sol Pro 或 High
- **Python 3.x**（用于安全扫描和文件打包）

### 验证设置

```bash
# 检查 Python
python3 --version

# 检查安全扫描器
python3 scripts/check_packet_safety.py --help

# 检查文件打包器
python3 scripts/build_attachment_bundle.py --help
```

---

## 依赖表格

### 核心依赖

| 组件 | 是否必需 | 用途 |
|------|----------|------|
| Python 3.x | 必需 | 安全扫描、文件打包、回复提取 |
| Codex CLI | 推荐 | AI 编程助手，默认咨询路径 |
| Chrome 插件 | 推荐 | 默认咨询路径 |
| OpenCLI | 可选 | 备选咨询路径 |

### Python 脚本

| 脚本 | 用途 |
|------|------|
| `check_packet_safety.py` | 凭证扫描，防止敏感数据泄露 |
| `build_attachment_bundle.py` | 多文件打包成单一 Markdown |
| `extract_chatgpt_reply.py` | 从 OpenCLI 提取回复 |
| `model_router.py` | 模型选择逻辑 |
| `run_webgpt_consult.py` | 主咨询运行器 |

---

## 常见问题

**Q1: Chrome 插件不可用怎么办？**
A: 检查 OpenCLI 是否就绪（`opencli doctor`）。如果都不可用，停止并报告连接缺失。

**Q2: 为什么选择 Pro 后显示降级？**
A: 这是预期行为。当 Pro 不可用时，系统自动降级到 High，并在元数据中报告 `downgraded=true`。

**Q3: 上下文包应该多大？**
A: 8K-15K 字符。太短会丢失因果细节，太长会稀释关键信息。

**Q4: 哨兵标记是什么？**
A: `WEBGPT_CONSULT_RESULT_YYYYMMDD_HHMMSS` 格式的标记，用于验证咨询是否完成。

**Q5: 可以发送代码吗？**
A: 可以。代码是普通项目上下文，不是凭证。但不要发送包含密钥的配置文件。

---

## 行为链摘要

AI Agent 的完整行为链：

1. **读取本文件** → 理解整体结构
2. **执行第 0 节** → 自动配置并报告
3. **读取 SKILL.md** → 理解完整工作流
4. **根据路由策略选择路径** → Chrome 或 OpenCLI
5. **构建上下文包** → 使用模板
6. **运行安全扫描** → 凭证检查
7. **执行咨询** → 发送、等待、提取
8. **验证哨兵标记** → 确认完成
9. **本地采纳决策** → 采纳/拒绝/修改
10. **返回结果** → 格式化输出

---

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)。

---

## 返回

- [README.md](README.md) - 中文说明
- [README_en.md](README_en.md) - 英文说明
