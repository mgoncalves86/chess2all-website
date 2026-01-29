#!/usr/bin/env python3
"""
Simple image optimizer: creates WebP copies for images under src/assets/img
Requires Pillow: pip install pillow
"""
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'assets', 'img')

EXTS = ('.png', '.jpg', '.jpeg')

os.makedirs(os.path.join(ROOT, 'webp'), exist_ok=True)

for dirpath, dirs, files in os.walk(ROOT):
    for f in files:
        if f.lower().endswith(EXTS):
            src = os.path.join(dirpath, f)
            rel = os.path.relpath(src, ROOT)
            dest_dir = os.path.join(ROOT, 'webp', os.path.dirname(rel))
            os.makedirs(dest_dir, exist_ok=True)
            name, _ = os.path.splitext(os.path.basename(f))
            dest = os.path.join(dest_dir, name + '.webp')
            try:
                with Image.open(src) as im:
                    im.save(dest, 'WEBP', quality=80, method=6)
                    print('WROTE', dest)
            except Exception as e:
                print('SKIP', src, e)
