from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_file

# =========================
# Configuração de caminhos
# =========================

PASTA_BASE = Path(__file__).resolve().parent
CAMINHO_HTML = PASTA_BASE / "plataforma_grafico.html"
CAMINHO_BANCO = PASTA_BASE / "pontos.sqlite3"

app = Flask(__name__)


# =========================
# Persistência SQLite
# =========================

def conectar_banco() -> sqlite3.Connection:
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco() -> None:
    with conectar_banco() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS pontos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dados TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def normalizar_pontos(conteudo: Any) -> list[Any]:
    if isinstance(conteudo, dict) and "pontos" in conteudo:
        pontos = conteudo["pontos"]
    else:
        pontos = conteudo

    if not isinstance(pontos, list):
        raise ValueError("Envie uma lista de pontos ou um objeto JSON com a chave 'pontos'.")

    return pontos


def buscar_pontos_salvos() -> list[Any]:
    inicializar_banco()
    with conectar_banco() as conexao:
        registros = conexao.execute(
            "SELECT dados FROM pontos ORDER BY id ASC"
        ).fetchall()

    return [json.loads(registro["dados"]) for registro in registros]


def substituir_pontos(pontos: list[Any]) -> None:
    inicializar_banco()
    with conectar_banco() as conexao:
        conexao.execute("DELETE FROM pontos")
        conexao.executemany(
            "INSERT INTO pontos (dados) VALUES (?)",
            [(json.dumps(ponto, ensure_ascii=False),) for ponto in pontos],
        )


def limpar_pontos() -> None:
    inicializar_banco()
    with conectar_banco() as conexao:
        conexao.execute("DELETE FROM pontos")


# =========================
# Rotas HTTP
# =========================

@app.get("/")
def pagina_inicial():
    return send_file(CAMINHO_HTML)


@app.get("/api/pontos")
def api_buscar_pontos():
    return jsonify({"pontos": buscar_pontos_salvos()})


@app.post("/api/pontos")
def api_salvar_pontos():
    try:
        pontos = normalizar_pontos(request.get_json(silent=True))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    substituir_pontos(pontos)
    return jsonify({"pontos": pontos, "total": len(pontos)}), 201


@app.delete("/api/pontos")
def api_limpar_pontos():
    limpar_pontos()
    return jsonify({"pontos": [], "total": 0})


# =========================
# Execução local
# =========================

if __name__ == "__main__":
    inicializar_banco()
    app.run(debug=True)
