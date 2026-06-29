# Contexto do projeto

## Objetivo do sistema

O projeto implementa uma solução local de IA para análise de escopo técnico de atividades/fases de projetos industriais, usando:

- indexação de documentos PDF em ChromaDB;
- embeddings multilingual Sentence Transformers;
- recuperação semântica filtrada por `fase`;
- LLM local via Ollama para decidir se fases candidatas pertencem ao escopo da atividade principal;
- interfaces desktop simples em Tkinter.

## Problema que resolve

O código busca apoiar a comparação entre uma **atividade principal** e até cinco **fases candidatas**, combinando similaridade semântica, evidências documentais recuperadas e regras explícitas de prompt para classificar relação de escopo.

## Público usuário

- Analistas de engenharia, manutenção, confiabilidade, CAPEX ou gestão de projetos industriais.
- Usuários técnicos que precisam indexar documentos por fase e consultar evidências locais.
- **Inferência:** o ambiente esperado é Windows corporativo, pois versões antigas usam caminho absoluto `D:\Users\...` para ChromaDB.

## Principais módulos

- **Indexador PDF:** extrai texto de PDFs, divide em chunks, gera embeddings e persiste documentos em ChromaDB com metadados.
- **RAG CAPEX:** consulta ChromaDB por fase, calcula similaridade entre atividade e fases, chama Ollama e exibe decisão estruturada.
- **Utilitários ChromaDB:** verificam coleções/registros e apagam coleções.

## Escopo atual

- Aplicação desktop local, sem backend web.
- Persistência vetorial local via ChromaDB.
- LLM local via endpoint HTTP do Ollama.
- Indexação manual de PDF por seleção em interface Tkinter.
- Análise manual de uma atividade principal contra até cinco fases candidatas.

## O que o sistema ainda não faz

- Não possui API HTTP própria.
- Não possui autenticação/autorização.
- Não possui banco relacional.
- Não possui pipeline automatizado de ingestão em lote.
- Não possui testes automatizados versionados.
- Não possui empacotamento/instalador.
- Não possui configuração central compartilhada entre todos os scripts.
- Não possui controle transacional ou deduplicação de documentos indexados.

