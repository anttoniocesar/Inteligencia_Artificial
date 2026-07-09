from __future__ import annotations

"""Gera um gráfico SVG de anos versus itens disponíveis no estoque.

Copie este arquivo inteiro para o VS Code se quiser testar em outro projeto.
Textos explicativos soltos, sem começar com ``#`` ou sem estarem dentro de
aspas triplas como esta documentação, causam ``SyntaxError`` em Python.
"""

from pathlib import Path
from statistics import mean


# =========================
# CONFIGURAÇÕES
# =========================

ANOS = list(range(1, 13))
ITENS_ESTOQUE = [3, 2, 4, 2, 4, 5, 6, 1, 2, 4, 1, 5]
ARQUIVO_SAIDA = Path(__file__).with_name("grafico_estoque.svg")

LARGURA = 640
ALTURA = 185
MARGEM_ESQUERDA = 40
MARGEM_DIREITA = 20
MARGEM_SUPERIOR = 48
MARGEM_INFERIOR = 42


# =========================
# FUNÇÕES
# =========================

def definir_cor_fundo(item: int, media_itens: float) -> str:
    """Retorna a cor da faixa de fundo conforme o nível de estoque."""
    if item < media_itens:
        return "#d9f2df"

    if item == media_itens:
        return "#fff1c7"

    return "#f5cccc"


def validar_dados(anos: list[int], itens_estoque: list[int]) -> None:
    """Valida os dados usados na criação do gráfico."""
    if len(anos) != len(itens_estoque):
        raise ValueError("As listas de anos e itens de estoque devem ter o mesmo tamanho.")

    if not anos:
        raise ValueError("Informe pelo menos um ano para criar o gráfico.")


def converter_x(indice: int, largura_util: int, total_anos: int) -> float:
    """Converte a posição do item para o centro da sua faixa no eixo X."""
    largura_faixa = largura_util / total_anos
    return MARGEM_ESQUERDA + (indice + 0.5) * largura_faixa


def converter_y(item: float, maior_item: int, altura_util: int) -> float:
    """Converte a quantidade em estoque para a coordenada Y do SVG."""
    return MARGEM_SUPERIOR + altura_util - (item / maior_item) * altura_util


def criar_grafico_estoque(
    anos: list[int],
    itens_estoque: list[int],
    arquivo_saida: Path = ARQUIVO_SAIDA,
) -> Path:
    """Cria um gráfico SVG de anos versus itens disponíveis no estoque."""
    validar_dados(anos, itens_estoque)

    media_itens = mean(itens_estoque)
    maior_item = max(max(itens_estoque), 1)
    total_anos = len(anos)
    largura_util = LARGURA - MARGEM_ESQUERDA - MARGEM_DIREITA
    altura_util = ALTURA - MARGEM_SUPERIOR - MARGEM_INFERIOR
    largura_faixa = largura_util / total_anos
    y_media = converter_y(media_itens, maior_item, altura_util)

    elementos = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" viewBox="0 0 {LARGURA} {ALTURA}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    for indice, item in enumerate(itens_estoque):
        x = MARGEM_ESQUERDA + indice * largura_faixa
        elementos.append(
            f'<rect x="{x:.2f}" y="{MARGEM_SUPERIOR}" width="{largura_faixa:.2f}" height="{altura_util}" fill="{definir_cor_fundo(item, media_itens)}"/>'
        )

    for indice, ano in enumerate(anos):
        x = converter_x(indice, largura_util, total_anos)
        elementos.append(
            f'<line x1="{x:.2f}" y1="{MARGEM_SUPERIOR}" x2="{x:.2f}" y2="{MARGEM_SUPERIOR + altura_util}" stroke="#9e9e9e" stroke-dasharray="5 3" opacity="0.55"/>'
        )
        elementos.append(
            f'<text x="{x:.2f}" y="{ALTURA - 15}" text-anchor="middle" font-family="Arial" font-size="11" font-weight="bold">{ano}</text>'
        )

    for indice, item in enumerate(itens_estoque):
        x = converter_x(indice, largura_util, total_anos)
        y = converter_y(item, maior_item, altura_util)
        cor = "#d00000" if item == media_itens else "#3f3f3f"
        raio = 5.8 if item == media_itens else 5.2
        elementos.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{raio}" fill="{cor}"/>')

    elementos.extend([
        f'<line x1="{MARGEM_ESQUERDA}" y1="{y_media:.2f}" x2="{MARGEM_ESQUERDA + largura_util}" y2="{y_media:.2f}" stroke="#005f99" stroke-width="2"/>',
        f'<text x="{MARGEM_ESQUERDA + largura_util - 4}" y="{y_media - 6:.2f}" text-anchor="end" font-family="Arial" font-size="15" font-weight="bold">Média: {media_itens:g}</text>',
        f'<rect x="{MARGEM_ESQUERDA}" y="{MARGEM_SUPERIOR}" width="{largura_util}" height="{altura_util}" fill="none" stroke="black" stroke-width="1.5"/>',
        f'<text x="10" y="{MARGEM_SUPERIOR + 6}" font-family="Arial" font-size="11" font-weight="bold">und</text>',
        f'<text x="{LARGURA - 12}" y="{ALTURA - 18}" text-anchor="end" font-family="Arial" font-size="9" font-weight="bold">anos</text>',
        "</svg>",
    ])

    arquivo_saida.write_text("\n".join(elementos), encoding="utf-8")
    return arquivo_saida


def main() -> None:
    arquivo = criar_grafico_estoque(ANOS, ITENS_ESTOQUE)
    print(f"Gráfico criado em: {arquivo}")


if __name__ == "__main__":
    main()
