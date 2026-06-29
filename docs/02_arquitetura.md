# Arquitetura

## Stack utilizada

- Linguagem: Python.
- UI desktop: Tkinter e `ttk`.
- Vetorização: `sentence-transformers` com modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- Banco vetorial: ChromaDB `PersistentClient`.
- Leitura de PDF: `pypdf.PdfReader`.
- Similaridade: `sklearn.metrics.pairwise.cosine_similarity`.
- LLM local: Ollama via `requests.post` em `/api/generate`.
- Serialização e parsing: `json` e regex.

## Estrutura de pastas

```text
/
├── Indexador_PDF/
│   └── Indexador.py
├── Rede_Neural_CAPEX/
│   ├── Nova_Versão.py
│   ├── Nova_versão_v2.py
│   ├── Nova_versão_v3.py
│   └── Nova_versão_v4.py
├── limpar_chroma.py
├── verificar_chroma.py
└── docs/
```

## Separação de responsabilidades observada

- `Indexador_PDF/Indexador.py`: ingestão e persistência de documentos.
- `Rede_Neural_CAPEX/Nova_versão_v4.py`: versão mais consolidada da aplicação RAG, com carregamento lazy, tipagem e `main()` protegido.
- `Rede_Neural_CAPEX/Nova_Versão.py`, `v2`, `v3`: versões históricas/evolutivas com regras parcialmente duplicadas.
- `verificar_chroma.py`: diagnóstico simples da base ChromaDB.
- `limpar_chroma.py`: operação destrutiva de limpeza completa das coleções.

## Camadas do sistema

A separação é mais conceitual do que física:

1. **Configuração:** constantes e variáveis de ambiente.
2. **Infraestrutura:** ChromaDB, modelo SentenceTransformer, Ollama e leitura de PDF.
3. **Domínio/Application:** regras de score, qualidade da informação, montagem de contexto, validação de decisões.
4. **UI:** widgets Tkinter, entradas, botões, tabela e mensagens.

## Dependências principais

- `chromadb` para persistência e busca vetorial.
- `sentence_transformers` para embeddings.
- `scikit-learn` para similaridade cosseno direta entre atividade e fases.
- `requests` para integração com Ollama.
- `pypdf` para extração de texto.

## Padrão arquitetural identificado

- **Script desktop monolítico por caso de uso.**
- **RAG local orientado a funções.**
- **Evolução por cópia de arquivo:** as versões `Nova_Versão.py`, `v2`, `v3` e `v4` preservam snapshots de evolução.

## Recomendações para manter consistência

- Tratar `Nova_versão_v4.py` como referência executável atual até decisão formal.
- Evitar criar novas versões por cópia; preferir módulos compartilhados.
- Manter integrações externas isoladas de regras de decisão.
- Preservar o filtro por metadado `fase` nas consultas ChromaDB.
- Centralizar configuração em variáveis de ambiente ou arquivo de configuração.
- Não misturar regras de negócio novas diretamente em callbacks Tkinter.

