import os
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# =========================
# CONFIGURAÇÕES
# =========================

MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PASTA_MODELO = "./modelo_sentence_transformer_multilingual"

PASTA_CHROMA = r"D:\Users\50047539\02_Redes_Neurais\04_Novo_Modelo_ChromaDB"
NOME_COLECAO = "documentos_industriais"

TAMANHO_CHUNK = 900
SOBREPOSICAO_CHUNK = 150


# =========================
# MODELO
# =========================

if os.path.exists(PASTA_MODELO):
    modelo_embedding = SentenceTransformer(PASTA_MODELO)
else:
    modelo_embedding = SentenceTransformer(MODELO_EMBEDDING)
    modelo_embedding.save(PASTA_MODELO)


# =========================
# CHROMADB
# =========================

cliente_chroma = chromadb.PersistentClient(path=PASTA_CHROMA)

colecao = cliente_chroma.get_or_create_collection(
    name=NOME_COLECAO
)


# =========================
# FUNÇÕES
# =========================

def extrair_texto_pdf(caminho_pdf):
    texto_total = ""
    leitor = PdfReader(caminho_pdf)

    for numero_pagina, pagina in enumerate(leitor.pages, start=1):
        texto_pagina = pagina.extract_text()

        if texto_pagina:
            texto_total += f"\n\n--- Página {numero_pagina} ---\n"
            texto_total += texto_pagina

    return texto_total.strip()


def dividir_em_chunks(texto, tamanho=TAMANHO_CHUNK, sobreposicao=SOBREPOSICAO_CHUNK):
    texto = texto.strip()

    if not texto:
        return []

    chunks = []
    inicio = 0

    while inicio < len(texto):
        fim = inicio + tamanho
        chunk = texto[inicio:fim].strip()

        if chunk:
            chunks.append(chunk)

        inicio = fim - sobreposicao

        if inicio >= len(texto):
            break

    return chunks


def indexar_pdf(caminho_pdf, fase):
    nome_arquivo = os.path.basename(caminho_pdf)

    texto = extrair_texto_pdf(caminho_pdf)

    if not texto:
        raise Exception("Não foi possível extrair texto do PDF.")

    chunks = dividir_em_chunks(texto)

    if not chunks:
        raise Exception("Nenhum chunk foi criado.")

    embeddings = modelo_embedding.encode(chunks).tolist()

    ids = []
    metadados = []

    for i, chunk in enumerate(chunks, start=1):
        id_chunk = f"fase_{fase}_{nome_arquivo}_{i}_{uuid.uuid4().hex[:8]}"

        ids.append(id_chunk)

        metadados.append({
            "arquivo": nome_arquivo,
            "fase": int(fase),
            "chunk": i,
            "total_chunks": len(chunks)
        })

    colecao.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadados
    )

    return nome_arquivo, len(chunks)


def selecionar_pdf():
    caminho_pdf = filedialog.askopenfilename(
        title="Selecionar PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    if caminho_pdf:
        entrada_pdf.delete(0, tk.END)
        entrada_pdf.insert(0, caminho_pdf)


def executar_indexacao():
    caminho_pdf = entrada_pdf.get().strip()
    fase = entrada_fase.get().strip()

    if not caminho_pdf:
        messagebox.showwarning("Aviso", "Selecione um PDF.")
        return

    if not fase.isdigit():
        messagebox.showwarning("Aviso", "Digite o número da fase. Exemplo: 1")
        return

    resultado_texto.delete("1.0", tk.END)
    resultado_texto.insert(tk.END, "Indexando PDF no ChromaDB...\n")
    janela.update_idletasks()

    try:
        nome_arquivo, total_chunks = indexar_pdf(caminho_pdf, fase)

        resultado_texto.delete("1.0", tk.END)
        resultado_texto.insert(
            tk.END,
            f"PDF indexado com sucesso!\n\n"
            f"Arquivo: {nome_arquivo}\n"
            f"Fase: {fase}\n"
            f"Chunks criados: {total_chunks}\n"
            f"ChromaDB: {PASTA_CHROMA}\n"
            f"Coleção: {NOME_COLECAO}\n"
        )

    except Exception as erro:
        resultado_texto.delete("1.0", tk.END)
        resultado_texto.insert(
            tk.END,
            f"Erro ao indexar PDF:\n\n{erro}"
        )


# =========================
# INTERFACE
# =========================

janela = tk.Tk()
janela.title("Indexador PDF - ChromaDB com Fase")
janela.geometry("850x430")

titulo = tk.Label(
    janela,
    text="Indexador PDF para ChromaDB",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=15)

frame_pdf = tk.Frame(janela)
frame_pdf.pack(padx=20, pady=10, fill="x")

entrada_pdf = tk.Entry(frame_pdf, width=90)
entrada_pdf.pack(side="left", padx=5)

botao_pdf = tk.Button(
    frame_pdf,
    text="Selecionar PDF",
    command=selecionar_pdf
)
botao_pdf.pack(side="left", padx=5)

frame_fase = tk.Frame(janela)
frame_fase.pack(padx=20, pady=10, anchor="w")

label_fase = tk.Label(
    frame_fase,
    text="Número da fase:",
    font=("Arial", 11, "bold")
)
label_fase.pack(side="left")

entrada_fase = tk.Entry(frame_fase, width=10)
entrada_fase.pack(side="left", padx=10)

botao_indexar = tk.Button(
    janela,
    text="Indexar PDF",
    font=("Arial", 12, "bold"),
    bg="#1F618D",
    fg="white",
    width=20,
    command=executar_indexacao
)
botao_indexar.pack(pady=15)

resultado_texto = tk.Text(janela, height=10, width=100)
resultado_texto.pack(padx=20, pady=10)

janela.mainloop()