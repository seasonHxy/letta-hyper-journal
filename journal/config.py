"""连接 Letta server + 模型配置（智谱 GLM，OpenAI 兼容）。

整个 app 是 Letta server 的一个客户端：它不自己跑模型，而是通过 SDK
让 server 上的有状态 Agent 干活。换模型只改这里。
"""
import os
from pathlib import Path

from letta_client import Letta


def _load_env():
    """极简 .env 加载（无需 python-dotenv）。"""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_client() -> Letta:
    _load_env()
    return Letta(base_url=os.environ.get("LETTA_BASE_URL", "http://localhost:8283"))


# 智谱国内开放平台（OpenAI 兼容）。server 从 OPENAI_API_KEY 读 key。
ZHIPU_BASE = "https://open.bigmodel.cn/api/paas/v4"

LLM_CONFIG = {
    "model": "glm-4-flash",            # 免费聊天模型
    "model_endpoint_type": "openai",
    "model_endpoint": ZHIPU_BASE,
    "context_window": 128000,
    "put_inner_thoughts_in_kwargs": True,
}

EMBEDDING_CONFIG = {
    "embedding_model": "embedding-3",   # 2048 维，Letta padding 到 4096
    "embedding_endpoint_type": "openai",
    "embedding_endpoint": ZHIPU_BASE,
    "embedding_dim": 2048,
}
