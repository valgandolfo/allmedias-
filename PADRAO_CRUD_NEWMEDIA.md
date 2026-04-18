# Padrão de CRUD - NewMedia (Arquitetura Pai-Filho)

Para manter o projeto extremamente limpo, padronizado, e altamente escalável, adotamos uma arquitetura de herança rigorosa para os CRUDs (Create, Read, Update, Delete) de todos os módulos.

O sistema baseia-se em um **CRUD-Pai genérico** e **CRUDs-Filhos específicos**. O principal objetivo é não repetir código HTML, CSS ou JavaScript. 

Todo módulo (ex: `anota_ai`, `medias`) deve ter **apenas dois (2) arquivos** HTML:
1. `lista.html`
2. `detalhes.html`

---

## 🏗️ 1. O CRUD Pai (A Inteligência Base)
A pasta `templates/crud/` contém a "casca" que dita o comportamento de todo o sistema. Se houver um bug genérico ou se for preciso mudar uma cor no layout principal, altera-se apenas o CRUD Pai.

### `crud/lista_base.html`
**Responsabilidades:**
- Controla a interface da lista de itens e a barra de pesquisa genérica.
- Contém o **View Toggle (Lista vs Grid)**, salvando a preferência no `localStorage` do navegador.
- Requer que o filho implemente blocos como `{% block list_content %}`.

### `crud/detalhes_base.html`
**Responsabilidades:**
- Redireciona a tela baseado na variável de contexto `acao` enviada pelo backend (ex: `criar`, `editar`, `deletar`, ou padrão/ver).
- Fornece o container de formulário e a tela oficial (padronizada) de confirmação de Exclusão (com ícone vermelho de perigo).

---

## 👨‍👦 2. Como criar um CRUD Filho

Se você for criar ou manter um módulo (ex: `Clientes`), você criará apenas dois arquivos na pasta do seu app (`templates/clientes/`):

### Passo A: Criando `lista.html`

```html
{% extends 'crud/lista_base.html' %}

<!-- 1. Textos do Cabeçalho -->
{% block crud_title %}Meus Clientes{% endblock %}
{% block crud_icon %}👥{% endblock %}
{% block crud_subtitle %}Gerenciamento de contatos{% endblock %}

<!-- 2. Botões de Filtro -->
{% block filters %}
<button type="button" class="btn btn-sm btn-outline-secondary rounded-pill px-3 filter-btn active" data-tipo="all" onclick="filtrarTipo('all')">Todos</button>
<button type="button" class="btn btn-sm btn-outline-secondary rounded-pill px-3 filter-btn" data-tipo="pj" onclick="filtrarTipo('pj')">Empresas</button>
{% endblock %}

<!-- 3. Loop da Lista. Atenção para a classe 'crud-item' e os atributos 'data-' usados no JS de filtro do CRUD Pai -->
{% block list_content %}
    {% for cliente in clientes %}
    <div class="crud-item cliente-item" data-tipo="{{ cliente.tipo }}" data-titulo="{{ cliente.nome|lower }}">
        <!-- O layout aqui deve estar preparado para o modo GRID via CSS -->
        <div class="cliente-info" onclick="window.location.href='{% url 'cliente_detalhes' cliente.pk %}'">
            <strong>{{ cliente.nome }}</strong>
        </div>
        <!-- Menu de três pontinhos -->
        <div onclick="abrirMenu({{ cliente.pk }}, '{{ cliente.nome|escapejs }}')">
            <i class="bi bi-three-dots-vertical fs-5"></i>
        </div>
    </div>
    {% empty %}
        <p>Nenhum cliente cadastrado.</p>
    {% endfor %}
{% endblock %}

<!-- 4. Botão FAB Flutuante -->
{% block fab %}
{% url 'cliente_form' as url_criar %}
{% include "components/fab.html" with url=url_criar icon="bi-plus-lg" position="right" color="var(--primary-color)" title="Novo" %}
{% endblock %}

<!-- 5. Modal de Opções (acionado pelos três pontinhos) -->
{% block modal %}
<!-- (Ver exemplo na lista.html de anota_ai ou medias) -->
{% endblock %}

<!-- 6. Scripts (Filtro e Menu) e CSS (Configurar a adaptação para .layout-grid .cliente-item) -->
{% block child_js %} ... {% endblock %}
{% block child_css %} ... {% endblock %}
```

### Passo B: Criando `detalhes.html`

```html
{% extends 'crud/detalhes_base.html' %}

{% block crud_title %}Clientes{% endblock %}

<!-- 1. BLOCO FORMULÁRIO (Usado para ação 'criar' ou 'editar') -->
{% block form_view %}
<div class="card-custom p-3">
    <h5>{% if cliente %}Editar{% else %}Criar{% endif %}</h5>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Salvar</button>
    </form>
</div>
{% endblock %}

<!-- 2. BLOCO EXCLUSÃO (Para ação 'deletar') -->
<!-- Define como os dados do item aparecerão na tela de aviso de exclusão -->
{% block delete_info %}
<div class="border p-3 bg-light text-center">
    <strong>{{ cliente.nome }}</strong> - {{ cliente.email }}
</div>
{% endblock %}
{% block delete_cancel_url %}{% url 'cliente_detalhes' cliente.pk %}{% endblock %}

<!-- 3. BLOCO LEITURA / VER DETALHES (Modo Padrão) -->
{% block detail_view %}
<div class="card-custom p-4">
    <h4>{{ cliente.nome }}</h4>
    <p>{{ cliente.email }}</p>
    <!-- OBRIGATÓRIO: Botões de Editar e Excluir apontando corretamente -->
    <a href="{% url 'cliente_form' cliente.pk %}" class="btn btn-outline-primary">Editar</a>
    <a href="{% url 'cliente_detalhes' cliente.pk %}?acao=deletar" class="btn btn-outline-danger">Excluir</a>
</div>
{% endblock %}

<!-- 4. CSS e JS Específico do formulário ou da visualização -->
{% block child_js %} ... {% endblock %}
{% block child_css %} ... {% endblock %}
```

---

## ⚙️ 3. Configurando a `views.py` e `urls.py` do Filho

Para que o template Pai reaja corretamente, o backend precisa estar minimalista:

### `urls.py` (Exatamente 4 rotas necessárias)
```python
urlpatterns = [
    path('lista/', views.cliente_lista, name='cliente_lista'),
    path('criar/', views.cliente_form, name='cliente_form'),
    path('<int:pk>/', views.cliente_detalhes, name='cliente_detalhes'),
    path('<int:pk>/form/', views.cliente_form, name='cliente_form'), # Usa mesma view de criar
]
```

### `views.py` (Lógica Unificada)
```python
# 1. View de Lista (Manda os itens)
def cliente_lista(request):
    clientes = Cliente.objects.all()
    # Importante passar 'crud_name' único para o View Toggle salvar certinho no localStorage (ex: 'clientes_layout')
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'crud_name': 'clientes'})

# 2. View de Formulário (Cria e Edita na mesma função, passando a 'acao')
def cliente_form(request, pk=None):
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None
    acao = 'editar' if pk else 'criar'
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/detalhes.html', {'form': form, 'cliente': cliente, 'acao': acao})

# 3. View de Leitura/Exclusão (Trata exclusão via GET '?acao=deletar')
def cliente_detalhes(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    acao = request.GET.get('acao', 'ver')
    
    # Se bater no modo deletar E for um POST confirmando a tela:
    if acao == 'deletar' and request.method == 'POST':
        cliente.delete()
        return redirect('cliente_lista')
        
    return render(request, 'clientes/detalhes.html', {'cliente': cliente, 'acao': acao})
```
