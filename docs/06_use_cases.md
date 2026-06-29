# Use cases

## UC01 — Indexar PDF industrial

- **Responsabilidade:** persistir evidências documentais vetorizadas por fase.
- **Entradas:** caminho do PDF, número da fase.
- **Saídas:** documentos/chunks no ChromaDB.
- **Dependências:** `pypdf`, SentenceTransformer, ChromaDB.
- **Regras acionadas:** fase numérica, chunking, embeddings, metadados obrigatórios.
- **Testes unitários possíveis:** extração vazia, chunking com sobreposição, geração de metadados, erro quando fase inválida.

## UC02 — Consultar ChromaDB por fase

- **Responsabilidade:** recuperar trechos mais próximos para uma consulta e uma fase específica.
- **Entradas:** consulta textual, número da fase, `top_k`.
- **Saídas:** lista de chunks ranqueados com metadados e similaridade.
- **Dependências:** SentenceTransformer, ChromaDB.
- **Regras acionadas:** filtro `where` por fase e conversão distância/similaridade.
- **Testes unitários possíveis:** chamada ChromaDB com filtro correto, conversão de distância inválida, lista vazia.

## UC03 — Calcular análise semântica

- **Responsabilidade:** combinar score textual, evidências documentais e qualidade da informação.
- **Entradas:** atividade principal, lista de fases candidatas.
- **Saídas:** lista de análises por fase.
- **Dependências:** embeddings, `cosine_similarity`, consulta ChromaDB.
- **Regras acionadas:** interpretação de score, qualidade de informação, presença de documento.
- **Testes unitários possíveis:** score com mocks, qualidade baixa/média/alta, ordenação por fase preservada.

## UC04 — Decidir escopo com LLM

- **Responsabilidade:** obter decisão estruturada de pertencimento ao escopo.
- **Entradas:** atividade principal e análise semântica.
- **Saídas:** decisões JSON validadas por fase.
- **Dependências:** Ollama HTTP, prompt, parser JSON.
- **Regras acionadas:** hierarquia de análise, classificação de natureza, regras de evidência documental.
- **Testes unitários possíveis:** parsing JSON puro, parsing JSON embutido em texto, fallback para fase faltante, erro de JSON inválido.

## UC05 — Exibir resultado na UI

- **Responsabilidade:** apresentar tabela e detalhes para o usuário.
- **Entradas:** análise semântica e decisões LLM.
- **Saídas:** linhas no `Treeview` e texto detalhado.
- **Dependências:** Tkinter.
- **Regras acionadas:** exibição `Sim/Não` para documento encontrado, truncamento textual.
- **Testes possíveis:** testes de apresentação com camada desacoplada no futuro; hoje é difícil testar sem UI.

## UC06 — Verificar base vetorial

- **Responsabilidade:** auditar coleções existentes e contagem de registros.
- **Entradas:** caminho ChromaDB.
- **Saídas:** prints no terminal.
- **Dependências:** ChromaDB.
- **Testes possíveis:** mock de cliente ChromaDB.

## UC07 — Limpar base vetorial

- **Responsabilidade:** apagar todas as coleções do ChromaDB local.
- **Entradas:** caminho ChromaDB.
- **Saídas:** coleções removidas.
- **Dependências:** ChromaDB.
- **Testes possíveis:** garantir que todas as coleções listadas sejam removidas; adicionar confirmação antes de uso real.

