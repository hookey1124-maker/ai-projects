# -*- coding: utf-8 -*-
with open('新品月报_2026年3月_增强版.html', 'r', encoding='utf-8') as f:
    html = f.read()

cnt = html.count('¥')
html = html.replace('¥', '$')
print('替换完成: ¥ -> $', cnt, '次')

with open('新品月报_2026年3月_增强版.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('已保存')
