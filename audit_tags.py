import os
import re

path = 'templates/base.html'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    # Find all if and endif on this line
    ifs = re.findall(r'{%\s*if\b', line)
    endifs = re.findall(r'{%\s*endif\b', line)
    if ifs or endifs:
        print(f"{i+1}: IF:{len(ifs)} ENDIF:{len(endifs)} | {line.strip()[:100]}")
