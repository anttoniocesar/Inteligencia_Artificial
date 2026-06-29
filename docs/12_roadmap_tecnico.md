# Roadmap técnico

## Ordem sugerida de evolução

1. Definir `Nova_versão_v4.py` como versão canônica ou escolher outra formalmente.
2. Criar `requirements.txt` ou `pyproject.toml` com dependências e versões mínimas.
3. Centralizar configuração em módulo único.
4. Extrair funções puras de regra para módulos testáveis.
5. Criar suíte inicial de testes unitários.
6. Criar testes de integração com ChromaDB temporário e Ollama mockado.
7. Separar UI, application services e infraestrutura.
8. Adicionar confirmação/dry-run ao script de limpeza.
9. Implementar deduplicação/reindexação controlada.
10. Melhorar observabilidade e logs.

## Quick wins

- Adicionar documentação de setup e variáveis de ambiente.
- Criar testes para `interpretar_score`, `distancia_para_similaridade`, `extrair_json` e `avaliar_qualidade_informacao`.
- Parametrizar `PASTA_CHROMA` no indexador e utilitários.
- Adicionar `if __name__ == "__main__"` ao indexador e utilitários.
- Renomear scripts com nomes ASCII consistentes em uma etapa planejada.

## Refatorações futuras

- Módulo `config.py`.
- Módulo `embeddings.py`.
- Módulo `chroma_repository.py`.
- Módulo `pdf_indexer.py`.
- Módulo `rag_use_cases.py`.
- Módulo `llm_client.py`.
- Módulo `decision_rules.py`.
- UI separada em `ui_tkinter.py`.

## Melhorias de teste

- Cobertura mínima inicial para regras puras.
- Fixtures de ChromaDB temporário.
- Mocks de SentenceTransformer para testes rápidos.
- Contratos de JSON do LLM com schema.
- Testes de regressão para prompts críticos.

## Melhorias de arquitetura

- Trocar globais por injeção de dependências.
- Encapsular ChromaDB em repositório.
- Encapsular Ollama em client com retry, timeout e erro tipado.
- Separar prompt template de lógica Python.
- Criar DTOs/dataclasses para `FaseCandidata`, `AnaliseSemantica` e `DecisaoLLM`.

## Itens que exigem decisão de negócio

- Limiar oficial de scores por tipo de decisão.
- Vocabulário oficial de natureza da atividade.
- Política para classificar `Parcialmente`.
- Critério de confiança mínimo para aceitar decisão sem revisão humana.
- Política de reindexação e deduplicação documental.
- Se evidência documental deve ser obrigatória para alguns tipos de decisão.
- Se o sistema deve salvar histórico/auditoria de análises.

