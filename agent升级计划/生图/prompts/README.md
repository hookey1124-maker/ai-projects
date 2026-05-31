# Prompt 管理规范

## 目录结构

```
prompts/
├── image/              # 生图 Prompt
│   ├── main_product_v1.json       # V1 白底主图（历史参考）
│   ├── scene_v1.json              # V1 场景图（历史参考）
│   ├── detail_v1.json             # V1 细节图（历史参考）
│   ├── main_product_v2.json       # V2 产品主图（非白底/场景化）
│   ├── fitment_v2.json            # V2 适配信息图
│   ├── install_v2.json            # V2 安装效果图
│   ├── selling_points_v2.json     # V2 卖点可视化图
│   ├── detail_v2.json             # V2 细节特写图
│   └── shipping_v2.json           # V2 发货售后图
├── copywriting/        # 文案 Prompt
│   ├── title_v1.json
│   └── description_v1.json
├── validation/         # 验证 Prompt
│   ├── image_check_v1.json
│   └── listing_check_v1.json
└── README.md
```

## 规则

1. **所有 Prompt 必须版本化。** 修改 Prompt 时递增版本号（如 `v1` → `v2`），新建文件而非覆盖旧文件。
2. **每个 Prompt 文件固定包含：** `prompt_id`、`version`、`purpose`、`last_updated`、`model`、`template`、`variables`、`constraints`。
3. **禁止 Prompt 写死在代码里。** 代码从 Prompt Registry 读取，不硬编码模板字符串。
4. **Prompt 变更必须记录目的和影响范围。**
5. **validation/ 目录下的 Prompt 供 verification/ 模块读取使用。**

## 如何使用

```python
import json

def load_prompt(prompt_id: str) -> dict:
    """从 Prompt Registry 加载 Prompt"""
    # 遍历 prompts/ 子目录查找匹配的 prompt_id
    import glob
    for f in glob.glob("prompts/**/*.json", recursive=True):
        data = json.load(open(f, encoding="utf-8"))
        if data.get("prompt_id") == prompt_id:
            return data
    raise FileNotFoundError(f"Prompt {prompt_id} not found")

prompt = load_prompt("IMG_MAIN_V1")
filled = prompt["template"].format(
    product_description="4个金属门铰链",
    background_description="浅色橡木桌面"
)
```

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-24 | V2 | 重构6张套图类型（产品主图/适配图/安装图/卖点图/细节图/发货图），Prompt 由 DeepSeek (prompt_builder.py) 动态生成，不再使用硬编码模板 |
| 2026-05-23 | V1 | 初始版本，包含 6 个 Prompt（3 生图 + 2 文案 + 1 验证）|

## V2 架构说明

V2 中 Prompt 不再由 Python 硬编码模板生成，而是由 `生图/prompt_builder.py` 调用 DeepSeek API 动态生成。JSON 注册表文件（*_v2.json）用于记录各类型的 schema、约束条件和用途描述，作为文档和参考。

V1 JSON 文件保留不动，作为历史参考。
