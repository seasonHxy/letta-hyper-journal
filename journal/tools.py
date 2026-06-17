"""自定义工具（L2 二次开发）——交易计算能力，交给 Agent 自主调用。

每个工具就是一个普通 Python 函数，约定：
  - 类型注解 → Letta 自动生成参数 schema
  - docstring 的 Args 段 → 参数说明（模型据此填参）
  - 返回 str
  - 自包含：import 写函数体内（沙箱里独立执行）

这些函数以「源码字符串」注册到 server（见 agent.py），所以这里保留源码形态。
"""

CALCULATE_PNL = '''
def calculate_pnl(entry_price: float, exit_price: float, size: float, side: str = "long") -> str:
    """计算一笔交易的盈亏，支持做多/做空。

    Args:
        entry_price (float): 入场价格
        exit_price (float): 出场（或当前）价格
        size (float): 持仓数量
        side (str): 方向，"long"（做多）或 "short"（做空），默认 long

    Returns:
        str: 盈亏金额与收益率
    """
    s = (side or "long").lower()
    diff = (exit_price - entry_price) if s == "long" else (entry_price - exit_price)
    pnl = diff * size
    pct = diff / entry_price * 100 if entry_price else 0.0
    tag = "盈利" if pnl >= 0 else "亏损"
    return f"[{s}] {tag} {abs(pnl):.2f}（收益率 {pct:+.2f}%）"
'''

POSITION_SIZE = '''
def position_size_for_risk(account_balance: float, risk_pct: float, entry_price: float, stop_price: float) -> str:
    """根据可承受风险算出该开多大仓位（风险管理）。

    Args:
        account_balance (float): 账户总资金
        risk_pct (float): 本笔愿承担的风险百分比，如 1 表示 1%
        entry_price (float): 计划入场价
        stop_price (float): 止损价

    Returns:
        str: 建议持仓数量与对应名义价值
    """
    risk_amount = account_balance * (risk_pct / 100.0)
    per_unit_risk = abs(entry_price - stop_price)
    if per_unit_risk == 0:
        return "止损价不能等于入场价，无法计算仓位。"
    size = risk_amount / per_unit_risk
    notional = size * entry_price
    return f"建议持仓 {size:.4f} 个（名义价值 {notional:.2f}），最大亏损约 {risk_amount:.2f}"
'''

LOG_TRADE = '''
def log_trade(symbol: str, side: str, entry_price: float, exit_price: float, size: float, reason: str) -> str:
    """把一笔交易格式化成规范记录（自己算盈亏，不依赖模型口算）。

    用途：记录交易前先调它拿到「规范记录字符串」，再把该字符串原样归档，
    这样归档里的数字永远准确。

    Args:
        symbol (str): 标的，如 HYPE
        side (str): 方向，"long" 或 "short"
        entry_price (float): 入场价
        exit_price (float): 出场（或当前）价
        size (float): 数量
        reason (str): 交易理由

    Returns:
        str: 规范化的一行交易记录（请原样用于归档，勿改数字）
    """
    s = (side or "long").lower()
    diff = (exit_price - entry_price) if s == "long" else (entry_price - exit_price)
    pnl = diff * size
    pct = diff / entry_price * 100 if entry_price else 0.0
    return (
        f"[{symbol}] {s} {entry_price}->{exit_price} x{size} | "
        f"PnL {pnl:+.2f} ({pct:+.2f}%) | 理由: {reason}"
    )
'''

# 所有要注册的工具源码
ALL_TOOLS = [CALCULATE_PNL, POSITION_SIZE, LOG_TRADE]
