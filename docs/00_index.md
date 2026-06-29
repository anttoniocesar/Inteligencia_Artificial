# Índice da documentação viva

Esta pasta é a fonte de verdade técnica do projeto **Inteligencia_Artificial**. Ela documenta o comportamento observado no código atual, sem propor mudanças funcionais imediatas.

## Ordem recomendada de leitura

1. `01_contexto_do_projeto.md` — entende objetivo, usuários e escopo.
2. `02_arquitetura.md` — explica stack, módulos, camadas e dependências.
3. `03_modelo_de_dados.md` — descreve entidades, contratos e persistência.
4. `04_regras_de_negocio.md` — consolida regras implementadas e pendências de validação.
5. `05_fluxos_principais.md` — detalha fluxos operacionais ponta a ponta.
6. `06_use_cases.md` — organiza casos de uso e testes unitários possíveis.
7. `07_componentes_ui.md` — descreve telas Tkinter e riscos de acoplamento.
8. `08_servicos_e_integracoes.md` — documenta ChromaDB, Ollama, PDF e modelo de embeddings.
9. `09_testes_e_tdd.md` — registra estado de testes e estratégia TDD.
10. `10_padroes_de_codigo.md` — registra convenções atuais e padrões a manter/evitar.
11. `11_riscos_e_debitos_tecnicos.md` — lista riscos, impacto e correções futuras.
12. `12_roadmap_tecnico.md` — sugere evolução técnica ordenada.

## Finalidade dos arquivos

- Servir como memória arquitetural para manutenção e evolução.
- Reduzir reinvestigação em prompts futuros.
- Apoiar TDD, refatorações e análise de impacto.
- Separar fatos encontrados no código de inferências e pendências humanas.

## Como usar em prompts futuros

Use sempre um comando inicial semelhante a:

> Leia primeiro os arquivos em `/docs` como fonte de verdade. Depois execute a tarefa abaixo respeitando a arquitetura e as regras documentadas.

Ao pedir novas features ou refatorações, cite os documentos relevantes. Exemplos:

- Para criar testes: referencie `09_testes_e_tdd.md` e `06_use_cases.md`.
- Para alterar regras de decisão: referencie `04_regras_de_negocio.md`.
- Para mexer em UI: referencie `07_componentes_ui.md`.
- Para integrações: referencie `08_servicos_e_integracoes.md`.

## Escopo desta documentação

A documentação cobre os scripts Python existentes no repositório:

- `Indexador_PDF/Indexador.py`.
- `Rede_Neural_CAPEX/Nova_Versão.py`.
- `Rede_Neural_CAPEX/Nova_versão_v2.py`.
- `Rede_Neural_CAPEX/Nova_versão_v3.py`.
- `Rede_Neural_CAPEX/Nova_versão_v4.py`.
- `verificar_chroma.py`.
- `limpar_chroma.py`.

