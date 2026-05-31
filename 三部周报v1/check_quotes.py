# -*- coding: utf-8 -*-
import re

with open('C:/Users/Administrator/Desktop/三部周报v1/New project 2-新品板块已放入/src/modules/newProductStatus/新品板块_4.30-5.6_v3.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
issues = []
for script in script_blocks:
    lines = script.split('\n')
    for i, line in enumerate(lines):
        single_quotes = [j for j, c in enumerate(line) if c == "'" and (j == 0 or line[j-1] != '\\')]
        if len(single_quotes) % 2 == 1 and i+1 < len(lines):
            next_line = lines[i+1]
            stripped = next_line.strip()
            if stripped and not stripped.startswith('+') and not stripped.startswith('`') and not stripped.startswith("'") and not stripped.startswith(')') and not stripped.startswith(';'):
                issues.append((i+1, line[:80], next_line[:80]))

if issues:
    print(f'Found {len(issues)} potential issues:')
    for ln, line, nxt in issues:
        print(f'  Line {ln}: {line}')
        print(f'    Next: {nxt}')
else:
    print('No obvious multi-line single-quoted string issues found.')
