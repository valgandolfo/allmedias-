# Passagem de Contexto - Deploy de Amanhã

Data: 2026-03-18

## O que foi ajustado hoje

### Minhas Mídias
- Após criar mídia, o fluxo agora retorna para a lista (`media_lista`) com grid atualizado.
- Thumbnail no grid prioriza `miniatura` quando existir.
- Em editar/excluir mídia, retorno padronizado para a lista de mídias.
- Menu dos 3 pontinhos ganhou opção **Compartilhar**:
  - usa compartilhamento nativo quando disponível (`navigator.share`);
  - fallback com abertura do arquivo.

### Conversor de Mídia
- Removido botão antigo de voltar.
- Adicionado botão flutuante Home no mesmo padrão visual de "Minhas Mídias".

### Anota Aí
- Lista numerada:
  - inicia com `1 - ` automaticamente quando vazio;
  - ao `Enter`, incrementa (`2 -`, `3 -`...) com cursor já posicionado.
- Checklist:
  - inicia com `[ ] ` automaticamente quando vazio;
  - ao `Enter`, cria nova linha `[ ] ` com cursor posicionado.
- Parser backend atualizado para aceitar formatos com espaço (`1 - item`) e checklist com hífen (`- [ ]`, `- [x]`).

### Excluir Anotação
- Tela de exclusão agora mostra preview da anotação antes de confirmar:
  - texto, lista numerada, checklist ou dados PIX.

### Ticar Checklist
- Menu dos 3 pontinhos ganhou **Ticar** (somente para checklist).
- Fluxo evoluiu de modal para **tela própria** estilo módulo.
- Tela `ticar`:
  - item clicável marca/desmarca;
  - alterna `[ ]` / `[X]`;
  - aplica/remover risco no texto;
  - persistência imediata via endpoint.
- Tela refinada visualmente com container/card melhor enquadrado e contador de progresso.
- Mantida navegação simplificada: somente seta superior de retorno.

### Compartilhar Anotações
- Menu dos 3 pontinhos ganhou **Compartilhar** para anotações.
- Backend prepara payload por tipo:
  - PIX (nome/chave/favorecido/banco),
  - checklist (`[X]` e `[ ]`),
  - lista numerada (`1 - ...`),
  - texto simples.
- Frontend:
  - usa `navigator.share` no celular;
  - fallback copia texto para clipboard.

## Endpoints adicionados/ajustados (Anota Aí)
- `GET /anotacoes/<pk>/checklist-itens/`
- `POST /anotacoes/item/<item_pk>/ticar/`
- `GET /anotacoes/<pk>/ticar/`
- `GET /anotacoes/<pk>/compartilhar-dados/`

## Checklist sugerido para amanhã (Deploy)
- Rodar testes manuais principais:
  - criar/editar/excluir mídia;
  - compartilhar mídia;
  - conversor com retorno correto;
  - anotações (texto/lista/checklist/pix);
  - ticar checklist e compartilhar anotação.
- Validar fluxo em celular real (principalmente `navigator.share`).
- Conferir variáveis de ambiente de produção.
- Executar migrações pendentes (se houver).
- Coletar estáticos (se aplicável).
- Subir versão e validar páginas críticas pós-deploy.

## Observações
- Alterações focadas em UX mobile e consistência de navegação.
- Sem erros de lint reportados nos arquivos modificados durante os ajustes.
