"""命令行聊天入口：和「交易复盘记忆助手」对话。

用法：
  python chat.py                    # 进入交互式对话（输入 exit 退出）
  python chat.py "我用2.5买了1000个HYPE，现在3.1"   # 单条快速发问

前置：Letta server 在跑、.env 配好智谱 key。
"""
import sys

from journal.agent import get_or_create_agent


def print_response(response):
    for msg in response.messages:
        mtype = getattr(msg, "message_type", "?")
        if mtype == "reasoning_message":
            print(f"  🧠 {msg.reasoning}")
        elif mtype == "assistant_message":
            print(f"\n助手：{msg.content}\n")
        elif mtype == "tool_call_message":
            tc = msg.tool_call
            print(f"  🔧 调用 {tc.name}({tc.arguments})")
        elif mtype == "tool_return_message":
            print(f"  ↩️  {msg.tool_return}")


def ask(client, agent, text):
    resp = client.agents.messages.create(
        agent_id=agent.id,
        messages=[{"role": "user", "content": text}],
    )
    print_response(resp)


def main():
    print("正在连接 Letta server 并加载 Agent ...")
    client, agent = get_or_create_agent()
    print(f"✅ 交易复盘助手就绪（agent_id={agent.id}）\n")

    if len(sys.argv) > 1:  # 单条模式
        q = " ".join(sys.argv[1:])
        print(f"你：{q}")
        ask(client, agent, q)
        return

    print("进入对话（输入 exit / quit 退出）。试试：")
    print('  「我用 2.5 买入 1000 个 HYPE，现在 3.1，帮我算下盈亏并记下来」')
    print('  「我账户 10000，想冒 1% 风险，入场 3.1 止损 2.9，开多大仓位？」')
    print('  「回顾下我之前的交易，我有什么毛病？」\n')
    while True:
        try:
            q = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if q.lower() in ("exit", "quit", ""):
            print("再见。")
            break
        ask(client, agent, q)


if __name__ == "__main__":
    main()
