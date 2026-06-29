# Fluxos principais

## Fluxo 1 — Indexar PDF por fase

1. Usuário abre o indexador Tkinter.
2. Usuário seleciona um arquivo PDF.
3. Usuário informa número da fase.
4. Sistema valida se há caminho de PDF.
5. Sistema valida se a fase é numérica.
6. Sistema extrai texto de todas as páginas com `PdfReader`.
7. Sistema divide texto em chunks.
8. Sistema gera embeddings dos chunks.
9. Sistema cria IDs únicos e metadados.
10. Sistema adiciona documentos, embeddings e metadados na coleção ChromaDB.
11. UI mostra arquivo, fase, total de chunks, caminho ChromaDB e coleção.

### Saídas esperadas

- Chunks persistidos na coleção `documentos_industriais`.
- Metadados com `arquivo`, `fase`, `chunk`, `total_chunks`.

### Validações

- PDF obrigatório.
- Fase numérica obrigatória.
- Texto extraível obrigatório.
- Pelo menos um chunk obrigatório.

## Fluxo 2 — Executar análise RAG local

1. Usuário informa atividade principal.
2. Usuário informa uma ou mais fases candidatas, até cinco.
3. Sistema valida atividade principal obrigatória.
4. Sistema valida pelo menos uma fase candidata.
5. Sistema calcula embeddings da atividade e das fases.
6. Sistema calcula similaridade cosseno fase/atividade.
7. Para cada fase, sistema consulta ChromaDB filtrando por `fase`.
8. Sistema calcula qualidade da informação da fase.
9. Sistema monta contexto para o LLM.
10. Sistema chama Ollama com prompt estruturado.
11. Sistema tenta extrair JSON da resposta.
12. Sistema valida se todas as fases receberam decisão.
13. UI preenche tabela e área de resultado detalhado.

### Telas envolvidas

- Tela `RAG Local - ChromaDB Filtrado por Fase`.
- Campos: atividade principal, cinco fases candidatas, botão de execução, tabela e texto detalhado.

### Alterações de status

Não há status persistido em banco. A mudança ocorre apenas no estado da UI:

- aguardando entrada;
- consultando ChromaDB;
- exibindo resultado;
- exibindo erro técnico.

## Fluxo 3 — Verificar ChromaDB

1. Script abre `PersistentClient` no caminho configurado.
2. Lista coleções.
3. Para cada coleção, imprime nome e quantidade de registros.

## Fluxo 4 — Limpar ChromaDB

1. Script abre `PersistentClient` no caminho configurado.
2. Lista coleções.
3. Apaga cada coleção.
4. Imprime mensagem final.

### Risco

Este fluxo é destrutivo e não pede confirmação.

