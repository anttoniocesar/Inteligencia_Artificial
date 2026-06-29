# Regras de negócio

## Regras identificadas no código

### Indexação por fase

- Todo PDF indexado exige uma fase numérica.
- Chunks são gravados com metadado `fase` inteiro.
- Consultas documentais usam filtro `where={"fase": int(numero_fase)}`.

### Chunking documental

- O texto extraído do PDF é dividido em chunks de 900 caracteres com sobreposição de 150 caracteres.
- PDFs sem texto extraível geram erro.
- Textos sem chunks geram erro.

### Similaridade fase/atividade

- A atividade principal é vetorizada e comparada por cosseno com o texto de cada fase candidata.
- O score textual fase/atividade é independente do ChromaDB.

### Similaridade documental

- A consulta ao ChromaDB usa embedding da atividade principal na v2/v3/v4.
- A busca é filtrada pela fase candidata.
- O melhor chunk define `score_documento`.

### Interpretação de score

- v2/v3/v4 usam faixas: `>=0.85 Muito alta`, `>=0.70 Alta`, `>=0.55 Média`, `>=0.40 Baixa`, senão `Muito baixa`.
- A primeira versão usa limiares diferentes: `>=0.75 Alta proximidade`, `>=0.50 Média`, `>=0.30 Baixa`.

### Qualidade da informação

- v3/v4 calculam qualidade por quantidade de palavras, presença de campos padronizados, verbos de ação e termos técnicos.
- Qualidade `Alta`, `Média` ou `Baixa` altera recomendação e alerta.

### Decisão de escopo pelo LLM

O prompt da v4 instrui o LLM a avaliar:

1. natureza da atividade principal;
2. natureza da fase candidata;
3. objetivos técnicos;
4. escopo de intervenção;
5. equipamentos e sistemas;
6. relação declarada com o projeto;
7. evidências documentais como complemento.

Categorias de natureza usadas no prompt:

- Engenharia;
- Aquisição;
- Execução;
- Operação / Manutenção;
- Modernização.

Classificações de saída:

- `esta_contida`: `Sim`, `Parcialmente`, `Não`.
- `grau_relacao`: `Alto`, `Médio`, `Baixo`.
- `evidencia_documento`: `Confirma`, `Enfraquece`, `Sem evidência`.

### Regras de evidência documental

- Se não houver documento recuperado, a evidência deve ser `Sem evidência`.
- Ausência de evidência documental não deve ser tratada como ausência de relação com o projeto.
- A decisão deve priorizar comparação técnica entre atividade principal e fase candidata.

## Onde cada regra está implementada

- Indexação, chunking e metadados: `Indexador_PDF/Indexador.py`.
- Similaridade, busca por fase, qualidade, prompt e validação de decisão: principalmente `Rede_Neural_CAPEX/Nova_versão_v4.py`.
- Versões duplicadas/anteriores: `Nova_Versão.py`, `Nova_versão_v2.py`, `Nova_versão_v3.py`.

## Regras duplicadas

- Carregamento do modelo de embedding.
- Conexão ChromaDB.
- `interpretar_score`.
- `distancia_para_similaridade`.
- `consultar_chromadb_por_fase`.
- `calcular_analise_semantica`.
- `consultar_llm`.
- `extrair_json`.
- `validar_decisoes`.
- UI Tkinter de RAG nas versões antigas.

## Regras que deveriam sair da UI

- Validação de entradas de atividade/fases.
- Construção da lista de fases válidas.
- Orquestração completa do fluxo RAG.
- Formatação de decisões para tabela.

## Pontos pendentes de validação humana

- Se os limiares de score são adequados ao domínio CAPEX.
- Se os termos técnicos e verbos de ação cobrem os casos reais.
- Se `Parcialmente` deve ser usado para atividades auxiliares conforme descrito no prompt.
- Se `TOP_K_CHUNKS = 3` é suficiente.
- Se a fase digitada no indexador deve corresponder obrigatoriamente às caixas 1..5 da UI RAG.

