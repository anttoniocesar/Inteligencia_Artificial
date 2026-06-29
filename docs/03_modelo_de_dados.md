# Modelo de dados

## Entidades principais

### Documento PDF

Representa um arquivo PDF selecionado pelo usuário para indexação.

Campos observados:

- `caminho_pdf`: caminho local escolhido na UI.
- `nome_arquivo`: `os.path.basename(caminho_pdf)`.
- `texto_total`: texto extraído de todas as páginas com marcador `--- Página N ---`.

### Chunk documental

Unidade persistida no ChromaDB.

Campos/metadados:

- `id`: padrão `fase_{fase}_{nome_arquivo}_{i}_{uuid}`.
- `document`: texto do chunk.
- `embedding`: vetor gerado pelo SentenceTransformer.
- `metadata.arquivo`: nome do PDF.
- `metadata.fase`: número inteiro da fase.
- `metadata.chunk`: índice sequencial do chunk.
- `metadata.total_chunks`: total de chunks do documento.

### Atividade principal

Texto livre digitado pelo usuário para representar o escopo principal analisado.

### Fase candidata

Texto livre digitado pelo usuário, associado à posição da caixa de texto na UI.

Campos internos:

- `numero_fase`: índice de 1 a 5.
- `texto_fase`: descrição textual da fase.

### Análise semântica

Objeto intermediário produzido por fase candidata.

Campos principais:

- `numero_fase`.
- `texto_fase`.
- `score_fase`.
- `score_documento`.
- `interpretacao_score_fase`.
- `interpretacao_score_documento`.
- `chunks_documento`.
- `tem_documento`.
- `qualidade_informacao` e atributos relacionados na versão v3/v4.

### Decisão LLM

Contrato esperado de saída JSON do LLM.

Campos:

- `fase`.
- `esta_contida`: `Sim`, `Parcialmente`, `Não` ou `ERRO LLM` em fallback.
- `grau_relacao`: `Alto`, `Médio`, `Baixo` ou fallback.
- `evidencia_documento`: `Confirma`, `Enfraquece`, `Sem evidência`, `Não avaliado`.
- `qualidade_informacao`.
- `alerta_qualidade`.
- `justificativa`.

## Relacionamentos

- Um PDF gera muitos chunks.
- Cada chunk pertence a uma fase via metadado `fase`.
- Uma atividade principal é comparada com uma lista de fases candidatas.
- Cada fase candidata consulta até `TOP_K_CHUNKS` chunks no ChromaDB filtrados pela própria fase.
- Cada decisão LLM deve corresponder a uma fase candidata.

## Origem dos dados

- PDFs: selecionados manualmente pelo usuário.
- Fase do documento: digitada manualmente na interface de indexação.
- Atividade principal e fases candidatas: digitadas manualmente na interface RAG.
- Evidências documentais: recuperadas do ChromaDB.
- Decisão final: retornada pelo Ollama a partir do prompt construído.

## Persistência

- Persistência vetorial local em ChromaDB.
- Versões antigas usam caminho absoluto Windows.
- `Nova_versão_v4.py` usa `PASTA_CHROMA` por variável de ambiente com default `./chroma_db`.
- Não há persistência relacional dos resultados da análise.

## Observações e inconsistências

- O indexador ainda usa caminho absoluto Windows, diferente do default relativo da v4.
- A conversão de distância para similaridade mudou entre versões: a primeira usa `1 / (1 + distancia)`; v2+ usa `1 - distancia` limitado a `[0, 1]`.
- O contrato JSON depende de aderência do LLM ao prompt; há fallback parcial para fases faltantes.
- Não há schema formal, validação com Pydantic ou dataclasses.

