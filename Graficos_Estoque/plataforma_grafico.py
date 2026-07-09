from __future__ import annotations

"""Plataforma em Python para gerar o gráfico de estoque com campos de entrada.

Execute este arquivo com Python. Não copie o conteúdo do arquivo HTML para um
arquivo ``.py``, porque CSS como ``max-width: 980px;`` não é sintaxe Python.
"""

import tkinter as tk
from statistics import mean
from tkinter import messagebox


ANOS_INICIAIS = list(range(1, 13))
ITENS_INICIAIS = [3, 2, 4, 2, 4, 5, 6, 1, 2, 4, 1, 5]

LARGURA = 640
ALTURA = 185
MARGEM_ESQUERDA = 40
MARGEM_DIREITA = 20
MARGEM_SUPERIOR = 48
MARGEM_INFERIOR = 42


class PlataformaGrafico:
    """Interface gráfica com o gráfico acima e campos de dados abaixo."""

    def __init__(self, janela: tk.Tk) -> None:
        self.janela = janela
        self.janela.title("Plataforma de Gráfico de Estoque")
        self.janela.geometry("760x560")
        self.janela.minsize(700, 500)

        self.canvas = tk.Canvas(janela, width=LARGURA, height=ALTURA, bg="white", highlightthickness=0)
        self.canvas.pack(padx=20, pady=(20, 10))

        frame_campos = tk.Frame(janela)
        frame_campos.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(frame_campos, text="Eixo X (um valor por linha)", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(frame_campos, text="Eixo Y (um valor por linha)", font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )

        self.campo_x = tk.Text(frame_campos, height=10, width=28)
        self.campo_y = tk.Text(frame_campos, height=10, width=28)
        self.campo_x.grid(row=1, column=0, sticky="nsew")
        self.campo_y.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

        frame_campos.columnconfigure(0, weight=1)
        frame_campos.columnconfigure(1, weight=1)
        frame_campos.rowconfigure(1, weight=1)

        texto_ajuda = "Preencha a mesma quantidade de linhas nos dois campos. Depois clique em Gerar gráfico."
        tk.Label(janela, text=texto_ajuda, fg="#52606d").pack(padx=20, anchor="w")

        tk.Button(
            janela,
            text="Gerar gráfico",
            command=self.gerar_grafico_pelos_campos,
            bg="#005f99",
            fg="white",
            activebackground="#004b78",
            activeforeground="white",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=8,
        ).pack(padx=20, pady=14, anchor="w")

        self.preencher_dados_iniciais()
        self.gerar_grafico(ANOS_INICIAIS, ITENS_INICIAIS)

    def preencher_dados_iniciais(self) -> None:
        """Preenche os campos com dados de exemplo."""
        self.campo_x.insert("1.0", "\n".join(str(ano) for ano in ANOS_INICIAIS))
        self.campo_y.insert("1.0", "\n".join(str(item) for item in ITENS_INICIAIS))

    def gerar_grafico_pelos_campos(self) -> None:
        """Lê, valida e desenha o gráfico usando os valores digitados."""
        try:
            valores_x, valores_y = self.obter_dados()
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return

        self.gerar_grafico(valores_x, valores_y)

    def obter_dados(self) -> tuple[list[str], list[float]]:
        """Obtém os valores dos campos de texto."""
        valores_x = [valor.strip() for valor in self.campo_x.get("1.0", "end").splitlines() if valor.strip()]
        textos_y = [valor.strip() for valor in self.campo_y.get("1.0", "end").splitlines() if valor.strip()]

        if not valores_x or not textos_y:
            raise ValueError("Preencha os campos Eixo X e Eixo Y.")

        if len(valores_x) != len(textos_y):
            raise ValueError("Os campos Eixo X e Eixo Y precisam ter a mesma quantidade de valores.")

        try:
            valores_y = [float(valor.replace(",", ".")) for valor in textos_y]
        except ValueError as erro:
            raise ValueError("Preencha o Eixo Y apenas com números válidos.") from erro

        if any(valor < 0 for valor in valores_y):
            raise ValueError("Use apenas valores maiores ou iguais a zero no Eixo Y.")

        return valores_x, valores_y

    @staticmethod
    def definir_cor_fundo(item: float, media_itens: float) -> str:
        """Retorna a cor da faixa de fundo conforme o nível de estoque."""
        if item < media_itens:
            return "#d9f2df"

        if item == media_itens:
            return "#fff1c7"

        return "#f5cccc"

    @staticmethod
    def converter_x(indice: int, largura_util: int, total_pontos: int) -> float:
        """Converte a posição do item para o centro da sua faixa no eixo X."""
        largura_faixa = largura_util / total_pontos
        return MARGEM_ESQUERDA + (indice + 0.5) * largura_faixa

    @staticmethod
    def converter_y(item: float, maior_item: float, altura_util: int) -> float:
        """Converte a quantidade em estoque para a coordenada Y do canvas."""
        return MARGEM_SUPERIOR + altura_util - (item / maior_item) * altura_util

    def gerar_grafico(self, valores_x: list[str] | list[int], valores_y: list[float] | list[int]) -> None:
        """Desenha o gráfico no canvas."""
        self.canvas.delete("all")

        total_pontos = len(valores_x)
        media_itens = mean(valores_y)
        maior_item = max(max(valores_y), 1)
        largura_util = LARGURA - MARGEM_ESQUERDA - MARGEM_DIREITA
        altura_util = ALTURA - MARGEM_SUPERIOR - MARGEM_INFERIOR
        largura_faixa = largura_util / total_pontos
        y_media = self.converter_y(media_itens, maior_item, altura_util)

        self.canvas.create_rectangle(0, 0, LARGURA, ALTURA, fill="white", outline="")

        for indice, item in enumerate(valores_y):
            x = MARGEM_ESQUERDA + indice * largura_faixa
            self.canvas.create_rectangle(
                x,
                MARGEM_SUPERIOR,
                x + largura_faixa,
                MARGEM_SUPERIOR + altura_util,
                fill=self.definir_cor_fundo(item, media_itens),
                outline="",
            )

        for indice, valor_x in enumerate(valores_x):
            x = self.converter_x(indice, largura_util, total_pontos)
            self.canvas.create_line(
                x,
                MARGEM_SUPERIOR,
                x,
                MARGEM_SUPERIOR + altura_util,
                fill="#9e9e9e",
                dash=(5, 3),
            )
            self.canvas.create_text(x, ALTURA - 15, text=str(valor_x), font=("Arial", 8, "bold"))

        for indice, item in enumerate(valores_y):
            x = self.converter_x(indice, largura_util, total_pontos)
            y = self.converter_y(item, maior_item, altura_util)
            raio = 5.8 if item == media_itens else 5.2
            cor = "#d00000" if item == media_itens else "#3f3f3f"
            self.canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=cor, outline=cor)

        self.canvas.create_line(
            MARGEM_ESQUERDA,
            y_media,
            MARGEM_ESQUERDA + largura_util,
            y_media,
            fill="#005f99",
            width=2,
        )
        self.canvas.create_text(
            MARGEM_ESQUERDA + largura_util - 4,
            y_media - 8,
            text=f"Média: {media_itens:g}",
            anchor="e",
            font=("Arial", 11, "bold"),
        )
        self.canvas.create_rectangle(
            MARGEM_ESQUERDA,
            MARGEM_SUPERIOR,
            MARGEM_ESQUERDA + largura_util,
            MARGEM_SUPERIOR + altura_util,
            outline="black",
            width=1.5,
        )
        self.canvas.create_text(10, MARGEM_SUPERIOR + 6, text="und", anchor="w", font=("Arial", 8, "bold"))
        self.canvas.create_text(LARGURA - 12, ALTURA - 18, text="eixo X", anchor="e", font=("Arial", 7, "bold"))


def main() -> None:
    janela = tk.Tk()
    PlataformaGrafico(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
