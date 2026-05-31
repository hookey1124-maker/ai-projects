"""market.db — SQLite 持久化层

7 表结构：
  own_products        — 锚定产品
  competitor_listings — 竞品列表
  relationships       — 锚定↔竞品关联
  price_snapshots     — 价格历史
  crawl_jobs          — 爬取任务
  canonical_snapshots — 规范化快照
  ruleset_version     — 规则集版本

用法:
  from crawler.database import MarketDB
  db = MarketDB()                        # 默认 data/market.db
  db.init_tables()                       # 建表（幂等）
  db.upsert_own_product(...)
  db.link_competitor(own_id, comp_id, ...)
"""

import re
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

_DEFAULT_PATH = Path(__file__).parent.parent / "data" / "market.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS own_products (
    id              TEXT PRIMARY KEY,                  -- eBay item ID
    sku             TEXT NOT NULL,
    title           TEXT,
    url             TEXT,
    price           REAL,
    position        TEXT,
    finish          TEXT,
    structure       TEXT,
    sub_type        TEXT,
    material        TEXT,
    count           TEXT,
    cab             TEXT,
    bed_length      TEXT,
    vehicle_json    TEXT,                              -- {makes:[], models:[], years:[]}
    image_path      TEXT,
    classification_json TEXT,
    first_seen      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS competitor_listings (
    id              TEXT PRIMARY KEY,                  -- eBay item ID
    title           TEXT,
    url             TEXT,
    price           REAL,
    currency        TEXT DEFAULT 'USD',
    seller          TEXT,
    seller_url      TEXT,
    seller_feedback TEXT,
    seller_feedback_pct TEXT,
    position        TEXT,
    finish          TEXT,
    structure       TEXT,
    sub_type        TEXT,
    material        TEXT,
    count           TEXT,
    cab             TEXT,
    bed_length      TEXT,
    vehicle_json    TEXT,
    image_path      TEXT,
    image_count     INTEGER,
    description_text TEXT,
    compatibility_json TEXT,
    specs_json      TEXT,
    oe_numbers_json TEXT,                              -- [oe1, oe2, ...]
    classification_json TEXT,
    shipping_json   TEXT,                              -- {cost, service, location}
    condition       TEXT,
    first_seen      TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS relationships (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    own_product_id  TEXT NOT NULL REFERENCES own_products(id),
    competitor_id   TEXT NOT NULL REFERENCES competitor_listings(id),
    similarity      REAL,
    final_status    TEXT NOT NULL DEFAULT 'pending',   -- approved/borderline/rejected/pending
    raw_score       REAL,
    max_score       REAL,
    coverage        REAL,
    breakdown_json  TEXT,
    filter_result_json TEXT,
    vision_diff_json   TEXT,
    hard_reject_reason  TEXT,                          -- e.g. "count不同: anchor=2, competitor=4"
    is_new          INTEGER DEFAULT 1,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(own_product_id, competitor_id)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id      TEXT NOT NULL,
    listing_type    TEXT NOT NULL CHECK(listing_type IN ('own','competitor')),
    price           REAL NOT NULL,
    currency        TEXT DEFAULT 'USD',
    snapped_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_price_listing ON price_snapshots(listing_id, snapped_at);

CREATE TABLE IF NOT EXISTS crawl_jobs (
    id              TEXT PRIMARY KEY,                  -- UUID or timestamp slug
    sku             TEXT,
    mother_dir      TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',   -- pending/running/done/failed
    phase           TEXT,                              -- search/scrape/analyze
    total_candidates INTEGER DEFAULT 0,
    valid_count     INTEGER DEFAULT 0,
    excluded_count  INTEGER DEFAULT 0,
    borderline_count INTEGER DEFAULT 0,
    vision_enabled  INTEGER DEFAULT 0,
    error_log       TEXT,
    config_json     TEXT,                              -- snapshot of key config
    started_at      TEXT,
    finished_at     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS canonical_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id      TEXT NOT NULL,
    listing_type    TEXT NOT NULL CHECK(listing_type IN ('own','competitor')),
    classification_json TEXT NOT NULL,
    parser_version  TEXT,
    ruleset_version TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_canon_listing ON canonical_snapshots(listing_id, created_at);

CREATE TABLE IF NOT EXISTS ruleset_version (
    version         TEXT PRIMARY KEY,                  -- e.g. "2026-05-29-a"
    description     TEXT,
    config_snapshot_json TEXT,                         -- frozen config at this version
    is_active       INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _parse_price(price_str: str) -> float | None:
    """从价格字符串提取数字。"""
    if not price_str:
        return None
    m = re.search(r'[\d,]+\.?\d*', str(price_str))
    if m:
        return float(m.group().replace(",", ""))
    return None


class MarketDB:
    """market.db 操作封装，单连接 + 自动重试。"""

    def __init__(self, path: str | Path = None):
        self._path = str(path or _DEFAULT_PATH)
        self._conn: sqlite3.Connection | None = None

    # ── lifecycle ──────────────────────────────────────

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._path)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def init_tables(self):
        """幂等建表"""
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ── helpers ────────────────────────────────────────

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _j(v: Any) -> str | None:
        """Encode as JSON string, or None if empty."""
        if v is None:
            return None
        if isinstance(v, str):
            return v
        return json.dumps(v, ensure_ascii=False)

    @staticmethod
    def _jload(s: str | None) -> Any:
        if not s:
            return None
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            return s

    @staticmethod
    def _extract_vehicle_json(classification: dict) -> str | None:
        """Extract vehicle info from classification dict into JSON string."""
        v = classification.get("vehicle", {})
        if isinstance(v, dict):
            val = v.get("value", v)
            if isinstance(val, dict):
                return MarketDB._j(val)
        return MarketDB._j(v) if v else None

    @staticmethod
    def _pick_cls_field(classification: dict, field: str) -> str | None:
        v = classification.get(field, {})
        if isinstance(v, dict):
            val = v.get("value")
            if val and val != "Unknown":
                return val
        return None

    # ── own_products ───────────────────────────────────

    def upsert_own_product(self, item_id: str, sku: str, title: str = None,
                           url: str = None, price: float = None,
                           classification: dict = None,
                           image_path: str = None) -> None:
        """插入或更新锚定产品。"""
        cls = classification or {}
        self.conn.execute("""
            INSERT INTO own_products (id, sku, title, url, price,
                position, finish, structure, sub_type, material, count,
                cab, bed_length, vehicle_json, image_path, classification_json,
                first_seen, updated_at)
            VALUES (?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title, url=excluded.url, price=excluded.price,
                position=excluded.position, finish=excluded.finish,
                structure=excluded.structure, sub_type=excluded.sub_type,
                material=excluded.material, count=excluded.count,
                cab=excluded.cab, bed_length=excluded.bed_length,
                vehicle_json=excluded.vehicle_json,
                image_path=excluded.image_path,
                classification_json=excluded.classification_json,
                updated_at=excluded.updated_at
        """, (
            item_id, sku, title, url, price,
            self._pick_cls_field(cls, "position"),
            self._pick_cls_field(cls, "finish"),
            self._pick_cls_field(cls, "structure"),
            self._pick_cls_field(cls, "sub_type"),
            self._pick_cls_field(cls, "material"),
            self._pick_cls_field(cls, "count"),
            self._pick_cls_field(cls, "cab"),
            self._pick_cls_field(cls, "bed_length"),
            self._extract_vehicle_json(cls),
            image_path,
            self._j(cls),
            self._now(), self._now(),
        ))
        self.conn.commit()

    def get_own_product(self, item_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM own_products WHERE id=?", (item_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_own_products(self) -> list[dict]:
        return [dict(r) for r in
                self.conn.execute("SELECT * FROM own_products ORDER BY updated_at DESC").fetchall()]

    # ── competitor_listings ────────────────────────────

    def upsert_competitor(self, item_id: str, title: str = None,
                          url: str = None, price: float = None,
                          currency: str = "USD", seller: str = None,
                          seller_url: str = None, seller_feedback: str = None,
                          seller_feedback_pct: str = None,
                          classification: dict = None,
                          image_path: str = None, image_count: int = None,
                          description_text: str = None,
                          compatibility: list = None,
                          specs: dict = None,
                          oe_numbers: list = None,
                          shipping: dict = None,
                          condition: str = None) -> None:
        """插入或更新竞品 listing。"""
        cls = classification or {}
        self.conn.execute("""
            INSERT INTO competitor_listings (id, title, url, price, currency,
                seller, seller_url, seller_feedback, seller_feedback_pct,
                position, finish, structure, sub_type, material, count,
                cab, bed_length, vehicle_json, image_path, image_count,
                description_text, compatibility_json, specs_json,
                oe_numbers_json, classification_json, shipping_json,
                condition, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title, url=excluded.url, price=excluded.price,
                currency=excluded.currency,
                seller=excluded.seller, seller_url=excluded.seller_url,
                seller_feedback=excluded.seller_feedback,
                seller_feedback_pct=excluded.seller_feedback_pct,
                position=excluded.position, finish=excluded.finish,
                structure=excluded.structure, sub_type=excluded.sub_type,
                material=excluded.material, count=excluded.count,
                cab=excluded.cab, bed_length=excluded.bed_length,
                vehicle_json=excluded.vehicle_json,
                image_path=excluded.image_path,
                image_count=excluded.image_count,
                description_text=excluded.description_text,
                compatibility_json=excluded.compatibility_json,
                specs_json=excluded.specs_json,
                oe_numbers_json=excluded.oe_numbers_json,
                classification_json=excluded.classification_json,
                shipping_json=excluded.shipping_json,
                condition=excluded.condition,
                last_seen=excluded.last_seen
        """, (
            item_id, title, url, price, currency,
            seller, seller_url, seller_feedback, seller_feedback_pct,
            self._pick_cls_field(cls, "position"),
            self._pick_cls_field(cls, "finish"),
            self._pick_cls_field(cls, "structure"),
            self._pick_cls_field(cls, "sub_type"),
            self._pick_cls_field(cls, "material"),
            self._pick_cls_field(cls, "count"),
            self._pick_cls_field(cls, "cab"),
            self._pick_cls_field(cls, "bed_length"),
            self._extract_vehicle_json(cls),
            image_path, image_count,
            description_text,
            self._j(compatibility),
            self._j(specs),
            self._j(oe_numbers),
            self._j(cls),
            self._j(shipping),
            condition,
            self._now(), self._now(),
        ))
        self.conn.commit()

    def get_competitor(self, item_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM competitor_listings WHERE id=?", (item_id,)
        ).fetchone()
        return dict(row) if row else None

    def competitor_exists(self, item_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM competitor_listings WHERE id=?", (item_id,)
        ).fetchone()
        return row is not None

    # ── relationships ──────────────────────────────────

    def link_competitor(self, own_product_id: str, competitor_id: str,
                        similarity: float = None, final_status: str = "pending",
                        raw_score: float = None, max_score: float = None,
                        coverage: float = None,
                        breakdown: dict = None,
                        filter_result: dict = None,
                        vision_diff: dict = None,
                        hard_reject_reason: str = None,
                        is_new: bool = True) -> None:
        """建立/更新锚定↔竞品关联。"""
        self.conn.execute("""
            INSERT INTO relationships (own_product_id, competitor_id,
                similarity, final_status, raw_score, max_score, coverage,
                breakdown_json, filter_result_json, vision_diff_json,
                hard_reject_reason, is_new, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(own_product_id, competitor_id) DO UPDATE SET
                similarity=excluded.similarity,
                final_status=excluded.final_status,
                raw_score=excluded.raw_score,
                max_score=excluded.max_score,
                coverage=excluded.coverage,
                breakdown_json=excluded.breakdown_json,
                filter_result_json=excluded.filter_result_json,
                vision_diff_json=excluded.vision_diff_json,
                hard_reject_reason=excluded.hard_reject_reason,
                is_new=excluded.is_new,
                updated_at=excluded.updated_at
        """, (
            own_product_id, competitor_id,
            similarity, final_status, raw_score, max_score, coverage,
            self._j(breakdown), self._j(filter_result), self._j(vision_diff),
            hard_reject_reason, int(is_new),
            self._now(), self._now(),
        ))
        self.conn.commit()

    def get_relationship(self, own_id: str, comp_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM relationships WHERE own_product_id=? AND competitor_id=?",
            (own_id, comp_id)
        ).fetchone()
        return dict(row) if row else None

    def list_competitors_for(self, own_product_id: str,
                             status: str = None) -> list[dict]:
        """查某个锚定产品的所有竞品关联。"""
        q = """
            SELECT r.*, c.title, c.url, c.price, c.seller
            FROM relationships r
            LEFT JOIN competitor_listings c ON r.competitor_id = c.id
            WHERE r.own_product_id = ?
        """
        params: list = [own_product_id]
        if status:
            q += " AND r.final_status = ?"
            params.append(status)
        q += " ORDER BY r.similarity DESC"
        return [dict(r) for r in self.conn.execute(q, params).fetchall()]

    def count_by_status(self, own_product_id: str) -> dict[str, int]:
        rows = self.conn.execute("""
            SELECT final_status, COUNT(*) as cnt
            FROM relationships
            WHERE own_product_id = ?
            GROUP BY final_status
        """, (own_product_id,)).fetchall()
        return {r["final_status"]: r["cnt"] for r in rows}

    # ── price_snapshots ────────────────────────────────

    def snap_price(self, listing_id: str, price: float,
                   listing_type: str = "competitor",
                   currency: str = "USD") -> None:
        """记录一次价格快照。仅当前价与最近一次不同时才写入。"""
        last = self.conn.execute("""
            SELECT price FROM price_snapshots
            WHERE listing_id=? AND listing_type=?
            ORDER BY snapped_at DESC LIMIT 1
        """, (listing_id, listing_type)).fetchone()
        if last and abs(last["price"] - price) < 0.01:
            return  # price unchanged
        self.conn.execute("""
            INSERT INTO price_snapshots (listing_id, listing_type, price, currency)
            VALUES (?, ?, ?, ?)
        """, (listing_id, listing_type, price, currency))
        self.conn.commit()

    def get_price_history(self, listing_id: str,
                          listing_type: str = "competitor") -> list[dict]:
        return [dict(r) for r in self.conn.execute("""
            SELECT * FROM price_snapshots
            WHERE listing_id=? AND listing_type=?
            ORDER BY snapped_at DESC
        """, (listing_id, listing_type)).fetchall()]

    # ── crawl_jobs ─────────────────────────────────────

    def create_crawl_job(self, job_id: str, sku: str = None,
                         mother_dir: str = None,
                         config: dict = None) -> None:
        self.conn.execute("""
            INSERT INTO crawl_jobs (id, sku, mother_dir, status, config_json, created_at)
            VALUES (?, ?, ?, 'pending', ?, ?)
        """, (job_id, sku, mother_dir, self._j(config), self._now()))
        self.conn.commit()

    def update_crawl_job(self, job_id: str, **kwargs) -> None:
        """更新爬取任务字段。支持 status/phase/counts/error_log 等。"""
        allowed = {"status", "phase", "total_candidates", "valid_count",
                   "excluded_count", "borderline_count", "vision_enabled",
                   "error_log", "started_at", "finished_at"}
        sets = []
        vals = []
        for k, v in kwargs.items():
            if k in allowed:
                sets.append(f"{k}=?")
                vals.append(v)
        if not sets:
            return
        vals.append(job_id)
        self.conn.execute(
            f"UPDATE crawl_jobs SET {', '.join(sets)} WHERE id=?", vals
        )
        self.conn.commit()

    def start_job(self, job_id: str) -> None:
        self.update_crawl_job(job_id, status="running", started_at=self._now())

    def finish_job(self, job_id: str, success: bool = True,
                   error: str = None) -> None:
        self.update_crawl_job(
            job_id,
            status="done" if success else "failed",
            error_log=error,
            finished_at=self._now(),
        )

    def get_crawl_job(self, job_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM crawl_jobs WHERE id=?", (job_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_recent_jobs(self, limit: int = 20) -> list[dict]:
        return [dict(r) for r in self.conn.execute(
            "SELECT * FROM crawl_jobs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()]

    # ── canonical_snapshots ────────────────────────────

    def snap_classification(self, listing_id: str, classification: dict,
                            listing_type: str = "competitor",
                            parser_version: str = None,
                            ruleset_version: str = None) -> None:
        self.conn.execute("""
            INSERT INTO canonical_snapshots (listing_id, listing_type,
                classification_json, parser_version, ruleset_version)
            VALUES (?, ?, ?, ?, ?)
        """, (listing_id, listing_type, self._j(classification),
              parser_version, ruleset_version))
        self.conn.commit()

    def get_latest_classification(self, listing_id: str) -> dict | None:
        row = self.conn.execute("""
            SELECT * FROM canonical_snapshots
            WHERE listing_id=? ORDER BY created_at DESC LIMIT 1
        """, (listing_id,)).fetchone()
        if row:
            d = dict(row)
            d["classification"] = self._jload(d.get("classification_json"))
            return d
        return None

    # ── ruleset_version ────────────────────────────────

    def register_ruleset(self, version: str, description: str = None,
                         config_snapshot: dict = None) -> None:
        """注册新规则集版本，旧版本自动 deactivate。"""
        self.conn.execute(
            "UPDATE ruleset_version SET is_active=0 WHERE is_active=1"
        )
        self.conn.execute("""
            INSERT INTO ruleset_version (version, description, config_snapshot_json, is_active)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(version) DO UPDATE SET is_active=1, description=excluded.description
        """, (version, description, self._j(config_snapshot)))
        self.conn.commit()

    def get_active_ruleset(self) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM ruleset_version WHERE is_active=1 ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    # ── 复合查询 ───────────────────────────────────────

    def cache_hit(self, item_id: str, anchor_family: str,
                  product_type: str, cab: str) -> dict | None:
        """复合 key 缓存命中检查（competitor_memory 适配）。"""
        row = self.conn.execute("""
            SELECT r.*, c.classification_json
            FROM relationships r
            JOIN competitor_listings c ON r.competitor_id = c.id
            WHERE r.competitor_id = ?
        """, (item_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["classification"] = self._jload(d.get("classification_json"))
        return d

    def is_known_competitor(self, item_id: str,
                            own_product_id: str = None) -> bool:
        """检查 item 是否已被任何锚定产品收录为竞品。"""
        q = "SELECT 1 FROM relationships WHERE competitor_id=?"
        params: list = [item_id]
        if own_product_id:
            q += " AND own_product_id=?"
            params.append(own_product_id)
        return self.conn.execute(q, params).fetchone() is not None

    def mark_not_new(self, own_product_id: str) -> None:
        """将某锚定产品的所有关联标记为非新增（用于去重新旧比较）。"""
        self.conn.execute("""
            UPDATE relationships SET is_new=0
            WHERE own_product_id=?
        """, (own_product_id,))
        self.conn.commit()

    # ── 批量导入（从 market_intel 结构）───────────────

    def ingest_analysis(self, mother_dir: str, sku: str,
                        product_data: list[dict],
                        source_links: list[dict],
                        market_intel: dict,
                        vision_enabled: bool = False) -> str:
        """将整次分析结果写入 market.db。

        Args:
            mother_dir: 母目录路径
            sku: SKU 名
            product_data: 所有 product_*.json 数据列表
            source_links: source_links.json 中的 links 数组
            market_intel: analyze() 返回的 market_intel dict
            vision_enabled: 是否启用了视觉模块

        Returns:
            crawl_job_id
        """
        job_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.create_crawl_job(job_id, sku=sku, mother_dir=mother_dir)
        self.start_job(job_id)

        # 识别锚点
        anchor_ids = set()
        for link in (source_links or []):
            if link.get("anchor"):
                m = re.search(r'/itm/(\d+)', link.get("url", ""))
                if m:
                    anchor_ids.add(m.group(1))

        classifications = {
            c["item_id"]: c["classification"]
            for c in market_intel.get("product_classifications", [])
        }
        anchor_analysis = market_intel.get("anchor_analysis", {})
        excluded_list = anchor_analysis.get("rule0_excluded", [])

        # 构建 excluded_map
        excluded_map = {}
        for ex in excluded_list:
            url = ex.get("competitor_url", "")
            m = re.search(r'/itm/(\d+)', url)
            if m:
                excluded_map[m.group(1)] = ex

        total_candidates = 0
        valid_count = 0
        excluded_count = 0

        for p in product_data:
            item_id = p.get("item_id", "")
            if not item_id:
                continue
            cls = classifications.get(item_id, {})
            is_anchor = item_id in anchor_ids

            if is_anchor:
                # ── 锚定产品 ──
                self.upsert_own_product(
                    item_id=item_id,
                    sku=sku,
                    title=p.get("title", ""),
                    url=p.get("url", ""),
                    price=_parse_price(p.get("price", "")),
                    classification=cls,
                    image_path=p.get("image_path", ""),
                )
                self.snap_classification(item_id, cls, "own")
                self.snap_price(item_id, _parse_price(p.get("price", "")) or 0, "own")
            else:
                # ── 竞品 listing ──
                total_candidates += 1
                self.upsert_competitor(
                    item_id=item_id,
                    title=p.get("title", ""),
                    url=p.get("url", ""),
                    price=_parse_price(p.get("price", "")),
                    seller=p.get("seller", ""),
                    seller_url=p.get("sellerUrl", ""),
                    seller_feedback=str(p.get("sellerFeedback", "")),
                    seller_feedback_pct=str(p.get("sellerFeedbackPct", "")),
                    classification=cls,
                    image_path=p.get("image_path", ""),
                    image_count=p.get("imageCount"),
                    description_text=p.get("description_text", ""),
                    compatibility=p.get("compatibility", []),
                    specs=p.get("specs", {}),
                    oe_numbers=p.get("oe_numbers"),
                    shipping=p.get("shipping"),
                    condition=p.get("condition", ""),
                )
                self.snap_classification(item_id, cls, "competitor")
                self.snap_price(item_id, _parse_price(p.get("price", "")) or 0, "competitor")

                # ── 关联 ──
                for aid in anchor_ids:
                    # 获取 filter/score 信息
                    sim_info = {}
                    for c in market_intel.get("product_classifications", []):
                        if c["item_id"] == item_id:
                            sim_info = c.get("_similarity_info", {})
                            break

                    if item_id in excluded_map:
                        ex = excluded_map[item_id]
                        self.link_competitor(
                            own_product_id=aid,
                            competitor_id=item_id,
                            similarity=0.0,
                            final_status="rejected",
                            hard_reject_reason=(
                                f"{ex.get('field', 'unknown')}: "
                                f"{ex.get('reason', '')}"
                            ),
                            filter_result=ex,
                        )
                        excluded_count += 1
                    else:
                        status = sim_info.get("final_status", "approved")
                        self.link_competitor(
                            own_product_id=aid,
                            competitor_id=item_id,
                            similarity=sim_info.get("similarity"),
                            final_status=status,
                            raw_score=sim_info.get("raw_score"),
                            max_score=sim_info.get("max_score"),
                            coverage=sim_info.get("coverage"),
                            breakdown=sim_info.get("breakdown"),
                            filter_result=sim_info.get("filter_result"),
                            vision_diff=sim_info.get("_vision_diff"),
                        )
                        if status == "approved":
                            valid_count += 1

        # 更新 job 统计
        self.update_crawl_job(
            job_id,
            total_candidates=total_candidates,
            valid_count=valid_count,
            excluded_count=excluded_count,
            borderline_count=market_intel.get("anchor_analysis", {}).get("borderline_count", 0),
            vision_enabled=int(vision_enabled),
        )
        self.finish_job(job_id)
        return job_id


    # ── 统计 ───────────────────────────────────────────

    def stats(self) -> dict:
        """返回库级概览统计。"""
        return {
            "own_products": self.conn.execute("SELECT COUNT(*) FROM own_products").fetchone()[0],
            "competitors": self.conn.execute("SELECT COUNT(*) FROM competitor_listings").fetchone()[0],
            "relationships": self.conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0],
            "approved": self.conn.execute(
                "SELECT COUNT(*) FROM relationships WHERE final_status='approved'"
            ).fetchone()[0],
            "rejected": self.conn.execute(
                "SELECT COUNT(*) FROM relationships WHERE final_status='rejected'"
            ).fetchone()[0],
            "borderline": self.conn.execute(
                "SELECT COUNT(*) FROM relationships WHERE final_status='borderline'"
            ).fetchone()[0],
            "price_snapshots": self.conn.execute("SELECT COUNT(*) FROM price_snapshots").fetchone()[0],
            "crawl_jobs": self.conn.execute("SELECT COUNT(*) FROM crawl_jobs").fetchone()[0],
            "active_ruleset": (self.get_active_ruleset() or {}).get("version", "none"),
        }


# ── bootstrap ──────────────────────────────────────────

if __name__ == "__main__":
    db = MarketDB()
    db.init_tables()
    s = db.stats()
    print("market.db initialized successfully")
    for k, v in s.items():
        print(f"  {k}: {v}")
