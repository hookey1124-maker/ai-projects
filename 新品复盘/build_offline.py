"""
构建离线版 HTML — 将 Chart.js + SheetJS CDN 内嵌到 HTML 中
"""
import sys, io, urllib.request, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKDIR = 'c:/Users/Administrator/Desktop/AI项目/新品复盘/'
INPUT = WORKDIR + '新品板块_clean.html'
OUTPUT = WORKDIR + '新品板块_离线版.html'

print("读取 HTML...")
with open(INPUT, 'r', encoding='utf-8') as f:
    html = f.read()

# CDN URLs in the HTML
CDNS = {
    'https://cdn.sheetjs.com/xlsx-0.20.0/package/dist/xlsx.full.min.js': 'SheetJS',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js': 'Chart.js',
}

for url, name in CDNS.items():
    print(f"下载 {name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            js_content = resp.read().decode('utf-8')
        # Replace CDN <script src="..."> with inline <script>...</script>
        html = html.replace(
            f'<script src="{url}"></script>',
            f'<script>/* {name} inlined */\n{js_content}\n</script>'
        )
        print(f"  {name}: {len(js_content)} chars ✅")
    except Exception as e:
        print(f"  {name}: FAILED - {e}")
        print("  保留 CDN 引用")

# Update title
html = html.replace('<title>新品周报看板</title>', '<title>新品周报看板（离线版）</title>')

print(f"\n写入 {OUTPUT}...")
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = len(html) / 1024
print(f"✅ 离线版已生成: {OUTPUT}")
print(f"   文件大小: {size_kb:.0f} KB")
