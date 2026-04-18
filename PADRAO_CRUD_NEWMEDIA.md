# Padrão de CRUD - NewMedia (2 Arquivos HTML)

Para manter o projeto limpo, padronizado e evitar a proliferação de arquivos HTML desnecessários, adotamos um padrão estrito para as operações de CRUD (Create, Read, Update, Delete) nos módulos do sistema. 

**Todo CRUD deve possuir apenas dois (2) arquivos de template HTML principais:**
1. `lista.html`
2. `detalhes.html`

## 1. O Arquivo `lista.html`
**Responsabilidade:** Visualização das coleções de dados, filtragem, paginação e navegação inicial.
- Deve conter a estrutura de lista (cards zebrados, grids ou tabelas).
- Deve incluir uma barra de pesquisa e opções de filtros (se houver).
- O botão `(+)` (geralmente um FAB) aponta para a rota de Criação.
- O clique em um item da lista aponta para a rota de Detalhes (`/item/<id>/`).
- O clique no menu de opções (`...`) do item, direciona para as ações rápidas, que por sua vez chamam rotas específicas com a ação correspondente (ex: `/item/<id>/form/` para Editar ou `/item/<id>/?acao=deletar` para Excluir).

## 2. O Arquivo `detalhes.html`
**Responsabilidade:** Agrupar TODAS as telas e interações envolvendo um único registro.

Em vez de criar `form.html`, `criar.html`, `editar.html`, `excluir.html`, centralizamos as interfaces em `detalhes.html`. Este template reage a uma variável de contexto enviada pela View (ex: `acao`).

### Estrutura Interna do `detalhes.html`
O template deve utilizar uma cadeia sequencial de `{% if %}` e `{% elif %}` baseada na ação requerida. A interface HTML, o Título da Página e o JavaScript devem mudar com base nessa ação.

```html
{% extends 'base.html' %}

{% block title %}
{% if acao == 'deletar' %}Excluir Registro
{% elif acao == 'criar' %}Incluir Registro
{% elif acao == 'editar' %}Editar Registro
{% else %}Detalhes do Registro{% endif %} - NewMedia
{% endblock %}

{% block content %}
    
    <!-- 1. MODO: INCLUIR OU EDITAR (FORMULÁRIO) -->
    {% if acao == 'criar' or acao == 'editar' %}
        <div class="card-custom p-3">
            <h5 class="mb-3">
                {% if acao == 'editar' %}Editar Registro{% else %}Incluir Registro{% endif %}
            </h5>
            <form method="post">
                {% csrf_token %}
                <!-- Seu formulário aqui -->
                <button type="submit">Salvar</button>
            </form>
        </div>

    <!-- 2. MODO: EXCLUIR (CONFIRMAÇÃO) -->
    {% elif acao == 'deletar' %}
        <div class="card-custom p-4 text-center">
            <h4 class="text-danger">Excluir Registro?</h4>
            <p>Confirme a exclusão deste item. A ação não pode ser desfeita.</p>
            <form method="post">
                {% csrf_token %}
                <button type="submit" class="btn btn-danger">Sim, Excluir</button>
            </form>
        </div>

    <!-- 3. MODO PADRÃO: VER DETALHES -->
    {% else %}
        <div class="card-custom p-4">
            <h4>{{ objeto.titulo }}</h4>
            <p>{{ objeto.descricao }}</p>
            
            <!-- Botões de Ação na View de Detalhes -->
            <a href="{% url 'meu_app_form' objeto.pk %}" class="btn">Editar</a>
            <a href="{% url 'meu_app_detalhes' objeto.pk %}?acao=deletar" class="btn">Excluir</a>
        </div>
    {% endif %}

{% endblock %}
```

## Como configurar a `views.py`

As Views também devem ser otimizadas. Você não precisa de uma view para cada template, mas pode ter funções de View que mapeiam para as intenções do usuário, e ao final, todas renderizam o `detalhes.html` enviando a ação correta no contexto.

**Exemplo Prático:**

```python
# View para Lista (Renderiza lista.html)
def item_lista(request):
    itens = Item.objects.all()
    return render(request, 'meu_app/lista.html', {'itens': itens})

# View para Formulário (Criar/Editar) (Renderiza detalhes.html)
def item_form(request, pk=None):
    if pk:
        item = get_object_or_404(Item, pk=pk)
        acao = 'editar'
    else:
        item = None
        acao = 'criar'
    
    # Lógica do Formulário (POST e GET)...
    
    return render(request, 'meu_app/detalhes.html', {
        'form': form,
        'acao': acao,
        'item': item
    })

# View para Ver Detalhes e Excluir (Renderiza detalhes.html)
def item_detalhes(request, pk):
    item = get_object_or_404(Item, pk=pk)
    acao = request.GET.get('acao', 'ver')
    
    if acao == 'deletar' and request.method == 'POST':
        item.delete()
        return redirect('item_lista')
        
    return render(request, 'meu_app/detalhes.html', {
        'item': item,
        'acao': acao
    })
```

## Vantagens desta Abordagem
- Redução brutal na quantidade de templates.
- Todo CSS/JS pertinente às operações em um registro fica centralizado em um só arquivo.
- O controle de renderização recai sobre a "ação" vinda da View.
- Padrão uniforme, todos os apps mantêm a mesma inteligência na UI.
