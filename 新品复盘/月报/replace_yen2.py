# -*- coding: utf-8 -*-
with open('新品月报_2026年3月_增强版.html', 'r', encoding='utf-8') as f:
    html = f.read()
yen = '\xa5'
cnt = html.count(yen)
html = html.replace(yen, '$')
with open('新品月报_2026年3月_增强版.html', 'w', encoding='utf-8') as f:
    f.write(html)
# write result to file so we can check
with open('replace_result.txt', 'w', encoding='utf-8') as f:
    f.write('RMB yen replaced: ' + str(cnt) + ' times\n')
    f.write('Dollar signs now: ' + str(html.count('$')) + '\n')
    idx = html.find('18.22')
    f.write('Context around 18.22: ' + repr(html[max(0,idx-50):idx+50]) + '\n')
