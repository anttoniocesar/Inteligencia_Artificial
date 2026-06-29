# Testes e TDD

## Situação atual dos testes

Não há arquivos de teste automatizado identificados no repositório. Também não há configuração de `pytest`, CI ou relatório de cobertura.

## Bibliotecas de teste usadas

Nenhuma biblioteca de teste é usada atualmente no código versionado.

## Lacunas de cobertura

- Chunking e extração de texto.
- Geração de metadados e IDs.
- Conversão distância/similaridade.
- Interpretação de score.
- Avaliação de qualidade da informação.
- Parsing de JSON do LLM.
- Validação de decisões faltantes.
- Tratamento de erro de Ollama.
- Consulta ChromaDB com filtro de fase.
- Fluxos UI com entradas inválidas.
- Operações destrutivas de limpeza ChromaDB.

## Testes unitários recomendados

- `dividir_em_chunks` com texto vazio, texto curto, texto longo e sobreposição.
- `distancia_para_similaridade` para valores válidos, negativos, maiores que 1 e inválidos.
- `interpretar_score` nos limites exatos.
- `avaliar_qualidade_informacao` para baixa, média e alta qualidade.
- `extrair_json` com JSON puro, JSON cercado por texto e JSON inválido.
- `validar_decisoes` com fase faltante, fase inválida e fase sem documento.

## Testes de integração recomendados

- Indexar PDF mínimo gerado em teste e consultar ChromaDB temporário.
- Simular Ollama com servidor fake/local ou monkeypatch de `requests.post`.
- Validar que a consulta ChromaDB inclui `where={"fase": int(numero_fase)}`.
- Validar criação de coleção temporária sem usar diretório real do usuário.

## Estratégia TDD para novas features

1. Extrair regra ou integração para função/módulo testável.
2. Escrever teste de comportamento atual antes da refatoração.
3. Criar teste da nova regra esperada.
4. Implementar a menor mudança possível.
5. Rodar testes e revisar documentação em `/docs`.

## Padrão esperado para nomes de testes

Sugestão para futuro `pytest`:

- Arquivos: `tests/test_<modulo>.py`.
- Funções: `test_<funcao>__<cenario>__<resultado_esperado>()`.

Exemplos:

- `test_dividir_em_chunks__texto_vazio__retorna_lista_vazia`.
- `test_validar_decisoes__fase_faltante__adiciona_erro_llm`.
- `test_avaliar_qualidade_informacao__descricao_curta__retorna_baixa`.

