# Serviços e integrações

## ChromaDB

- Cliente usado: `chromadb.PersistentClient`.
- Coleção padrão: `documentos_industriais`.
- Metadado crítico: `fase`.
- Operações usadas:
  - `get_or_create_collection`;
  - `add`;
  - `query`;
  - `list_collections`;
  - `delete_collection`.

### Contrato de dados de indexação

- `ids`: lista de IDs únicos por chunk.
- `documents`: lista de textos.
- `embeddings`: lista de vetores.
- `metadatas`: lista de dicionários com arquivo, fase, chunk e total.

### Riscos de falha

- Caminho local inexistente ou sem permissão.
- Divergência de caminho entre indexador e aplicação RAG.
- Coleção vazia ou fase sem documentos.
- Distância retornada com semântica diferente da assumida.

## SentenceTransformer

- Modelo padrão: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Cache local: `./modelo_sentence_transformer_multilingual`.
- v4 permite configurar por `MODELO_EMBEDDING` e `PASTA_MODELO`.

### Riscos

- Primeiro carregamento pode exigir rede se modelo não estiver salvo localmente.
- Modelo local pode ficar inconsistente se diretório for corrompido.
- Versões diferentes de bibliotecas podem alterar embeddings.

## Ollama

- Modelo padrão: `qwen2.5`.
- URL padrão: `http://127.0.0.1:11434/api/generate`.
- Requisição usa `stream=False`, `temperature=0.1`, `num_predict=900` na v4 e `num_ctx=4096`.
- Timeout: 600 segundos.

### Contrato esperado de resposta

- JSON HTTP com campo `response` contendo texto.
- O texto deve conter array JSON de decisões.

### Tratamento de erro atual

- Erro de conexão vira mensagem amigável.
- HTTP status inválido chama `raise_for_status`.
- Ausência de `response` gera erro.
- JSON inválido gera erro técnico.

## PDF local

- Leitura por `pypdf.PdfReader`.
- O texto extraído é concatenado por página.

### Riscos

- PDFs escaneados sem OCR podem não produzir texto.
- Extração pode perder tabelas, layout e contexto.
- Não há pré-processamento semântico avançado.

## SharePoint, banco relacional e arquivos externos

- Não há integração SharePoint identificada no código.
- Não há banco relacional identificado.
- Arquivos externos são PDFs selecionados manualmente e diretórios locais de modelo/ChromaDB.

