import os
import json
import re
import tkinter as tk
from tkinter import messagebox, ttk

import requests
import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# CONFIGURAÇÕES
# =========================

MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PASTA_MODELO = "./modelo_sentence_transformer_multilingual"

MODELO_LLM = "qwen2.5"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

PASTA_CHROMA = r"D:\Users\50047539\02_Redes_Neurais\04_Novo_Modelo_ChromaDB"
NOME_COLECAO = "documentos_industriais"

TOP_K_CHUNKS = 3


# =========================
# CARREGA MODELO
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
# FUNÇÕES AUXILIARES
# =========================

def interpretar_score(score):
    if score >= 0.85:
        return "Muito alta"
    elif score >= 0.70:
        return "Alta"
    elif score >= 0.55:
        return "Média"
    elif score >= 0.40:
        return "Baixa"
    else:
        return "Muito baixa"


def distancia_para_similaridade(distancia):
    """
    Conversão para coleções ChromaDB usando distância cosseno.
    Quanto menor a distância, maior a similaridade.
    """
    try:
        sim = 1.0 - float(distancia)
        return max(0.0, min(1.0, sim))
    except Exception:
        return 0.0


def consultar_chromadb_por_fase(consulta, numero_fase, top_k=TOP_K_CHUNKS):
    embedding_consulta = modelo_embedding.encode([consulta])[0].tolist()

    resultado = colecao.query(
        query_embeddings=[embedding_consulta],
        n_results=top_k,
        where={"fase": int(numero_fase)},
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documentos = resultado.get("documents", [[]])[0]
    metadados = resultado.get("metadatas", [[]])[0]
    distancias = resultado.get("distances", [[]])[0]

    print("\n===== DEBUG CHROMADB =====")
    print(f"Fase consultada: {numero_fase}")
    for d in distancias:
        print(f"Distância: {d:.4f} | Similaridade: {distancia_para_similaridade(d):.4f}")
    print("==========================\n")

    chunks = []

    for i, texto_chunk in enumerate(documentos):
        metadata = metadados[i] if i < len(metadados) else {}
        distancia = distancias[i] if i < len(distancias) else 999

        chunks.append({
            "ranking": i + 1,
            "texto_chunk": texto_chunk,
            "metadata": metadata,
            "distancia": distancia,
            "similaridade": distancia_para_similaridade(distancia)
        })

    return chunks


def calcular_analise_semantica(frase_principal, fases_validas):
    embedding_principal = modelo_embedding.encode([frase_principal])
    textos_fases = [item["texto_fase"] for item in fases_validas]

    embeddings_fases = modelo_embedding.encode(textos_fases)

    similaridades = cosine_similarity(
        embedding_principal,
        embeddings_fases
    )[0]

    analise = []

    for i, item in enumerate(fases_validas):
        numero_fase = item["numero_fase"]
        texto_fase = item["texto_fase"]

        # IMPORTANTE:
        # A busca no ChromaDB agora usa somente a atividade principal.
        # A fase já é filtrada pelo metadado "fase".
        consulta = frase_principal

        chunks = consultar_chromadb_por_fase(
            consulta=consulta,
            numero_fase=numero_fase,
            top_k=TOP_K_CHUNKS
        )

        score_fase = float(similaridades[i])
        score_documento = chunks[0]["similaridade"] if chunks else 0.0

        analise.append({
            "numero_fase": numero_fase,
            "texto_fase": texto_fase,
            "score_fase": score_fase,
            "score_documento": score_documento,
            "interpretacao_score_fase": interpretar_score(score_fase),
            "interpretacao_score_documento": interpretar_score(score_documento),
            "chunks_documento": chunks,
            "tem_documento": bool(chunks)
        })

    return analise


def consultar_llm(prompt):
    try:
        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO_LLM,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 900,
                    "num_ctx": 4096
                }
            },
            timeout=600
        )
    except requests.exceptions.ConnectionError:
        raise Exception("Não foi possível conectar ao Ollama. Verifique se ele está aberto.")

    resposta.raise_for_status()
    dados = resposta.json()

    if "response" not in dados:
        raise Exception(f"Resposta inesperada do Ollama: {dados}")

    return dados["response"]


def montar_bloco_chunks(chunks):
    if not chunks:
        return "Nenhum trecho encontrado no ChromaDB para esta fase."

    texto = ""

    for chunk in chunks:
        arquivo = chunk["metadata"].get("arquivo", "Arquivo não informado")
        fase = chunk["metadata"].get("fase", "Fase não informada")
        numero_chunk = chunk["metadata"].get("chunk", "Chunk não informado")

        texto += f"""
Trecho {chunk["ranking"]}:
Arquivo: {arquivo}
Fase metadata: {fase}
Chunk: {numero_chunk}
Distância: {chunk["distancia"]:.4f}
Similaridade: {chunk["similaridade"]:.4f}

Conteúdo:
{chunk["texto_chunk"][:1600]}
"""

    return texto


def montar_contexto_para_llm(analise_semantica):
    contexto = ""

    for item in analise_semantica:
        contexto += f"""
==============================
Fase {item["numero_fase"]}
==============================

Texto da fase candidata:
{item["texto_fase"]}

Score semântico entre atividade principal e texto da fase:
{item["score_fase"]:.4f}

Interpretação do score da fase:
{item["interpretacao_score_fase"]}

Score do melhor trecho documental recuperado no ChromaDB:
{item["score_documento"]:.4f}

Interpretação do score documental:
{item["interpretacao_score_documento"]}

Trechos recuperados no ChromaDB filtrados somente pela Fase {item["numero_fase"]}:
{montar_bloco_chunks(item["chunks_documento"])}
"""

    return contexto


def extrair_json(texto):
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    padrao = r"\[\s*\{.*?\}\s*\]"
    encontrado = re.search(padrao, texto, re.DOTALL)

    if encontrado:
        return json.loads(encontrado.group())

    raise Exception(f"Não foi possível extrair JSON válido da resposta:\n{texto}")


def validar_decisoes(decisoes_llm, analise_semantica):
    analise_por_fase = {
        item["numero_fase"]: item
        for item in analise_semantica
    }

    fases_esperadas = set(analise_por_fase.keys())
    fases_retornadas = set()
    decisoes_validas = []

    for item in decisoes_llm:
        try:
            fase = int(item.get("fase"))
            fases_retornadas.add(fase)

            # Regra fixa:
            # Se o ChromaDB não encontrou documento para a fase,
            # a evidência documental deve ser "Sem evidência",
            # independentemente do que o LLM respondeu.
            if fase in analise_por_fase and not analise_por_fase[fase]["tem_documento"]:
                item["evidencia_documento"] = "Sem evidência"

            decisoes_validas.append(item)

        except Exception:
            continue

    fases_faltantes = fases_esperadas - fases_retornadas

    for fase in fases_faltantes:
        decisoes_validas.append({
            "fase": fase,
            "esta_contida": "ERRO LLM",
            "grau_relacao": "ERRO LLM",
            "evidencia_documento": "Não avaliado",
            "justificativa": "O LLM não retornou decisão estruturada para esta fase."
        })

    return sorted(decisoes_validas, key=lambda x: int(x["fase"]))

def decidir_com_llm(frase_principal, analise_semantica):
    contexto = montar_contexto_para_llm(analise_semantica)

    prompt = f"""
Você é um especialista em engenharia industrial, gestão de projetos, confiabilidade, manutenção e análise de escopo técnico.

Sua tarefa é determinar se cada fase candidata pertence ao escopo da atividade principal.

A análise deve ser baseada principalmente na comparação entre:

* Atividade principal.
* Descrição da fase candidata.
* Objetivo da atividade.
* Natureza da atividade.
* Relação declarada com o projeto.
* Evidências documentais recuperadas do ChromaDB (quando existirem).

HIERARQUIA OBRIGATÓRIA DE ANÁLISE

Ao avaliar cada fase, siga obrigatoriamente esta sequência:

1. Identifique a natureza da atividade principal.
2. Identifique a natureza da atividade da fase candidata.
3. Compare os objetivos técnicos.
4. Compare o escopo de intervenção.
5. Compare equipamentos e sistemas envolvidos.
6. Avalie a relação declarada com o projeto.
7. Considere evidências documentais do ChromaDB apenas como complemento.

A natureza da atividade possui prioridade sobre os equipamentos citados.

Em caso de conflito entre palavras-chave e natureza da atividade, priorize a natureza da atividade.

Exemplos:

- Elaborar especificação técnica de um ventilador = Engenharia.
- Comprar um ventilador = Aquisição.
- Instalar um ventilador = Execução.
- Reparar um ventilador = Operação/Manutenção.

O mesmo equipamento pode aparecer em atividades de naturezas completamente diferentes.

O fato de duas atividades mencionarem os mesmos equipamentos não significa que pertençam ao mesmo escopo.

CLASSIFICAÇÃO DA NATUREZA DA ATIVIDADE

Classifique mentalmente cada atividade em uma das categorias abaixo:

* Engenharia
* Aquisição
* Execução
* Operação / Manutenção
* Modernização

Exemplos:

Engenharia:

* estudos técnicos
* estudos de alternativas
* levantamentos de campo
* topografia
* escaneamento 3D
* modelagem
* memoriais de cálculo
* fluxogramas
* layouts
* listas de materiais
* especificações técnicas
* critérios de projeto
* documentação técnica

Aquisição:

* compra
* contratação de fornecimento
* aquisição de equipamentos
* aquisição de materiais

Execução:

* fabricação
* construção
* montagem
* instalação física
* comissionamento físico

Operação / Manutenção:

* manutenção corretiva
* manutenção preventiva
* reparos
* inspeções operacionais
* intervenções de rotina

Estes exemplos servem apenas como referência de raciocínio e não devem limitar a análise.

REGRAS DE DECISÃO

Se a fase produzir entregas técnicas necessárias para atingir o objetivo da atividade principal, considere evidência favorável.

Se a fase produzir estudos, levantamentos, cálculos, modelagens, especificações, documentação técnica ou definições necessárias para o desenvolvimento do projeto, considere forte evidência de relação com o escopo.

Se a fase representar aquisição, fornecimento, fabricação, montagem, instalação física, operação ou manutenção, verifique se essas atividades estão explicitamente previstas na atividade principal.

Atividades de mesma natureza tendem a possuir maior relação com o escopo.

Atividades de natureza diferente exigem evidências adicionais para serem consideradas pertencentes ao projeto.
Antes de classificar uma fase como "Não", verifique se a atividade candidata menciona explicitamente equipamentos, sistemas, intervenções ou modernizações que estejam descritos na atividade principal.

Se a atividade principal mencionar explicitamente a reforma, modernização, atualização tecnológica ou substituição de determinado sistema, atividades equivalentes devem ser consideradas forte evidência de pertencimento ao escopo.

Não confunda:

* elaboração de especificação técnica com compra;
* elaboração de documentação técnica com fornecimento;
* estudo de alternativas com implantação;
* engenharia com execução;
* engenharia com manutenção.

REGRA ESPECIAL PARA DOCUMENTAÇÃO DE ENGENHARIA

A elaboração de especificações técnicas, requisitos técnicos, critérios de projeto, listas de materiais, fluxogramas, memoriais de cálculo, layouts, modelagens e demais documentos de engenharia deve ser considerada parte do escopo de engenharia, mesmo quando tais documentos forem utilizados posteriormente para aquisição, contratação ou execução.

Não confunda o desenvolvimento da documentação técnica com a futura compra, fornecimento, fabricação, montagem ou instalação dos equipamentos.

Regra de prioridade:

1. Equipamento ou sistema explicitamente citado no escopo principal.
2. Objetivo técnico.
3. Natureza da atividade.
4. Relação declarada com o projeto.
5. Evidência documental.

CRITÉRIOS OBRIGATÓRIOS DE COMPARAÇÃO

1. Natureza da atividade.
2. Objetivo técnico.
3. Escopo de intervenção.
4. Relação declarada com o projeto.
5. Equipamentos citados.
6. Sistemas citados.
7. Processos envolvidos.
8. Contribuição para o objetivo principal.

CLASSIFICAÇÃO DE "esta_contida"

"Sim":
A fase faz parte claramente do escopo da atividade principal.

"Parcialmente":

A fase contribui para o sucesso do projeto,
mas não representa uma entrega principal explicitamente prevista no escopo.

Utilize "Parcialmente" quando a atividade for:

- infraestrutura de apoio;
- monitoramento;
- instrumentação;
- acessos operacionais;
- suporte técnico;
- atividades auxiliares;
- sistemas de controle ou acompanhamento;
- recursos necessários para operação futura,
  mas que não constituem o objeto principal da implantação.

Pergunta de validação:

Se esta atividade fosse removida,
o objeto principal do projeto ainda poderia ser implantado?

Se SIM, considere "Parcialmente".

Se NÃO, considere "Sim".

"Não":
A fase não possui relação técnica relevante ou pertence a outro tipo de atividade não previsto no escopo principal.

Antes de responder "Não", verifique se a atividade produz alguma entrega técnica necessária para atingir o objetivo da atividade principal.

Se produzir uma entrega técnica necessária ao desenvolvimento do projeto, a classificação tende a ser "Sim", mesmo que a atividade mencione equipamentos que serão adquiridos futuramente.

CLASSIFICAÇÃO DE "grau_relacao"

"Alto":
Mesmo objetivo técnico, mesma finalidade ou mesma natureza de atividade.

"Médio":
Atividade complementar, de apoio ou relação indireta.

"Baixo":
Atividade operacional, manutenção, aquisição, execução ou escopo distinto do objetivo principal.

CLASSIFICAÇÃO DE "evidencia_documento"

"Confirma":
Os documentos recuperados reforçam a relação técnica.

"Enfraquece":
Os documentos recuperados apontam para outro escopo.

"Sem evidência":
Não existem documentos recuperados ou não há informação suficiente.

REGRAS OBRIGATÓRIAS PARA EVIDÊNCIA DOCUMENTAL

* Se "Documento encontrado para a fase" for "Não", a resposta deve ser obrigatoriamente "Sem evidência".
* Nunca utilize "Confirma" ou "Enfraquece" quando não houver documentos recuperados.
* A ausência de evidência documental não significa ausência de relação com o projeto.
* A decisão sobre pertencimento ao escopo deve ser baseada principalmente na comparação entre atividade principal e fase candidata.

JUSTIFICATIVA

A justificativa deve:

* Explicar a natureza da atividade.
* Explicar a relação com o objetivo principal.
* Explicar por que pertence ou não ao escopo.
* Evitar justificativas genéricas.
* Citar os elementos técnicos relevantes da decisão.
* A justificativa deve ser específica para cada fase.
* Não repita a mesma justificativa para fases diferentes.
* Cite obrigatoriamente o equipamento/sistema e o tipo de intervenção da fase avaliada.

Atividade principal:

{frase_principal}

Dados das fases:

{contexto}

Responda SOMENTE em JSON válido.

Não escreva nada antes ou depois do JSON.

Formato obrigatório:

[
{{
"fase": 1,
"esta_contida": "Sim",
"grau_relacao": "Alto",
"evidencia_documento": "Sem evidência",
"justificativa": "A fase possui a mesma natureza da atividade principal e contribui diretamente para o objetivo técnico do projeto."
}}
]

Você deve responder todas as fases existentes nos dados.

"""

    resposta_texto = consultar_llm(prompt)
    decisoes = extrair_json(resposta_texto)

    return validar_decisoes(decisoes, analise_semantica)


# =========================
# TABELA
# =========================

def limpar_tabela():
    for item in tabela_resultado.get_children():
        tabela_resultado.delete(item)


def preencher_tabela(analise_semantica, decisoes_llm):
    limpar_tabela()

    decisoes_por_fase = {
        int(item["fase"]): item
        for item in decisoes_llm
    }

    for item in analise_semantica:
        numero_fase = item["numero_fase"]
        decisao = decisoes_por_fase.get(numero_fase, {})

        tabela_resultado.insert(
            "",
            tk.END,
            values=(
                numero_fase,
                item["texto_fase"][:120],
                "Sim" if item["tem_documento"] else "Não",
                f"{item['score_fase']:.4f}",
                f"{item['score_documento']:.4f}",
                decisao.get("esta_contida", "ERRO LLM"),
                decisao.get("grau_relacao", "ERRO LLM"),
                decisao.get("evidencia_documento", "Não avaliado"),
                decisao.get("justificativa", "Sem justificativa")[:180]
            )
        )


# =========================
# EXECUÇÃO
# =========================

def executar_rag():
    frase_principal = entrada_principal.get("1.0", tk.END).strip()

    if not frase_principal:
        messagebox.showwarning("Aviso", "Digite a atividade principal.")
        return

    fases_validas = []

    for i, entrada in enumerate(entradas_frases):
        texto_fase = entrada.get("1.0", tk.END).strip()

        if texto_fase:
            fases_validas.append({
                "numero_fase": i + 1,
                "texto_fase": texto_fase
            })

    if not fases_validas:
        messagebox.showwarning("Aviso", "Digite pelo menos uma fase candidata.")
        return

    resultado_texto.delete("1.0", tk.END)
    limpar_tabela()

    resultado_texto.insert(
        tk.END,
        "Consultando ChromaDB filtrado por fase...\n"
    )
    janela.update_idletasks()

    try:
        analise_semantica = calcular_analise_semantica(
            frase_principal,
            fases_validas
        )

        decisoes_llm = decidir_com_llm(
            frase_principal,
            analise_semantica
        )

        preencher_tabela(
            analise_semantica,
            decisoes_llm
        )

        resultado_texto.delete("1.0", tk.END)

        resultado_texto.insert(
            tk.END,
            "=== ANÁLISE COM CHROMADB FILTRADO POR FASE ===\n\n"
        )

        for item in analise_semantica:
            resultado_texto.insert(
                tk.END,
                f"Fase {item['numero_fase']}:\n"
                f"{item['texto_fase']}\n\n"
                f"Score fase/atividade: {item['score_fase']:.4f} "
                f"({item['interpretacao_score_fase']})\n"
                f"Score documento ChromaDB: {item['score_documento']:.4f} "
                f"({item['interpretacao_score_documento']})\n"
                f"Documento encontrado para a fase: {'Sim' if item['tem_documento'] else 'Não'}\n\n"
            )

            for chunk in item["chunks_documento"]:
                arquivo = chunk["metadata"].get("arquivo", "Arquivo não informado")
                resultado_texto.insert(
                    tk.END,
                    f"- Arquivo: {arquivo} | "
                    f"Fase metadata: {chunk['metadata'].get('fase')} | "
                    f"Distância: {chunk['distancia']:.4f} | "
                    f"Similaridade: {chunk['similaridade']:.4f}\n"
                )

            resultado_texto.insert(tk.END, "\n")

        resultado_texto.insert(
            tk.END,
            "\n=== DECISÃO FINAL DO LLM EM JSON ===\n\n"
        )

        resultado_texto.insert(
            tk.END,
            json.dumps(decisoes_llm, indent=4, ensure_ascii=False)
        )

    except Exception as erro:
        resultado_texto.delete("1.0", tk.END)
        resultado_texto.insert(
            tk.END,
            "Erro ao executar a análise.\n\n"
            f"Erro técnico:\n{erro}"
        )


# =========================
# INTERFACE
# =========================

janela = tk.Tk()
janela.title("RAG Local - ChromaDB Filtrado por Fase")
janela.geometry("1450x850")

titulo = tk.Label(
    janela,
    text="RAG Local - ChromaDB com Metadados: arquivo + fase",
    font=("Arial", 16, "bold")
)
titulo.pack(pady=10)

label_principal = tk.Label(
    janela,
    text="Atividade principal:",
    font=("Arial", 11, "bold")
)
label_principal.pack(anchor="w", padx=20)

entrada_principal = tk.Text(janela, height=4, width=160)
entrada_principal.pack(padx=20, pady=5)

entradas_frases = []

for i in range(5):
    label = tk.Label(
        janela,
        text=f"Fase candidata {i + 1}:",
        font=("Arial", 10, "bold")
    )
    label.pack(anchor="w", padx=20)

    entrada = tk.Text(janela, height=2, width=160)
    entrada.pack(padx=20, pady=3)

    entradas_frases.append(entrada)


botao_run = tk.Button(
    janela,
    text="Run RAG - ChromaDB por Fase",
    font=("Arial", 12, "bold"),
    bg="#1F618D",
    fg="white",
    width=35,
    command=executar_rag
)
botao_run.pack(pady=10)


label_tabela = tk.Label(
    janela,
    text="Tabela estruturada:",
    font=("Arial", 11, "bold")
)
label_tabela.pack(anchor="w", padx=20)


colunas = (
    "fase",
    "texto",
    "documento",
    "score_fase",
    "score_documento",
    "decisao",
    "grau",
    "evidencia",
    "justificativa"
)

frame_tabela = tk.Frame(janela)
frame_tabela.pack(padx=20, pady=5, fill="both", expand=True)

tabela_resultado = ttk.Treeview(
    frame_tabela,
    columns=colunas,
    show="headings",
    height=6
)

scroll_vertical = ttk.Scrollbar(
    frame_tabela,
    orient="vertical",
    command=tabela_resultado.yview
)

scroll_horizontal = ttk.Scrollbar(
    frame_tabela,
    orient="horizontal",
    command=tabela_resultado.xview
)

tabela_resultado.configure(
    yscrollcommand=scroll_vertical.set,
    xscrollcommand=scroll_horizontal.set
)

cabecalhos = {
    "fase": "Fase",
    "texto": "Texto da fase",
    "documento": "Doc. ChromaDB",
    "score_fase": "Score fase",
    "score_documento": "Score documento",
    "decisao": "Está contida?",
    "grau": "Grau",
    "evidencia": "Evidência",
    "justificativa": "Justificativa"
}

for coluna in colunas:
    tabela_resultado.heading(coluna, text=cabecalhos[coluna])

tabela_resultado.column("fase", width=60)
tabela_resultado.column("texto", width=380)
tabela_resultado.column("documento", width=120)
tabela_resultado.column("score_fase", width=100)
tabela_resultado.column("score_documento", width=120)
tabela_resultado.column("decisao", width=120)
tabela_resultado.column("grau", width=90)
tabela_resultado.column("evidencia", width=140)
tabela_resultado.column("justificativa", width=520)

tabela_resultado.grid(row=0, column=0, sticky="nsew")
scroll_vertical.grid(row=0, column=1, sticky="ns")
scroll_horizontal.grid(row=1, column=0, sticky="ew")

frame_tabela.grid_rowconfigure(0, weight=1)
frame_tabela.grid_columnconfigure(0, weight=1)


label_resultado = tk.Label(
    janela,
    text="Resultado detalhado:",
    font=("Arial", 11, "bold")
)
label_resultado.pack(anchor="w", padx=20)

resultado_texto = tk.Text(janela, height=13, width=160)
resultado_texto.pack(padx=20, pady=5)

janela.mainloop()