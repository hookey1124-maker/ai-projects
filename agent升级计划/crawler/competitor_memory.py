"""Competitor Memory — SQLite 缓存，复合 key + TTL + checksum

schema:
  validated_listings: 已验证通过的竞品
  rejected_listings:  被拒竞品（记录原因）
"""
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "competitor_memory.db"
DEFAULT_TTL_DAYS = 14


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")  # 支持并发读
    return conn


def init_db():
    """初始化表结构"""
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS validated_listings (
            item_id TEXT NOT NULL,
            anchor_family TEXT NOT NULL,
            product_type TEXT NOT NULL,
            cab TEXT NOT NULL DEFAULT '',
            similarity REAL,
            validated_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            checksum TEXT,
            PRIMARY KEY (item_id, anchor_family, product_type, cab)
        );

        CREATE TABLE IF NOT EXISTS rejected_listings (
            item_id TEXT NOT NULL,
            anchor_family TEXT NOT NULL,
            product_type TEXT NOT NULL,
            cab TEXT NOT NULL DEFAULT '',
            reject_reason TEXT,
            rejected_at TEXT NOT NULL,
            PRIMARY KEY (item_id, anchor_family, product_type, cab)
        );
    """)
    conn.commit()
    conn.close()


def _make_key(item_id: str, anchor_family: str, product_type: str, cab: str = "") -> dict:
    return {"item_id": item_id, "anchor_family": anchor_family,
            "product_type": product_type, "cab": cab or ""}


def lookup_validated(item_id: str, anchor_family: str, product_type: str, cab: str = "") -> dict | None:
    """查询已缓存的验证结果。返回 dict 或 None"""
    conn = _connect()
    row = conn.execute(
        "SELECT similarity, validated_at, expires_at, checksum FROM validated_listings "
        "WHERE item_id=? AND anchor_family=? AND product_type=? AND cab=?",
        (item_id, anchor_family, product_type, cab or "")
    ).fetchone()
    conn.close()
    if not row:
        return None

    similarity, validated_at, expires_at, checksum = row
    # 检查过期
    if expires_at < datetime.now().isoformat():
        return None
    return {
        "item_id": item_id,
        "similarity": similarity,
        "validated_at": validated_at,
        "expires_at": expires_at,
        "checksum": checksum,
    }


def lookup_rejected(item_id: str, anchor_family: str, product_type: str, cab: str = "") -> dict | None:
    """查询是否已被拒过"""
    conn = _connect()
    row = conn.execute(
        "SELECT reject_reason, rejected_at FROM rejected_listings "
        "WHERE item_id=? AND anchor_family=? AND product_type=? AND cab=?",
        (item_id, anchor_family, product_type, cab or "")
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"item_id": item_id, "reject_reason": row[0], "rejected_at": row[1]}


def save_validated(item_id: str, anchor_family: str, product_type: str, cab: str = "",
                   similarity: float = 0.0, checksum: str = ""):
    """保存通过验证的竞品"""
    now = datetime.now()
    expires = now + timedelta(days=DEFAULT_TTL_DAYS)
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO validated_listings "
        "(item_id, anchor_family, product_type, cab, similarity, validated_at, expires_at, checksum) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (item_id, anchor_family, product_type, cab or "", similarity,
         now.isoformat(), expires.isoformat(), checksum)
    )
    conn.commit()
    conn.close()


def save_rejected(item_id: str, anchor_family: str, product_type: str, cab: str = "",
                  reason: str = ""):
    """保存被拒竞品"""
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO rejected_listings "
        "(item_id, anchor_family, product_type, cab, reject_reason, rejected_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (item_id, anchor_family, product_type, cab or "", reason, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def compute_checksum(title: str, price: str = "") -> str:
    """计算 listing 内容 checksum，用于检测变更"""
    raw = f"{title}|{price}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def validate_or_skip(item_id: str, title: str, price: str,
                     anchor_family: str, product_type: str, cab: str = "") -> str:
    """检查是否可跳过验证。

    Returns:
        "skip_valid" — 已验证且未过期且 checksum 匹配 → 跳过
        "skip_rejected" — 已被拒过 → 跳过
        "validate" — 需要重新验证
    """
    validated = lookup_validated(item_id, anchor_family, product_type, cab)
    if validated:
        current_checksum = compute_checksum(title, price)
        if validated["checksum"] == current_checksum:
            return "skip_valid"
        # checksum 变了（listing 内容已修改），需要重新验证
        # 删除旧记录，让流程重新走
        conn = _connect()
        conn.execute(
            "DELETE FROM validated_listings WHERE item_id=? AND anchor_family=? AND product_type=? AND cab=?",
            (item_id, anchor_family, product_type, cab or "")
        )
        conn.commit()
        conn.close()

    rejected = lookup_rejected(item_id, anchor_family, product_type, cab)
    if rejected:
        return "skip_rejected"

    return "validate"


# 启动时自动初始化
init_db()
