"""降级策略 — 当主方案失败时的兜底方案"""
import json
from pathlib import Path
from typing import Callable


class FallbackStrategy:
    """降级策略管理器"""

    # 降级链定义
    CHAINS = {
        "glm_image_check": [
            {"model": "GLM-4V-Plus", "description": "主力模型，精度最高"},
            {"model": "GLM-4V-Flash", "description": "免费降级模型"},
        ],
        "image_generation": [
            {"model": "gpt-image-2", "size": "1:1", "strength": 0.5, "description": "主力"},
            {"model": "gpt-image-2", "size": "1:1", "strength": 0.35, "description": "降 strength"},
            {"model": "nano-banana-pro", "size": "1:1", "strength": 0.5, "description": "切换模型"},
        ],
        "proxy_node": [
            {"action": "rotate_node", "prefer_us": True, "description": "优先美国节点"},
            {"action": "rotate_node", "prefer_us": False, "description": "任意节点"},
        ],
        "deepseek_call": [
            {"model": "deepseek-v4-pro", "description": "主力推理"},
            {"model": "deepseek-v3", "description": "降级推理"},
        ],
    }

    def __init__(self):
        self.history = []

    def execute(self, chain_name: str, fn_factory: Callable) -> dict:
        """按降级链依次尝试

        Args:
            chain_name: 降级链名称（glm_image_check/image_generation/proxy_node/deepseek_call）
            fn_factory: 接收当前策略配置，返回一个 callable。如:
                lambda cfg: lambda: call_glm(cfg["model"])

        Returns:
            {
                "success": bool,
                "result": any,
                "strategy_used": dict,
                "attempts": int,
                "history": list
            }
        """
        chain = self.CHAINS.get(chain_name)
        if not chain:
            return {"success": False, "error": f"未知降级链: {chain_name}", "attempts": 0}

        for i, strategy in enumerate(chain):
            fn = fn_factory(strategy)
            try:
                result = fn()
                self.history.append({
                    "strategy_index": i,
                    "strategy": strategy,
                    "success": True
                })
                return {
                    "success": True,
                    "result": result,
                    "strategy_used": strategy,
                    "attempts": i + 1,
                    "history": self.history
                }
            except Exception as e:
                self.history.append({
                    "strategy_index": i,
                    "strategy": strategy,
                    "success": False,
                    "error": str(e)
                })

        return {
            "success": False,
            "error": f"降级链 {chain_name} 全部失败",
            "attempts": len(chain),
            "history": self.history
        }


# ── 便捷函数 ──

def glm_vision_with_fallback(image_path: str, question: str) -> dict:
    """GLM-4V 调用，失败时降级 Flash"""
    from verification.image_validator import _call_glm4v

    fallback = FallbackStrategy()

    def factory(strategy: dict) -> Callable:
        model = strategy["model"]
        def call():
            # Flash 模型用不同的 base URL
            if "Flash" in model:
                import base64
                from openai import OpenAI
                client = OpenAI(
                    api_key="61ffd79cb5394e0284550b88ff3c0eda.hai1zorE9yumVzsd",
                    base_url="https://open.bigmodel.cn/api/paas/v4"
                )
                img = Path(image_path).read_bytes()
                b64 = base64.b64encode(img).decode()
                ext = Path(image_path).suffix.lower().lstrip(".")
                mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}
                mime = mime_map.get(ext, "image/png")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                        {"type": "text", "text": question}
                    ]}],
                    stream=False, timeout=60
                )
                return resp.choices[0].message.content
            else:
                return _call_glm4v(image_path, question)

    return fallback.execute("glm_image_check", factory)


def image_gen_with_fallback(gen_fn_factory: Callable) -> dict:
    """生图失败时自动降级"""
    fallback = FallbackStrategy()
    return fallback.execute("image_generation", gen_fn_factory)


if __name__ == "__main__":
    print("降级策略模块已就绪")
    print("可用降级链:", list(FallbackStrategy.CHAINS.keys()))
