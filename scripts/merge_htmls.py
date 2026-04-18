import re

def extract_block(text, block_name):
    # Extract content between {% block NAME %} and {% endblock %}
    match = re.search(r'{%\s*block\s+' + block_name + r'\s*%}(.*?){%\s*endblock\s*%}', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def main():
    base_dir = "/home/joaonote/newmedia/templates/anota_ai/"
    
    with open(base_dir + "detalhes.html", "r") as f:
        detalhes_text = f.read()
    with open(base_dir + "form.html", "r") as f:
        form_text = f.read()
    with open(base_dir + "ticar.html", "r") as f:
        ticar_text = f.read()
        
    # Extract blocks
    detalhes_content = extract_block(detalhes_text, "content")
    detalhes_js = extract_block(detalhes_text, "extra_js")
    
    form_content = extract_block(form_text, "content")
    form_css = extract_block(form_text, "extra_css")
    form_js = extract_block(form_text, "extra_js")
    
    ticar_content = extract_block(ticar_text, "content")
    ticar_css = extract_block(ticar_text, "extra_css")
    ticar_js = extract_block(ticar_text, "extra_js")

    # The current detalhes_content has an if-else for deletar.
    # We will split it manually since it's simpler.
    # From line 9 to line 62 is DELETAR. From 64 to 214 is VER.
    
    deletar_html = ""
    ver_html = ""
    
    # Quick hack to separate:
    parts = detalhes_content.split("<!-- ==================== MODO: VER CONTEUDO ==================== -->")
    if len(parts) > 1:
        deletar_part = parts[0]
        ver_part = parts[1]
        
        # clean up {% if acao == 'deletar' %}
        deletar_part = re.sub(r'{%\s*if acao == \'deletar\'\s*%}', '', deletar_part)
        
        # clean up {% else %}
        ver_part = re.sub(r'{%\s*else\s*%}', '', ver_part, count=1)
        # clean up {% endif %}
        ver_part = re.sub(r'{%\s*endif\s*%}$', '', ver_part.strip())
        
        deletar_html = deletar_part.strip()
        ver_html = ver_part.strip()
    
    
    # Assemble new HTML
    new_html = """{% extends 'base.html' %}

{% block title %}
{% if acao == 'deletar' %}Excluir Anotação
{% elif acao == 'criar' %}Incluir Anotação
{% elif acao == 'editar' %}Editar Anotação
{% elif acao == 'ticar' %}Ticar Checklist
{% else %}Detalhes da Anotação{% endif %} - NewMedia
{% endblock %}

{% block extra_css %}
"""
    new_html += """<style>
/* ================= CSS FORMULARIO ================= */
""" + form_css.replace('<style>', '').replace('</style>', '') + """

/* ================= CSS TICAR ================= */
""" + ticar_css.replace('<style>', '').replace('</style>', '') + """

/* ================= CSS DETALHES ================= */
.checklist-item-zebrado {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid transparent;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: background 0.15s;
}
.checklist-item-zebrado:nth-child(odd) { background: rgba(255,255,255,0.06); }
.checklist-item-zebrado:hover { background: rgba(14,165,233,0.1); border-left-color: var(--primary-color); }

.lista-item-zebrado {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid transparent;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: background 0.15s;
}
.lista-item-zebrado:nth-child(odd) { background: rgba(255,255,255,0.06); }
.lista-item-zebrado:hover { background: rgba(14,165,233,0.1); border-left-color: var(--primary-color); }
.lista-item-numero {
    background: var(--primary-color);
    color: white;
    font-weight: 700;
    font-size: 0.75rem;
    min-width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
</style>
{% endblock %}

{% block content %}
{% if acao == 'criar' or acao == 'editar' %}
<!-- ==================== MODO: CRIAR/EDITAR ==================== -->
""" + form_content.replace("{% if anotacao %}Editar{% else %}Criar Nova{% endif %}", "{% if acao == 'editar' %}Editar{% else %}Incluir{% endif %}") + """

{% elif acao == 'ticar' %}
<!-- ==================== MODO: TICAR ==================== -->
""" + ticar_content + """

{% elif acao == 'deletar' %}
<!-- ==================== MODO: CONFIRMAR EXCLUSAO ==================== -->
""" + deletar_html + """

{% else %}
<!-- ==================== MODO: VER CONTEUDO ==================== -->
"""
    
    # Strip the inline <style> from ver_html so it doesn't pollute
    ver_html_clean = re.sub(r'<style>.*?</style>', '', ver_html, flags=re.DOTALL)
    new_html += ver_html_clean + """
{% endif %}
{% endblock %}

{% block extra_js %}
"""
    new_html += """
<!-- ================= JS DETALHES ================= -->
""" + detalhes_js + """

{% if acao == 'criar' or acao == 'editar' %}
<!-- ================= JS FORMULARIO ================= -->
""" + form_js + """
{% endif %}

{% if acao == 'ticar' %}
<!-- ================= JS TICAR ================= -->
""" + ticar_js + """
{% endif %}
{% endblock %}
"""

    with open(base_dir + "detalhes_novo.html", "w") as f:
        f.write(new_html)
    print("detalhes_novo.html criado!")

if __name__ == "__main__":
    main()
