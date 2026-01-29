import re
from pathlib import Path

def hex_to_rgb(h):
    h = h.strip()
    if h.startswith('#'):
        h = h[1:]
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def luminance(rgb):
    def chan(c):
        c = c/255.0
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b = rgb
    return 0.2126*chan(r) + 0.7152*chan(g) + 0.0722*chan(b)

def contrast(a,b):
    la = luminance(a)
    lb = luminance(b)
    L1 = max(la,lb)
    L2 = min(la,lb)
    return (L1+0.05)/(L2+0.05)

root_css = Path('src/assets/css/style.css')
text = root_css.read_text(encoding='utf-8')
match = re.search(r':root\s*\{([^}]*)\}', text, re.S)
if not match:
    print('No :root block')
    raise SystemExit(1)
body = match.group(1)
vars_raw = re.findall(r'--([a-z0-9-]+)\s*:\s*([^;]+);', body)
vars = {k:v.strip() for k,v in vars_raw}
# normalize hex/rgb values (we only handle hex and simple rgba with full integer rgb)
norm = {}
for k,v in vars.items():
    if v.startswith('#'):
        norm[k] = v.lower()
    elif v.startswith('rgba') or v.startswith('rgb'):
        norm[k] = v
    else:
        norm[k] = v

# find exact duplicate hex tokens
value_to_keys = {}
for k,v in norm.items():
    # only normalize hex colors to full 6-digit lowercase
    if v.startswith('#'):
        h = v[1:]
        if len(h)==3:
            h = ''.join([c*2 for c in h])
        h = '#'+h.lower()
        value_to_keys.setdefault(h, []).append(k)
    else:
        value_to_keys.setdefault(v, []).append(k)

duplicates = {val:ks for val,ks in value_to_keys.items() if len(ks)>1}
print('DUPLICATE TOKEN GROUPS (exact matches):')
for val, ks in duplicates.items():
    print(val, '->', ', '.join(ks))

# compute contrast against white, black, brand, bg-section
reference_names = ['white','brand','bg-section']
refs = {}
for rn in reference_names:
    if rn in norm:
        refs[rn] = norm[rn]
    else:
        # fallback
        refs[rn] = '#ffffff' if rn=='white' else '#000000'

# helper to get rgb tuple
def parse_color(val):
    val = val.strip()
    if val.startswith('#'):
        return hex_to_rgb(val)
    m = re.match(r'rgba?\(([^)]+)\)', val)
    if m:
        parts = [int(float(x)) for x in m.group(1).split(',')[:3]]
        return tuple(parts)
    return None

print('\nCONTRAST RATIOS (token vs white/brand/bg-section):')
low = []
for k,v in norm.items():
    rgb = parse_color(v)
    if not rgb:
        continue
    out = []
    for rn,rv in refs.items():
        rrgb = parse_color(rv) if rv.startswith('#') or rv.startswith('rgb') else None
        if not rrgb:
            # try to parse var reference
            m = re.match(r'var\(--([a-z0-9-]+)\)', rv)
            if m and m.group(1) in norm:
                rrgb = parse_color(norm[m.group(1)])
        if not rrgb:
            continue
        cr = contrast(rgb, rrgb)
        out.append((rn, round(cr,2)))
        if cr < 4.5:
            low.append((k, v, rn, round(cr,2)))
    print(f"{k} ({v}) --> {out}")

print('\nLOW CONTRAST WARNINGS (ratio < 4.5 for normal text):')
for item in low:
    print(item)

# Find rules where color and background are set within same block
blocks = re.findall(r'([^{]+)\{([^}]+)\}', text, re.S)
pairs = []
for sel, body in blocks:
    c = re.search(r'color\s*:\s*var\(--([a-z0-9-]+)\)', body)
    b = re.search(r'background(?:-color)?\s*:\s*var\(--([a-z0-9-]+)\)', body)
    if c and b:
        pairs.append((sel.strip(), c.group(1), b.group(1)))

print('\nRULES WITH BOTH color AND background (by var name):')
for sel,cname,bname in pairs:
    print(f"{sel}  color:--{cname}  bg:--{bname}")

# Prepare safe consolidations for exact duplicate hex tokens: keep first as canonical
consolidations = []
for val,ks in duplicates.items():
    canon = ks[0]
    for other in ks[1:]:
        consolidations.append((other, canon))

if consolidations:
    print('\nPROPOSED CONSOLIDATIONS (replace var(--old) -> var(--canon)):')
    for old,can in consolidations:
        print(old, '->', can)
else:
    print('\nNo exact-duplicate consolidations found.')

# Write consolidations patch if any
if consolidations:
    s = text
    for old,can in consolidations:
        s = s.replace(f'var(--{old})', f'var(--{can})')
        # remove definition of old in :root
        s = re.sub(r'--'+re.escape(old)+r'\s*:[^;]+;\n', '', s)
    Path('src/assets/css/style.css').write_text(s, encoding='utf-8')
    print('\nApplied consolidations to src/assets/css/style.css')
else:
    print('No file edits applied.')
