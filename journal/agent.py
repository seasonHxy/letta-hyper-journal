"""创建/加载「交易复盘记忆助手」Agent。

设计要点（把学到的都用上）：
  - 有状态：Agent 存在 server 里，跨会话持续，记得你之前聊过的每笔交易。
  - 三层记忆：
      core memory「human」块 —— Agent 自己维护「用户的交易风格/偏好」摘要
      archival memory        —— Agent 把每笔交易记录归档，之后能检索复盘
  - 自定义工具：calculate_pnl / position_size_for_risk（见 tools.py）
"""
from .config import get_client, LLM_CONFIG, EMBEDDING_CONFIG
from .tools import ALL_TOOLS

AGENT_NAME = "hyper-journal"

# letta 的 include_base_tools 只给核心记忆工具，不含归档。
# 复盘助手要把交易记进归档记忆，所以显式挂这两个内置工具。
ARCHIVAL_TOOLS = ["archival_memory_insert", "archival_memory_search"]

PERSONA = """我是你的交易复盘教练。职责：
- 你描述一笔交易时，我用 calculate_pnl 算盈亏，必要时用 position_size_for_risk 给仓位建议。
- 我会用 archival_memory_insert 把每笔交易（标的/方向/价格/盈亏/你的理由）归档，方便日后复盘。
- 我会在我的核心记忆里持续更新对你交易风格的认识（爱追高？止损纪律如何？）。
- 复盘时我用 archival_memory_search 调出历史，给出基于你真实记录的、诚实直接的反馈。"""


def get_or_create_agent():
    """有则加载、无则创建，并确保自定义工具已挂上。返回 (client, agent)。"""
    client = get_client()

    # 1) 注册/更新自定义工具（upsert 幂等）
    tool_ids = [client.tools.upsert(source_code=src).id for src in ALL_TOOLS]

    # 1b) 查出内置归档工具的 id（按名字）
    by_name = {t.name: t.id for t in client.tools.list()}
    tool_ids += [by_name[n] for n in ARCHIVAL_TOOLS if n in by_name]

    # 2) 找现有 Agent
    existing = [a for a in client.agents.list() if a.name == AGENT_NAME]
    if existing:
        agent = existing[0]
        attached = {t.id for t in client.agents.tools.list(agent_id=agent.id)}
        for tid in tool_ids:  # 只挂还没挂的（避免重复）
            if tid not in attached:
                client.agents.tools.attach(tool_id=tid, agent_id=agent.id)
        return client, agent

    # 3) 创建新 Agent
    agent = client.agents.create(
        name=AGENT_NAME,
        llm_config=LLM_CONFIG,
        embedding_config=EMBEDDING_CONFIG,
        memory_blocks=[
            {"label": "persona", "value": PERSONA},
            {"label": "human", "value": "（还在了解这位交易者的风格）"},
        ],
        tool_ids=tool_ids,
        include_base_tools=True,  # 带上内置记忆/归档工具
    )
    return client, agent
