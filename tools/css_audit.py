import re
from pathlib import Path
root_css = Path('src/assets/css/style.css')
all_files = list(Path('src').rglob('*.*'))
text = root_css.read_text(encoding='utf-8')
match = re.search(r':root\s*\{([^}]*)\}', text, re.S)
if not match:
    print('NO_ROOT')
    raise SystemExit(1)
body = match.group(1)
vars = re.findall(r'--([a-z0-9-]+)\s*:', body)
usage = {}
for v in vars:
    pattern = re.compile(rf"var\(--{re.escape(v)}\)")
    count = 0
    for f in all_files:
        try:
            s = f.read_text(encoding='utf-8')
        except Exception:
            continue
        count += len(pattern.findall(s))
    usage[v] = count
# Print tokens with counts, and list unused
print('TOKEN|COUNT')
for k in sorted(usage.keys()):
    print(f"{k}|{usage[k]}")
print('\nUNUSED TOKENS:')
for k,v in usage.items():
    if v==0:
        print(k)
