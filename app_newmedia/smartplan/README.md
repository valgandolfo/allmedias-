# 📊 SmartPlan - Extrator de Planilhas

## Visão Geral
Módulo que permite extrair dados tabulares de PDFs e convertê-los para planilhas (CSV ou XLSX).

## Funcionalidades
- ✅ Lista todos os PDFs do usuário
- ✅ Extrai tabelas estruturadas de PDFs usando `pdfplumber`
- ✅ Fallback com regex para dados em formato de texto livre (faturas, extratos)
- ✅ Exportação em **CSV** (compatível Google Sheets/Excel) ou **XLSX** (Excel nativo)
- ✅ Interface responsiva seguindo o padrão do módulo Conversor

## Arquitetura
```
app_newmedia/smartplan/
├── __init__.py
├── apps.py              # Configuração do app
├── urls.py              # Rotas (/smartplan/, /smartplan/extrair/)
├── views.py             # Lógica principal
│   ├── smartplan_lista()     # Lista PDFs do usuário
│   └── smartplan_extrair()   # Extrai dados e retorna arquivo
└── planilha             # Script de referência (legado)
```

## Fluxo de Uso
1. Usuário acessa `/smartplan/`
2. Visualiza lista de seus PDFs
3. Clica em um PDF → abre modal bottom sheet
4. Seleciona formato de saída (CSV ou XLSX)
5. Clica "Extrair e Baixar"
6. Arquivo é gerado e download iniciado automaticamente

## Dependências
- `pdfplumber>=0.10.0` - Extração de tabelas de PDFs
- `pandas>=2.1.0` - Manipulação de dados e exportação
- `openpyxl>=3.1.0` - Geração de arquivos XLSX

## Padrões de Design
- Mesma UI/UX do módulo Conversor
- Filtros por tipo de arquivo
- Busca em tempo real
- Modal bottom sheet responsivo
- Loading overlay durante processamento
- Toast de feedback para usuário

## Extração de Dados
### Método 1: Tabelas Estruturadas
Usado quando o PDF contém tabelas reconhecíveis pelo pdfplumber.

### Método 2: Regex (Fallback)
Para PDFs sem tabelas estruturadas, usa padrões regex para detectar:
- Datas (DD/MM)
- Descrições
- Valores monetários
- Parcelas (XX/YY)

## URLs
- `GET /smartplan/` - Lista de PDFs para extração
- `POST /smartplan/extrair/` - Processa extração e retorna arquivo

## Segurança
- Login obrigatório (`@login_required`)
- Isolamento por usuário (só acessa seus próprios PDFs)
- Validação de existência de arquivo
