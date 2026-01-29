import re
from pathlib import Path
from math import sqrt

def hex_to_rgb(h):
    h = h.strip()
    if h.startswith('#'):
        h = h[1:]
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

css_path = Path('src/assets/css/style.css')
text = css_path.read_text(encoding='utf-8')
match = re.search(r':root\s*\{([^}]*)\}', text, re.S)
if not match:
    print('no root')
    raise SystemExit(1)
root = match.group(1)
vars = dict(re.findall(r'--([a-z0-9-]+)\s*:\s*([^;]+);', root))
# normalize hex only
hex_tokens = {}
for k,v in vars.items():
    val = v.strip()
    if val.startswith('#'):
        h = val[1:]
        if len(h)==3:
            h = ''.join([c*2 for c in h])
        hex_tokens[k] = '#'+h.lower()

# find near duplicates
tokens = list(hex_tokens.items())
clusters = []
used = set()
threshold = 12  # Euclidean distance in RGB space
for i,(k1,v1) in enumerate(tokens):
    if k1 in used:
        continue
    rgb1 = hex_to_rgb(v1)
    group = [ (k1,v1) ]
    used.add(k1)
    for j in range(i+1,len(tokens)):
        k2,v2 = tokens[j]
        if k2 in used:
            continue
        rgb2 = hex_to_rgb(v2)
        d = sqrt(sum((a-b)**2 for a,b in zip(rgb1,rgb2)))
        if d <= threshold:
            group.append((k2,v2))
            used.add(k2)
    if len(group)>1:
        clusters.append(group)

if not clusters:
    print('No near-duplicate clusters found')
    raise SystemExit(0)

print('Found clusters:')
for g in clusters:
    print(g)

# Apply consolidations: pick first as canonical
new_text = text
for g in clusters:
    canon = g[0][0]
    for k,v in g[1:]:
        # replace var(--k) with var(--canon)
        new_text = new_text.replace('var(--'+k+')', 'var(--'+canon+')')
        # remove definition from :root
        new_text = re.sub(r'--'+re.escape(k)+r'\s*:[^;]+;\n', '', new_text)

css_path.write_text(new_text, encoding='utf-8')
print('Applied consolidations and updated style.css')
