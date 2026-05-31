"""统一重试管理 — 不同错误类型 → 不同恢复策略"""
import time
import random
import json
from functools import wraps
from pathlib import Path
from typing import Callable


class RetryConfig:
    """重试配置"""

    STRATEGIES = {
        "api_timeout": {"max_retries": 3, "base_delay": 10, "backoff": "equal"},
        "ebay_403": {"max_retries": 2, "base_delay": 15, "backoff": "equal", "pre_action": "rotate_node"},
        "glm_error": {"max_retries": 1, "base_delay": 2, "backoff": "equal", "fallback_model": "GLM-4V-Flash"},
        "image_validation_fail": {"max_retries": 2, "base_delay": 3, "backoff": "linear", "adjust_strength": True},
        "json_parse_error": {"max_retries": 1, "base_delay": 0, "backoff": "none"},
        "network_error": {"max_retries": 3, "base_delay": 5, "backoff": "exponential"},
        "rate_limit": {"max_retries": 2, "base_delay": 30, "backoff": "exponential"},
    }

    @classmethod
    def get(cls, error_type: str) -> dict:
        return cls.STRATEGIES.get(error_type, {"max_retries": 1, "base_delay": 5, "backoff": "equal"})


class RetryManager:
    """重试管理器"""

    def __init__(self, log_path: str = None):
        self.log = []
        self.log_path = Path(log_path) if log_path else None

    def _compute_delay(self, attempt: int, config: dict) -> float:
        """计算重试延迟"""
        base = config["base_delay"]
        backoff = config["backoff"]

        if backoff == "none":
            return 0
        elif backoff == "equal":
            return base
        elif backoff == "linear":
            return base * attempt
        elif backoff == "exponential":
            return base * (2 ** (attempt - 1))
        return base

    def execute(self, fn: Callable, error_type: str, *args, **kwargs) -> dict:
        """执行函数，失败时按策略重试

        Args:
            fn: 要执行的函数
            error_type: 错误类型（api_timeout/ebay_403/glm_error/image_validation_fail/json_parse_error/network_error/rate_limit）
            *args, **kwargs: 传递给 fn 的参数

        Returns:
            {
                "success": bool,
                "result": any,        # fn 的返回值（成功时）
                "error": str,         # 最后一次失败的错误信息（失败时）
                "attempts": int,
                "elapsed": float,
                "log": list
            }
        """
        config = RetryConfig.get(error_type)
        max_retries = config["max_retries"]
        start_time = time.time()
        last_error = None

        for attempt in range(1, max_retries + 2):  # +2 because 1st try + retries
            try:
                result = fn(*args, **kwargs)
                elapsed = round(time.time() - start_time, 2)
                entry = {
                    "attempt": attempt,
                    "success": True,
                    "elapsed": elapsed,
                    "error_type": error_type
                }
                self.log.append(entry)
                self._save_log()
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt,
                    "elapsed": elapsed,
                    "log": self.log
                }
            except Exception as e:
                last_error = str(e)
                self.log.append({
                    "attempt": attempt,
                    "success": False,
                    "error": last_error,
                    "error_type": error_type
                })

                if attempt > max_retries:
                    break

                delay = self._compute_delay(attempt, config)
                if delay > 0:
                    jitter = random.uniform(0, delay * 0.3)
                    time.sleep(delay + jitter)

        elapsed = round(time.time() - start_time, 2)
        result = {
            "success": False,
            "error": last_error,
            "attempts": max_retries + 1,
            "elapsed": elapsed,
            "log": self.log
        }
        self._save_log()
        return result

    def _save_log(self):
        if self.log_path:
            self.log_path.write_text(
                json.dumps(self.log, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )


def retry_on(error_type: str, log_dir: str = None):
    """装饰器：自动重试

    Usage:
        @retry_on("api_timeout")
        def call_api():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            manager = RetryManager(
                log_path=Path(log_dir) / f"retry_{error_type}.json" if log_dir else None
            )
            result = manager.execute(fn, error_type, *args, **kwargs)
            if not result["success"]:
                raise RuntimeError(
                    f"{fn.__name__} 失败（{error_type}），"
                    f"已重试 {result['attempts']} 次: {result['error']}"
                )
            return result["result"]
        return wrapper
    return decorator


# ── 便捷函数 ──

def handle_api_timeout(fn: Callable, *args, **kwargs):
    """处理 API 超时"""
    mgr = RetryManager()
    return mgr.execute(fn, "api_timeout", *args, **kwargs)


def handle_ebay_403(fn: Callable, *args, **kwargs):
    """处理 eBay 403（切节点后重试）"""
    # 切节点由调用方在 pre_action 中处理，这里只负责重试逻辑
    mgr = RetryManager()
    return mgr.execute(fn, "ebay_403", *args, **kwargs)


def handle_image_validation_fail(fn: Callable, *args, **kwargs):
    """图片验证失败时降低 strength 重试"""
    mgr = RetryManager()
    return mgr.execute(fn, "image_validation_fail", *args, **kwargs)


if __name__ == "__main__":
    # 演示
    def flaky_api():
        if random.random() < 0.6:
            raise TimeoutError("API 超时")
        return "OK"

    mgr = RetryManager()
    res = mgr.execute(flaky_api, "api_timeout")
    print(json.dumps(res, ensure_ascii=False, indent=2))
