"""
重建 新品板块.html — 消除代码重复，确保单份计算引擎 + 单份渲染引擎
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKDIR = 'c:/Users/Administrator/Desktop/AI项目/新品复盘/'
INPUT = WORKDIR + '新品板块.html'
COMPUTE = WORKDIR + 'compute_engine.js'
RENDER = WORKDIR + 'render_dashboard.js'
OUTPUT = WORKDIR + '新品板块_clean.html'

print("读取源文件...")

# 1. 读取 CSS + HTML body (lines 1-282 of original)
with open(INPUT, 'r', encoding='utf-8') as f:
    html_lines = f.readlines()

# Find where the inline <script> starts
script_start = None
for i, line in enumerate(html_lines):
    if '<script>' in line and 'src=' not in line:
        script_start = i
        break

if script_start is None:
    print("ERROR: Could not find inline <script> tag")
    sys.exit(1)

print(f"HTML body ends at line {script_start + 1}, script starts at line {script_start + 1}")

# CSS + HTML body (everything before the inline <script>)
header = ''.join(html_lines[:script_start])

# 2. Read compute_engine.js (remove module.exports at the end)
with open(COMPUTE, 'r', encoding='utf-8') as f:
    compute_js = f.read()

# Remove the module.exports block at the end
import re
compute_js = re.sub(
    r'\n// Export for use\s*\nif \(typeof module.*?module\.exports\s*=\s*\{[^}]*\};\s*\}\s*$',
    '',
    compute_js,
    flags=re.DOTALL
)

# 3. Read render_dashboard.js (as-is, it has its own var DATA/var allCharts/destroyAllCharts)
with open(RENDER, 'r', encoding='utf-8') as f:
    render_js = f.read()

# 4. Assemble
html_output = header
html_output += '\n<script>\n'
html_output += '// ===== COMPUTATION ENGINE =====\n'
html_output += compute_js.strip() + '\n'
html_output += '\n// ===== RENDERING ENGINE =====\n'
html_output += render_js.strip() + '\n'
html_output += '</script>\n</body>\n</html>\n'

print(f"写入 {OUTPUT}...")
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html_output)

size_kb = len(html_output) / 1024
lines_out = html_output.count('\n')
print(f"✅ Clean HTML 已生成: {OUTPUT}")
print(f"   文件大小: {size_kb:.0f} KB")
print(f"   行数: {lines_out}")

# Verify no duplicate functions
import re
funcs = re.findall(r'function (\w+)\(', html_output)
from collections import Counter
dupes = {name: count for name, count in Counter(funcs).items() if count > 1}
if dupes:
    print(f"\n⚠️  重复函数: {dupes}")
else:
    print(f"\n✅ 无重复函数定义")
