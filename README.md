# letta-hyper-journal · 交易复盘记忆助手

一个跑在 [Letta](https://github.com/letta-ai/letta)（前 MemGPT）之上的 AI Agent：
它用**自定义工具**帮你算盈亏/仓位，用 **Letta 的长期记忆**记住你每一笔交易和交易风格——
**越用越懂你**，复盘时能调出你的真实历史给出反馈。

这是「在 Letta 上做二次开发（应用层）」的一个完整示例：把 Letta 当有状态 Agent 后端，
通过 SDK 扩展自定义工具 + 利用其三层记忆，组成一个领域应用。

## 它能做什么

```
你：我用 2.5 买入 1000 个 HYPE，现在 3.1，帮我算下并记下来，突破前高追的。
  🔧 calculate_pnl(entry=2.5, exit=3.1, size=1000, side=long) → 盈利 600.00 (+24.00%)
  🔧 archival_memory_insert(...)  # 归档这笔交易
助手：盈利 600（+24%），已归档。

（换一天 / 新会话）
你：回顾我所有交易，我反复犯的毛病是什么？
  🔧 archival_memory_search("交易记录") → 调出历史两笔
助手：你反复在「突破前高」时追多——一笔赚一笔亏，追高缺乏纪律。
```

## 架构

```
你 ── chat.py ──SDK──> Letta server ──> 智谱 GLM (glm-4-flash)
                          │
                          ├── 自定义工具 (journal/tools.py)：calculate_pnl / position_size_for_risk
                          ├── core memory：persona（复盘教练）+ human（你的交易风格，Agent 自维护）
                          └── archival memory：每笔交易归档，可语义检索
```

- **有状态**：Agent 存在 server 里，跨进程/跨天持续，记得你聊过的一切。
- **自定义工具**：普通 Python 函数 → `client.tools.upsert` 注册 → Agent 自主调用。
- **记忆**：核心记忆放「你是谁/你的风格」，归档记忆放「每笔交易」，按需检索。

## 运行

前置：一个跑着的 **Letta server**（本项目用智谱 GLM，免费）。

```bash
# 1. 自部署 Letta server（Postgres + pgvector），监听 localhost:8283
#    见 https://docs.letta.com/guides/selfhosting/

# 2. 配置
cp .env.example .env        # 填入智谱 key：https://open.bigmodel.cn/usercenter/apikeys

# 3. 装依赖
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. 对话
python chat.py                                   # 交互式
python chat.py "我3.1做空500个BTC，现在2.9"       # 单条
```

## 目录

| 文件 | 作用 |
|---|---|
| `chat.py` | 命令行对话入口 |
| `journal/config.py` | 连 server + 模型配置（智谱，换 provider 只改这里）|
| `journal/tools.py` | 自定义工具源码（盈亏、仓位风险）|
| `journal/agent.py` | 创建/加载 Agent，挂记忆块 + 工具 |

## 模型选择（一个真实的工程教训）

本应用是**多工具 agentic 编排**（算账→格式化→归档→检索→复盘），对模型的工具链与指令遵从要求高：

| 模型 | 成本 | 表现 |
|---|---|---|
| **glm-4.6**（默认） | 便宜（按量） | 可靠链式调工具、遵守指令、复盘到位 ✅ |
| glm-4-flash | 免费 | 工具链会断、无视否定指令，复盘不稳 —— 仅适合简单 demo |

切换：`.env` 里设 `LLM_MODEL=glm-4-flash`。结论：**agentic 任务别用太弱的模型**。

## Roadmap

- [x] **确定性归档**：`log_trade` 工具自己算 PnL 并返回规范记录，模型只需原样归档，杜绝数字笔误。
- [ ] 增加 `win_rate` / `avg_pnl` 自定义统计工具（目前靠模型口算，可下沉为确定性工具）。
- [ ] 接真实行情：`get_price(symbol)` 工具调 Hyperliquid/交易所 API，"现在多少"自动取价。
- [ ] 让自定义工具直接写归档（`agent_state` 注入），把记录两步合并为一步。

## 技术栈

Letta 0.16.x · letta-client SDK · 智谱 GLM（OpenAI 兼容，glm-4.6 / embedding-3）· Postgres + pgvector

---
基于 Letta（Apache-2.0）二次开发。
