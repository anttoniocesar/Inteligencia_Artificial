import chromadb

PASTA_CHROMA = r"D:\Users\50047539\02_Redes_Neurais\04_Novo_Modelo_ChromaDB"

cliente_chroma = chromadb.PersistentClient(path=PASTA_CHROMA)

colecoes = cliente_chroma.list_collections()

print("\n=== VERIFICAÇÃO DO CHROMADB ===")

print(f"Quantidade de coleções: {len(colecoes)}")

for c in colecoes:
    nome = c.name if hasattr(c, "name") else c

    colecao = cliente_chroma.get_or_create_collection(name=nome)

    print(f"\nColeção: {nome}")
    print(f"Registros: {colecao.count()}")
    