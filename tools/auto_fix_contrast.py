import re
from pathlib import Path

# Helpers

def hex_to_rgb(h):
    h = h.strip()
    if h.startswith('#'):
        h = h[1:]
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0,min(255,int(round(c)))) for c in rgb)

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

def darken(rgb, factor=0.85):
    return tuple(int(c*factor) for c in rgb)

# Load CSS
css_path = Path('src/assets/css/style.css')
text = css_path.read_text(encoding='utf-8')
match = re.search(r':root\s*\{([^}]*)\}', text, re.S)
if not match:
    print('No :root block')
    raise SystemExit(1)
root_body = match.group(1)
vars = dict(re.findall(r'--([a-z0-9-]+)\s*:\s*([^;]+);', root_body))
vars = {k:v.strip() for k,v in vars.items()}

# Find rules where color is white and background var is set
blocks = re.findall(r'([^{]+)\{([^}]+)\}', text, re.S)
white_bg_tokens = set()
for sel, body in blocks:
    c = re.search(r'color\s*:\s*var\(--([a-z0-9-]+)\)', body)
    b = re.search(r'background(?:-color)?\s*:\s*var\(--([a-z0-9-]+)\)', body)
    if c and b and c.group(1)=='white':
        white_bg_tokens.add(b.group(1))

print('Tokens used as background with white text:', white_bg_tokens)

# For each token, ensure contrast vs white >= 4.5
changed = {}
for token in white_bg_tokens:
    if token not in vars:
        print('Token not in :root:', token)
        continue
    val = vars[token]
    # Only handle hex and rgb/rgba
    if val.startswith('#'):
        rgb = hex_to_rgb(val)
    else:
        m = re.match(r'rgba?\(([^)]+)\)', val)
        if m:
            parts = [int(float(x)) for x in m.group(1).split(',')[:3]]
            rgb = tuple(parts)
        else:
            print('Skipping non-hex/rgb token:', token, val)
            continue
    white = (255,255,255)
    cur = contrast(rgb, white)
    print(token, val, 'contrast vs white:', round(cur,2))
    if cur >= 4.5:
        continue
    # Darken progressively
    iter_count = 0
    new_rgb = rgb
    while cur < 4.5 and iter_count < 20:
        new_rgb = darken(new_rgb, 0.88)
        cur = contrast(new_rgb, white)
        iter_count += 1
    if cur >= 4.5:
        new_hex = rgb_to_hex(new_rgb)
        print('Updating', token, '->', new_hex, 'contrast', round(cur,2))
        # replace in root_body
        root_body = re.sub(r'(--'+re.escape(token)+r'\s*:\s*)[^;]+;', r'\1'+new_hex+';', root_body)
        vars[token] = new_hex
        changed[token] = new_hex
    else:
        print('Could not reach contrast for', token)

if changed:
    # write back full file
    new_text = re.sub(r':root\s*\{[^}]*\}', ':root{\n'+root_body+'\n}', text, count=1, flags=re.S)
    css_path.write_text(new_text, encoding='utf-8')
    print('Wrote updates for tokens:', changed)
else:
    print('No token edits necessary')
