# Gráfico de estoque por ano

Este exemplo cria um gráfico em SVG para comparar anos com a quantidade de itens disponíveis no estoque.

> **Importante:** este arquivo `README.md` é apenas um manual de orientação. Ele não deve ser executado no Python nem copiado inteiro para o `Modelo_1.py`. O código que deve ser executado está no arquivo `grafico_estoque.py`.

## Para que serve este arquivo?

Este arquivo serve como documentação do projeto. Ele explica:

- qual é o objetivo do gráfico;
- qual arquivo Python deve ser executado;
- como evitar o erro `SyntaxError`;
- onde alterar os anos e as quantidades de itens do estoque.

Se você quiser apenas gerar o gráfico, use somente o arquivo `grafico_estoque.py`.

## Plataforma em Python

Se você quer executar tudo como arquivo `.py`, use `plataforma_grafico.py`:

```bash
python Graficos_Estoque/plataforma_grafico.py
```

Esse arquivo abre uma janela com o gráfico em cima, os campos **Eixo X** e **Eixo Y** abaixo e o botão **Gerar gráfico**. Não copie o conteúdo de `plataforma_grafico.html` para um arquivo Python, porque linhas de CSS como `max-width: 980px;` geram `SyntaxError` em Python.

## Plataforma interativa

Além do script Python, o arquivo `plataforma_grafico.html` abre uma página no navegador com:

- o gráfico na parte superior;
- campos visíveis para preencher os valores do eixo X e do eixo Y;
- preenchimento de vários pontos, usando um valor por linha em cada campo;
- botão **Gerar gráfico** para redesenhar o gráfico com os dados informados.

Para usar, abra `Graficos_Estoque/plataforma_grafico.html` no navegador.

## Correção do erro `SyntaxError: invalid syntax`

O erro abaixo acontece quando um texto explicativo é colado diretamente dentro de um arquivo `.py` sem estar comentado:

```text
SyntaxError: invalid syntax
Este exemplo cria um gráfico em SVG...
```

Em Python, textos explicativos precisam estar:

- em comentários, começando com `#`; ou
- dentro de aspas, por exemplo `"""texto"""`.

Para evitar esse erro, copie apenas o conteúdo do arquivo `grafico_estoque.py` para o seu `Modelo_1.py`, ou execute o arquivo diretamente conforme o passo abaixo.

## Como usar

Execute o script a partir da raiz do repositório:

```bash
python Graficos_Estoque/grafico_estoque.py
```

O arquivo `grafico_estoque.svg` será criado dentro da pasta `Graficos_Estoque`.

## Como alterar os dados

Edite as constantes no início de `grafico_estoque.py`:

- `ANOS`: lista dos anos ou períodos exibidos no eixo X.
- `ITENS_ESTOQUE`: lista das quantidades disponíveis no estoque para cada ano.
- `ARQUIVO_SAIDA`: nome do arquivo SVG gerado.

As listas `ANOS` e `ITENS_ESTOQUE` precisam ter o mesmo tamanho.
