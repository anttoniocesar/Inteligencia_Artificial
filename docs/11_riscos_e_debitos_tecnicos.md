# Riscos e débitos técnicos

## Riscos técnicos encontrados

### Múltiplas versões do mesmo aplicativo

Impacto: manutenção pode ocorrer no arquivo errado, gerando divergência de regra e comportamento.

Correção futura: escolher versão canônica, arquivar/remover versões históricas ou transformá-las em changelog.

### Caminhos locais divergentes

Impacto: indexador pode gravar em uma base ChromaDB enquanto v4 consulta outra.

Correção futura: centralizar configuração compartilhada.

### Ausência de testes automatizados

Impacto: refatorações podem quebrar regras críticas sem detecção.

Correção futura: iniciar suíte `pytest` cobrindo regras puras e integrações com mocks.

### Prompt como regra de negócio primária

Impacto: regras importantes ficam difíceis de versionar, testar e validar deterministicamente.

Correção futura: extrair regras determinísticas para código e manter prompt apenas para julgamento semântico.

### Dependência de LLM local

Impacto: resultado pode variar conforme modelo instalado, versão, disponibilidade do Ollama e parâmetros.

Correção futura: registrar versão do modelo, criar testes com mocks e observabilidade da resposta bruta.

### Parsing JSON frágil

Impacto: respostas parcialmente inválidas podem falhar ou extrair JSON errado.

Correção futura: validar schema, usar retries e prompt de reparo controlado.

### Operação destrutiva sem confirmação

Impacto: `limpar_chroma.py` apaga todas as coleções sem prompt de confirmação.

Correção futura: exigir confirmação explícita, dry-run e backup.

### Ausência de deduplicação

Impacto: o mesmo PDF/fase pode ser indexado repetidas vezes, poluindo resultados.

Correção futura: hash de arquivo/conteúdo e política de reindexação.

### Ausência de OCR

Impacto: PDFs escaneados não geram evidência documental, reduzindo qualidade da análise.

Correção futura: pipeline opcional de OCR.

### Sem logging estruturado

Impacto: diagnóstico depende de prints e mensagens na UI.

Correção futura: adotar `logging` com níveis e contexto.

## Duplicidades

- Funções de RAG repetidas em quatro versões.
- Configurações repetidas em indexador, RAG e utilitários.
- Prompt de decisão duplicado entre v2/v3/v4 com variações.

## Acoplamentos

- UI acoplada a aplicação e infraestrutura.
- Regras do prompt acopladas ao código que chama Ollama.
- ChromaDB e modelo carregados como globais nas versões antigas.

## Arquivos grandes demais

- `Nova_versão_v4.py` concentra configuração, domínio, integração, prompt e UI em um único arquivo.
- v2/v3 também são arquivos monolíticos.

## Ausência de validação

- Não há schema para decisão LLM.
- Não há validação formal de metadados no ChromaDB.
- Não há validação se a fase indexada existe/será consultada.

## Riscos de manutenção

- Regras críticas vivem em texto de prompt longo.
- Evolução histórica por cópia dificulta diff semântico.
- Dependências e ambiente não estão declarados em `requirements.txt` ou similar.

