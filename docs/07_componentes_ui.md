# Componentes de UI

## Indexador PDF

Arquivo: `Indexador_PDF/Indexador.py`.

### Tela principal

- Janela: `Indexador PDF - ChromaDB com Fase`.
- Título: `Indexador PDF para ChromaDB`.
- Entrada de caminho PDF.
- Botão `Selecionar PDF`.
- Entrada `Número da fase`.
- Botão `Indexar PDF`.
- Área de texto para status/resultado.

### Ações do usuário

- Selecionar PDF.
- Informar fase.
- Executar indexação.

### Estados internos relevantes

- Conteúdo da entrada de caminho.
- Conteúdo da entrada de fase.
- Texto de resultado.

### Riscos de acoplamento

- Callback `executar_indexacao` valida UI, chama regra de negócio e formata resposta no mesmo bloco.
- Objetos globais de ChromaDB e modelo são carregados ao importar o arquivo.

## RAG local CAPEX — versão v4

Arquivo: `Rede_Neural_CAPEX/Nova_versão_v4.py`.

### Classe principal

- `RagLocalApp` encapsula a UI Tkinter na versão v4.

### Elementos principais

- Campo `Atividade principal`.
- Cinco campos `Fase candidata`.
- Botão `Run RAG - ChromaDB por Fase`.
- Tabela `ttk.Treeview` com colunas: fase, texto, documento, score de fase, score documental, decisão, grau, evidência e justificativa.
- Área `Resultado detalhado`.

### Props/entradas relevantes

Tkinter não usa props no estilo React. Os dados entram por widgets:

- `entrada_principal`.
- `entradas_frases`.
- `tabela_resultado`.
- `resultado_texto`.

### Ações do usuário

- Digitar atividade principal.
- Digitar uma ou mais fases candidatas.
- Executar análise.

### Riscos de regra de negócio acoplada à interface

- `executar_rag` coleta dados, valida entradas, chama casos de uso e trata erro.
- `preencher_tabela` define parte do contrato visual e truncamento.
- `_exibir_resultado` mistura regras de apresentação com estrutura de dados interna.

## Versões antigas da UI

`Nova_Versão.py`, `Nova_versão_v2.py` e `Nova_versão_v3.py` implementam UI similar com funções globais e widgets globais. São úteis como histórico, mas aumentam risco de manutenção se alguém editar a versão errada.

