#!/usr/bin/env python3
"""
Safely wraps raw JS inside {% block extra_js %} with <script> tags.
Skips templates that already have <script> as their first tag inside the block.
"""
import re
import os

templates = [
    'templates/medias/detalhes.html',
    'templates/medias/lista.html',
    'templates/medias/criar.html',
    'templates/anota_ai/ticar.html',
    'templates/anota_ai/editar.html',
    'templates/anota_ai/lista.html',
    'templates/anota_ai/criar.html',
    'templates/registration/register.html',
]

BASE = '/home/joaonote/newmedia'

for rel_path in templates:
    full_path = os.path.join(BASE, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the extra_js block content
    pattern = r'(\{%\s*block extra_js\s*%\})(.*?)(\{%\s*endblock\s*%\})'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"SKIP (no block): {rel_path}")
        continue

    block_open = match.group(1)
    block_body = match.group(2)
    block_close = match.group(3)

    stripped = block_body.strip()

    # Already has <script> tag at the start?
    if stripped.lower().startswith('<script'):
        print(f"SKIP (already has <script>): {rel_path}")
        continue

    # Wrap it
    new_body = f"\n<script>\n{stripped}\n</script>\n"
    new_content = content[:match.start(2)] + new_body + content[match.end(2):]

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"FIXED: {rel_path}")
