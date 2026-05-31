"""进一步压缩：去空白行 + 压缩CSS"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

HTML = 'C:/Users/Hardy/ai-projects/新品复盘/新品板块_5.21-5.27.html'
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

before = len(html)

# 1. 压缩CSS: 去注释和多余空白
css_m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if css_m:
    css = css_m.group(1)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    css = re.sub(r'\n\s*\n', '\n', css)
    css = re.sub(r';\s+', ';', css)
    css = re.sub(r'\s*{\s*', '{', css)
    css = re.sub(r'\s*}\s*', '}', css)
    html = html[:css_m.start(1)] + css + html[css_m.end(1):]

# 2. 压缩JS渲染代码（保留数据块紧凑格式）: 去掉连续空行
script_m = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script_m:
    js = script_m.group(1)
    # 去掉3个以上连续空行
    js = re.sub(r'\n{3,}', '\n\n', js)
    html = html[:script_m.start(1)] + js + html[script_m.end(1):]

# 3. 去掉HTML body中的注释
body_m = re.search(r'<body>(.*?)<script>', html, re.DOTALL)
if body_m:
    body = body_m.group(1)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    body = re.sub(r'\n{3,}', '\n\n', body)
    html = html[:body_m.start(1)] + body + html[body_m.end(1):]

after = len(html)
saved = before - after
print(f"压缩前: {before:,} ({before/1024:.0f}KB)")
print(f"压缩后: {after:,} ({after/1024:.0f}KB)")
print(f"节省: {saved:,} ({saved/1024:.0f}KB, {saved/before*100:.1f}%)")

# 验证
new_js = re.search(r'<script>(.*?)</script>', html, re.DOTALL).group(1)
op = new_js.count('(') - new_js.count(')')
ob = new_js.count('{') - new_js.count('}')
if op != 0 or ob != 0:
    print(f"ERROR: 括号不平衡 ()={op} {{}}={ob}")
else:
    print("括号平衡 OK")
    with open(HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print("保存完成!")
