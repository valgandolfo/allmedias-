# AllMedias PWA – Visão Geral e Plano de Migração

## 1. Objetivo

Criar uma versão simplificada do AllMedias baseada **apenas em**:

- **Backend**: Django
- **Front**: Templates Django + HTML/CSS/JS simples
- **PWA**: Manifest + service worker em cima dessas mesmas páginas
- **Banco**: SQLite em dev, `DATABASE_URL` (Railway) em produção
- **Armazenamento de arquivos**: Wasabi S3 (via `django-storages`) ou `media/` local

Sem:

- Flutter / React Native
- WebView nativo
- Injeção de token pelo app
- Fluxo de autenticação obrigatório (no começo o PWA NÃO exige login)

---

## 2. Filosofia

- **Menos camadas**: navegador → Django → banco / S3.  
- **PWA = site Django**: o “app” é o próprio site, instalável no celular (Add to Home Screen).  
- **Começar simples**: primeiro tudo público; login/sessão só quando for necessário.  
- **Reaproveitar o que está pronto** aos poucos, dentro de uma pasta de “reciclagem”.

---

## 3. Stack técnica

- **Python**: 3.x  
- **Django**: 6.x  
- **Banco em dev**: SQLite (`db.sqlite3`)  
- **Banco em produção (Railway)**: `DATABASE_URL` (Postgres ou MySQL)  
- **Armazenamento de mídia**:
  - Local (`media/`) em dev
  - Wasabi S3 em produção (`storages`, `boto3`), se configurado no `.env`
- **PWA**:
  - `static/manifest.webmanifest`
  - `static/service-worker.js`
  - Ícones em `static/img/icons/`

---

## 4. Estrutura alvo (novo projeto)

Exemplo de estrutura desejada:

```text
allmedias_pwa/
  config/                 # projeto Django (settings, urls, wsgi)
  core/                   # app principal
    models.py
    views.py
    urls.py
    templates/core/
      base.html
      home.html
      medias_list.html
  templates/              # se usar DIRS global
  static/
    css/
    js/
    img/
    manifest.webmanifest
    service-worker.js
  media/                  # uploads locais (dev)
  venv/
  requirements.txt
  README.md
  docs/
    PROJETO_ALLMEDIAS_PWA.md   # este arquivo (ou cópia dele)
  reciclagem/             # pasta para código reaproveitado do projeto antigo
```

> Observação: no repositório atual os nomes das pastas podem variar, mas a ideia é ter:
> - um **módulo de config** (equivalente ao `pro_flexmedias`)
> - uma **app principal** (equivalente ao `app_flexmedias`)
> - uma pasta `reciclagem/` para código velho que ainda funciona e será migrado aos poucos.

---

## 5. O que pode ser reaproveitado do projeto atual

### 5.1. Models (banco de dados)

- **Tabela de mídias** (`TBMIDEAS` e correlatas) em `app_flexmedias/models.py`.
- **Anotações** (`TBANOTAAI`, itens de anotação, favoritos, transferências).
- **Perfil de usuário** (`TBPERFIL`).

Plano:

- Copiar os **models** para a app nova (`core/models.py` ou `medias/models.py`).
- Ajustar apenas:
  - `related_name` se necessário
  - `verbose_name`/`verbose_name_plural` (estética)
  - Import de `settings.AUTH_USER_MODEL` se ainda não for usado.

### 5.2. Lógica de negócio (utils / serviços)

- `app_flexmedias/utils_media.py`: funções de tratamento de arquivos, geração de thumbnails, etc.
- Qualquer utilitário específico de:
  - Conversão para PDF
  - Tratamento de nomes de arquivos
  - Geração de logs / notificações

Plano:

- Criar `core/utils.py` (ou `core/services/`) no novo projeto.
- Mover funções úteis para lá, **sem dependência de token / Flutter**.

### 5.3. Config de armazenamento (Wasabi / S3)

Bloco existente em `pro_flexmedias/settings.py`:

- `STORAGE_PROVIDER`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`
- `USE_S3` + configuração de `STORAGES`

Plano:

- Reaproveitar **quase igual** no novo `settings.py`.
- Usar `.env` para todas as chaves.
- Produção (Railway): setar as variáveis de ambiente lá; dev: usar local.

### 5.4. Templates que já foram “des-flutterizados”

- `templates/base_webview.html` (já sem `callFlutter`) → pode virar base do novo `base.html`.
- Templates que já usam só:
  - HTML
  - Bootstrap
  - JavaScript puro
  - Sem uso de canais tipo `NavigationChannel`, `UploadChannel`, etc.

Plano:

- Criar `core/templates/core/base.html` e `home.html`.
- Copiar pedaços de layout que já ficaram bons (cards, header, footer) dos templates atuais.
- Remover qualquer referência a tokens, `callFlutter`, canais, etc.

### 5.5. Scripts e automações

- `iniciar_projeto.sh`: já foi limpado para:
  - Criar `venv`
  - Instalar `requirements.txt`
  - Rodar `migrate`
  - Subir `runserver 127.0.0.1:8000`
- `backup_completo.sh`: faz dump do banco, copia `media`, `static`, templates, etc.

Plano:

- Reaproveitar os scripts que fazem sentido:
  - Ajustar caminhos para o novo módulo de config (se o nome mudar).
  - Garantir que não mencionem mais `mobile/`, Flutter, etc.

---

## 6. O que NÃO queremos levar para o novo projeto

- Qualquer código que dependa de:
  - `jwt_login_required`
  - Token JWT no front
  - Injeção de token em WebView / localStorage
- Restos de Flutter (nomes de canais, comentários, scripts).
- CORS complicado ou relaxado demais só porque tinha app externo.
- Lógicas duplicadas (HTML + API fazendo a mesma coisa para o mesmo fluxo).

---

## 7. Pasta de reciclagem

No novo projeto, criar uma pasta:

```text
reciclagem/
  models_velhos.py
  views_velhas.py
  templates_antigas/
  notas_migracao.md
```

Uso:

- Tudo que vier do projeto antigo e **ainda não estiver 100% encaixado** na nova arquitetura vai para lá.
- A cada “onda” de migração:
  - Pega 1 fluxo (ex.: “listar mídias”)
  - Copia só o necessário para o novo `core/views.py` + `core/templates`
  - Marca no `notas_migracao.md` o que já foi migrado e o que ainda depende de token / coisas antigas.

---

## 8. PWA – mínimo necessário

Depois que as páginas básicas estiverem rodando, acrescentar:

1. `static/manifest.webmanifest`:

   - `name`, `short_name`, `start_url: "/"`, `display: "standalone"`
   - Ícones em `static/img/icons/`

2. `static/service-worker.js` (básico):

   - Cacheia `static/` + `base.html` + `home.html`
   - Estratégia simples de `cache-first` para assets

3. No `base.html`:

   - `<link rel="manifest" href="{% static 'manifest.webmanifest' %}">`
   - Registro do service worker em um script JS (`navigator.serviceWorker.register(...)`)

---

## 9. Próximos passos

1. Definir e criar a estrutura do novo projeto (nome do módulo de config e da app principal).
2. Copiar este arquivo `.md` para o novo projeto (por exemplo em `docs/PROJETO_ALLMEDIAS_PWA.md`).
3. Criar a pasta `reciclagem/` no novo projeto.
4. Levar para `reciclagem/` os trechos do projeto antigo que você quiser reaproveitar.
5. A partir daí, migrar **um fluxo por vez** (ex.: lista de mídias, criação de mídia, anotações) para a nova app.

