import chromadb

PASTA_CHROMA = r"D:\Users\50047539\02_Redes_Neurais\04_Novo_Modelo_ChromaDB"

cliente_chroma = chromadb.PersistentClient(path=PASTA_CHROMA)

for c in cliente_chroma.list_collections():
    nome = c.name if hasattr(c, "name") else c
    print("Apagando:", nome)
    cliente_chroma.delete_collection(name=nome)

print("Todas as coleções foram apagadas.")
