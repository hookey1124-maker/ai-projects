"""压缩HTML中的JSON数据块，减少体积"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html'
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

before = len(html)
print(f"压缩前: {before:,} chars ({before/1024:.0f}KB)")

# 找到script标签
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
js = script_match.group(1)

# 分割数据块部分和渲染代码部分
data_end_marker = "// ========== Tab1: 总盘概览 =========="
if data_end_marker in js:
    idx = js.index(data_end_marker)
    data_part = js[:idx]
    code_part = js[idx:]
else:
    print("ERROR: 找不到数据/代码分界")
    sys.exit(1)

# 压缩每个const变量
def compact_const(match):
    var_name = match.group(1)
    json_str = match.group(2)
    try:
        obj = json.loads(json_str)
        compact_json = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
        return f"const {var_name} = {compact_json};"
    except:
        return match.group(0)

data_part = re.sub(r'const (\w+) = (.*?);\n', compact_const, data_part, flags=re.DOTALL)

# 重新组装
js = data_part + code_part
html = html[:script_match.start(1)] + js + html[script_match.end(1):]

after = len(html)
saved = before - after
print(f"压缩后: {after:,} chars ({after/1024:.0f}KB)")
print(f"节省: {saved:,} chars ({saved/1024:.0f}KB, {saved/before*100:.1f}%)")

# 验证括号平衡
new_js = re.search(r'<script>(.*?)</script>', html, re.DOTALL).group(1)
op = new_js.count('(') - new_js.count(')')
ob = new_js.count('{') - new_js.count('}')
print(f"Brackets: ()={op}, {{}}={ob}")
if op != 0 or ob != 0:
    print("ERROR: 括号不平衡!")
    sys.exit(1)

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("完成!")
