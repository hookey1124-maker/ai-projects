import re

with open(r'C:\Users\Administrator\Desktop\三部周报v1\必看.rtf', 'r', encoding='latin-1') as f:
    content = f.read()

all_chars = []
i = 0
while i < len(content):
    if content[i:i+2] == r'\u' and i+2 < len(content) and content[i+2].isdigit():
        j = i + 2
        while j < len(content) and content[j].isdigit():
            j += 1
        num = int(content[i+2:j])
        if 0 < num < 65536:
            all_chars.append(chr(num))
        i = j
        if i < len(content) and content[i] == '?':
            i += 1
        continue
    if content[i:i+4] == r'\par':
        all_chars.append('\n')
        i += 4
        continue
    if content[i] == '\\':
        j = i + 1
        if j < len(content) and content[j].isalpha():
            while j < len(content) and content[j].isalpha():
                j += 1
            while j < len(content) and content[j].isdigit():
                j += 1
            if j < len(content) and content[j] == ' ':
                j += 1
            i = j
            continue
        elif j < len(content) and content[j] == "'":
            i = j + 3
            continue
    if content[i] in '{}':
        i += 1
        continue
    if content[i] in '\r\n':
        i += 1
        continue
    i += 1

text = ''.join(all_chars)
for line in text.split('\n'):
    line = line.strip()
    if line and len(line) > 1:
        print(line)
