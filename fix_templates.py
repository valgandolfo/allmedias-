import os
import re

def fix_template(filepath, title):
    with open(filepath, 'r') as f:
        content = f.read()

    if '{% extends' in content:
        print(f"{filepath} already extends base.html")
        return

    # Extract CSS
    css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    css = css_match.group(1) if css_match else ""
    
    # Remove body styling and old header margin
    css = re.sub(r'body\s*{[^}]*}', '', css)
    css = css.replace('margin: -10px -10px 15px -10px;', 'margin-bottom: 15px;')
    css = css.replace('margin: -16px -16px 20px -16px;', 'margin-bottom: 20px;')
    css = css.replace('border-radius: 8px 8px 0 0;', 'border-radius: 8px;')

    # Extract Body Content
    body_match = re.search(r'<body>(.*?)<script', content, re.DOTALL)
    body_content = body_match.group(1) if body_match else ""
    if not body_content: # sometimes ends right before </body>
        body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
        body_content = body_match.group(1) if body_match else ""

    # Clear out fab button since base.html has header navigation
    body_content = re.sub(r'<a href=".*?" class="btn-fab btn-fab-home".*?</a>', '', body_content, flags=re.DOTALL)
    body_content = re.sub(r'<a href=".*?" class="fixed-bottom-btn".*?</a>', '', body_content, flags=re.DOTALL)

    # Extract JS
    js_match = re.search(r'<script>(.*?)</script>.*?</body>', content, re.DOTALL)
    if not js_match:
        # maybe there's no script tag or multiple
        js_match = re.search(r'<script>(.*?)</script>\s*</body>', content, re.DOTALL)
    js = js_match.group(1) if js_match else ""
    
    # Just grab all scripts except the bootstrap cdn one
    scripts = re.findall(r'<script.*?>(.*?)</script>', content, re.DOTALL)
    js_all = "\n".join([s for s in scripts if s.strip()])

    new_content = f"""{{% extends "base.html" %}}
{{% load static %}}

{{% block title %}}{title}{{% endblock %}}

{{% block extra_css %}}
<style>
{css}
</style>
{{% endblock %}}

{{% block content %}}
<div class="container px-0">
{body_content}
</div>
{{% endblock %}}

{{% block extra_js %}}
<script>
{js_all}
</script>
{{% endblock %}}
"""
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Fixed {filepath}")

fix_template('/home/joaonote/newmedia/templates/transferir/enviar_individual.html', 'Enviar Mídia')
fix_template('/home/joaonote/newmedia/templates/transferir/enviar_item.html', 'Enviar Item')
fix_template('/home/joaonote/newmedia/templates/transferir/enviar_anotacao.html', 'Enviar Anotação')
fix_template('/home/joaonote/newmedia/templates/transferir/caixa_entrada.html', 'Caixa de Entrada')

