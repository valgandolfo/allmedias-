import os

files_to_fix = [
    'templates/medias/detalhes.html',
    'templates/medias/editar.html',
    'templates/medias/lista.html',
    'templates/medias/criar.html',
    'templates/registration/register.html',
    'templates/anota_ai/ticar.html',
    'templates/anota_ai/editar.html',
    'templates/anota_ai/lista.html',
    'templates/anota_ai/criar.html'
]

for file_path in files_to_fix:
    full_path = os.path.join('/home/joaonote/newmedia', file_path)
    if not os.path.exists(full_path):
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "{% block extra_js %}\n<script>" not in content and "{% block extra_js %}\n    <script>" not in content:
        # Avoid double wrapping if already wrapped
        if "{% block extra_js %}" in content:
            new_content = content.replace("{% block extra_js %}", "{% block extra_js %}\n<script>")
            new_content = new_content.replace("{% endblock %}", "</script>\n{% endblock %}")
            # wait, replace endblock will replace ALL endblocks?
            # It's better to find the last {% endblock %}!
            # Since {% block extra_js %} is usually the last block:
            
            parts = new_content.rsplit("{% endblock %}", 1)
            new_content = "</script>\n{% endblock %}".join(parts)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")
