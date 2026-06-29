# Padrões de código

## Convenções identificadas

- Código e nomes em português.
- Separadores por comentários com `# =========================`.
- Constantes globais em maiúsculas.
- Funções proceduralmente organizadas por responsabilidade.
- UI Tkinter criada diretamente no script.
- Mensagens de usuário em português.

## Nomenclatura

- Variáveis com snake_case em português: `frase_principal`, `fases_validas`, `analise_semantica`.
- Constantes: `MODELO_EMBEDDING`, `PASTA_CHROMA`, `NOME_COLECAO`, `TOP_K_CHUNKS`.
- Classe v4: `RagLocalApp`.

## Organização de imports

- Bibliotecas padrão primeiro.
- Bibliotecas externas depois.
- v4 adiciona `from __future__ import annotations`, `Path` e `typing.Any`.

## Estilo de funções/classes

- v1/v2/v3 usam funções e widgets globais.
- v4 encapsula UI em classe e protege execução com `if __name__ == "__main__"`.
- v4 adiciona type hints em várias funções.
- Recursos pesados em v4 são carregados de forma lazy.

## Tratamento de erro

- Erros técnicos são exibidos em áreas de texto ou messagebox.
- Conexão com Ollama tem mensagem específica.
- Demais exceções são capturadas genericamente na execução UI.
- Scripts utilitários não têm confirmação ou tratamento robusto.

## Padrões que devem ser mantidos

- Mensagens claras em português.
- Configuração por variáveis de ambiente como na v4.
- `main()` protegido para evitar execução ao importar.
- Funções puras para regras testáveis quando possível.
- Filtro obrigatório por fase em consultas documentais.

## Padrões que devem ser evitados

- Criar novas cópias versionadas do mesmo script.
- Caminhos absolutos locais no código.
- Carregar modelo/ChromaDB no import de módulos testáveis.
- Misturar regra de negócio com callback de UI.
- Deixar scripts destrutivos sem confirmação.
- Duplicar prompts longos em vários arquivos.

