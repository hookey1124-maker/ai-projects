"""JSON Schema 校验 — 确保所有模块输出符合规范"""
import json
from pathlib import Path


# ── 产品信息 Schema ──
PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["title", "item_id", "price", "images"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "item_id": {"type": "string", "pattern": "^[0-9]{8,}$"},
        "price": {"type": "string", "minLength": 1},
        "condition": {"type": "string"},
        "seller": {"type": "string"},
        "sellerUrl": {"type": "string"},
        "images": {"type": "array", "minItems": 1},
        "specs": {"type": "object"},
        "compatibility": {"type": "array"},
        "scraped_at": {"type": "string"},
        "url": {"type": "string"}
    }
}

# ── 图片验证结果 Schema ──
IMAGE_VALIDATION_SCHEMA = {
    "type": "object",
    "required": ["passed", "action", "structure_changed", "logo_detected"],
    "properties": {
        "product_count_match": {"type": "boolean"},
        "structure_changed": {"type": "boolean"},
        "missing_parts": {"type": "boolean"},
        "floating_issue": {"type": "boolean"},
        "logo_detected": {"type": "boolean"},
        "perspective_ok": {"type": "boolean"},
        "lighting_ok": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "issues": {"type": "string"},
        "passed": {"type": "boolean"},
        "action": {"type": "string", "enum": ["accept", "reject", "retry", "human_review"]},
        "reason": {"type": "string"}
    }
}

# ── 文案验证结果 Schema ──
LISTING_VALIDATION_SCHEMA = {
    "type": "object",
    "required": ["title", "bullets", "passed", "action"],
    "properties": {
        "title": {
            "type": "object",
            "required": ["length", "length_ok"],
            "properties": {
                "length": {"type": "integer"},
                "length_ok": {"type": "boolean"},
                "no_oem_logo": {"type": "boolean"},
                "no_trademark": {"type": "boolean"},
                "passed": {"type": "boolean"},
                "issues": {"type": "array"}
            }
        },
        "bullets": {
            "type": "object",
            "required": ["count", "count_ok"],
            "properties": {
                "count": {"type": "integer"},
                "count_ok": {"type": "boolean"},
                "passed": {"type": "boolean"},
                "issues": {"type": "array"}
            }
        },
        "passed": {"type": "boolean"},
        "action": {"type": "string", "enum": ["accept", "retry", "reject"]},
        "reason": {"type": "string"}
    }
}

# ── 费用记录 Schema ──
COST_RECORD_SCHEMA = {
    "type": "object",
    "required": ["product_id", "total_cost"],
    "properties": {
        "product_id": {"type": "string"},
        "glm_cost": {"type": "number"},
        "image_cost": {"type": "number"},
        "deepseek_cost": {"type": "number"},
        "total_cost": {"type": "number"},
        "timestamp": {"type": "string"}
    }
}

SCHEMAS = {
    "product": PRODUCT_SCHEMA,
    "image_validation": IMAGE_VALIDATION_SCHEMA,
    "listing_validation": LISTING_VALIDATION_SCHEMA,
    "cost_record": COST_RECORD_SCHEMA
}


def _check_type(value, schema, path="$"):
    """递归检查类型和约束"""
    issues = []
    t = schema.get("type")

    if t == "object":
        if not isinstance(value, dict):
            return [f"{path}: 应为 object，实际 {type(value).__name__}"]

        for key in schema.get("required", []):
            if key not in value:
                issues.append(f"{path}.{key}: 缺少必填字段")
            elif value[key] is None or value[key] == "":
                issues.append(f"{path}.{key}: 必填字段为空")

        for key, prop_schema in schema.get("properties", {}).items():
            if key in value and value[key] is not None:
                issues.extend(_check_type(value[key], prop_schema, f"{path}.{key}"))

    elif t == "array":
        if not isinstance(value, list):
            return [f"{path}: 应为 array，实际 {type(value).__name__}"]
        min_items = schema.get("minItems", 0)
        if len(value) < min_items:
            issues.append(f"{path}: 数组长度 {len(value)} < 最小 {min_items}")

    elif t == "string":
        if not isinstance(value, str):
            return [f"{path}: 应为 string，实际 {type(value).__name__}"]
        if "minLength" in schema and len(value) < schema["minLength"]:
            issues.append(f"{path}: 字符串长度 {len(value)} < 最小 {schema['minLength']}")
        if "pattern" in schema and not __import__("re").match(schema["pattern"], value):
            issues.append(f"{path}: '{value}' 不匹配模式 {schema['pattern']}")
        if "enum" in schema and value not in schema["enum"]:
            issues.append(f"{path}: '{value}' 不在允许值 {schema['enum']} 中")

    elif t in ("number", "integer"):
        if not isinstance(value, (int, float)):
            return [f"{path}: 应为 {t}，实际 {type(value).__name__}"]
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(f"{path}: {value} < 最小值 {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(f"{path}: {value} > 最大值 {schema['maximum']}")

    elif t == "boolean":
        if not isinstance(value, bool):
            return [f"{path}: 应为 boolean，实际 {type(value).__name__}"]

    return issues


def validate(data: dict, schema_name: str) -> dict:
    """校验数据是否符合指定 Schema

    Args:
        data: 要校验的 JSON 数据
        schema_name: Schema 名称（product/image_validation/listing_validation/cost_record）

    Returns:
        {"passed": bool, "issues": list, "schema": str}
    """
    schema = SCHEMAS.get(schema_name)
    if not schema:
        return {"passed": False, "issues": [f"未知 Schema: {schema_name}"], "schema": schema_name}

    issues = _check_type(data, schema)
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "schema": schema_name,
        "fields_checked": len(schema.get("properties", {}))
    }


def validate_file(json_path: str, schema_name: str) -> dict:
    """从文件读取 JSON 并校验"""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    return validate(data, schema_name)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python schema_validator.py <data.json> <schema_name>")
        print(f"可用 Schema: {list(SCHEMAS.keys())}")
        sys.exit(1)
    result = validate_file(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))
