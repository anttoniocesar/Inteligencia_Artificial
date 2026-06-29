"""Aplicação Tkinter para análise RAG local com ChromaDB filtrado por fase.

Ajustes da etapa 1:
- Código consolidado em uma única cópia executável.
- Strings com quebras de linha corrigidas.
- Configurações sensíveis/locais lidas por variáveis de ambiente.
- Criação da interface protegida por ``if __name__ == "__main__"``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

import chromadb
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# CONFIGURAÇÕES
# =========================

MODELO_EMBEDDING = os.getenv(
    "MODELO_EMBEDDING",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
PASTA_MODELO = Path(os.getenv("PASTA_MODELO", "./modelo_sentence_transformer_multilingual"))

MODELO_LLM = os.getenv("MODELO_LLM", "qwen2.5")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")

PASTA_CHROMA = Path(os.getenv("PASTA_CHROMA", "./chroma_db"))
NOME_COLECAO = os.getenv("NOME_COLECAO", "documentos_industriais")

TOP_K_CHUNKS = int(os.getenv("TOP_K_CHUNKS", "3"))


# =========================
# CARREGAMENTO DE RECURSOS
# =========================

modelo_embedding: SentenceTransformer | None = None
colecao: Any | None = None


def carregar_modelo_embedding() -> SentenceTransformer:
    """Carrega o modelo de embeddings do disco ou baixa e salva localmente."""
    global modelo_embedding

    if modelo_embedding is not None:
        return modelo_embedding

    if PASTA_MODELO.exists():
        modelo_embedding = SentenceTransformer(str(PASTA_MODELO))
    else:
        modelo_embedding = SentenceTransformer(MODELO_EMBEDDING)
        modelo_embedding.save(str(PASTA_MODELO))

    return modelo_embedding


def carregar_colecao_chroma() -> Any:
    """Abre a coleção ChromaDB configurada."""
    global colecao

    if colecao is not None:
        return colecao

    cliente_chroma = chromadb.PersistentClient(path=str(PASTA_CHROMA))
    colecao = cliente_chroma.get_or_create_collection(name=NOME_COLECAO)
    return colecao


# =========================
# FUNÇÕES AUXILIARES
# =========================

def interpretar_score(score: float) -> str:
    if score >= 0.85:
        return "Muito alta"
    if score >= 0.70:
        return "Alta"
    if score >= 0.55:
        return "Média"
    if score >= 0.40:
        return "Baixa"
    return "Muito baixa"


def avaliar_qualidade_informacao(texto: str) -> dict[str, Any]:
    texto_limpo = texto.strip()
    texto_lower = texto_limpo.lower()
    palavras = re.findall(r"\b\w+\b", texto_lower)

    qtd_palavras = len(palavras)

    tem_modelo_padrao = all(
        campo in texto_lower
        for campo in [
            "objetivo",
            "equipamento",
            "tipo de intervenção",
            "relação com o projeto",
            "fora do escopo",
        ]
    )

    verbos_acao = [
        "substituir",
        "trocar",
        "instalar",
        "executar",
        "reparar",
        "automatizar",
        "integrar",
        "desenvolver",
        "adequar",
        "modernizar",
        "reformar",
        "realizar",
        "implantar",
    ]

    termos_tecnicos = [
        "sistema",
        "equipamento",
        "forno",
        "motor",
        "bomba",
        "painel",
        "manilha",
        "drenagem",
        "rede",
        "erp",
        "software",
        "estrutura",
        "tubulação",
        "elétrica",
        "hidráulica",
        "mecânica",
    ]

    tem_verbo_acao = any(verbo in texto_lower for verbo in verbos_acao)
    tem_termo_tecnico = any(termo in texto_lower for termo in termos_tecnicos)

    pontos = 0

    if qtd_palavras >= 40:
        pontos += 3
    elif qtd_palavras >= 15:
        pontos += 2
    elif qtd_palavras >= 5:
        pontos += 1

    if tem_modelo_padrao:
        pontos += 3

    if tem_verbo_acao:
        pontos += 2

    if tem_termo_tecnico:
        pontos += 2

    if pontos >= 7:
        qualidade = "Alta"
    elif pontos >= 4:
        qualidade = "Média"
    else:
        qualidade = "Baixa"

    if qualidade == "Baixa":
        recomendacao = "Classificação deve ser tratada com cautela. Pode haver contexto insuficiente."
    elif qualidade == "Média":
        recomendacao = "Há informação parcial. A decisão pode exigir validação humana."
    else:
        recomendacao = "Informação suficiente para análise técnica."

    return {
        "qtd_palavras": qtd_palavras,
        "qualidade_informacao": qualidade,
        "tem_modelo_padrao": tem_modelo_padrao,
        "tem_verbo_acao": tem_verbo_acao,
        "tem_termo_tecnico": tem_termo_tecnico,
        "recomendacao_qualidade": recomendacao,
    }


def distancia_para_similaridade(distancia: float) -> float:
    """Converte distância cosseno em similaridade no intervalo de 0 a 1."""
    try:
        similaridade = 1.0 - float(distancia)
        return max(0.0, min(1.0, similaridade))
    except (TypeError, ValueError):
        return 0.0


def consultar_chromadb_por_fase(
    consulta: str,
    numero_fase: int,
    top_k: int = TOP_K_CHUNKS,
) -> list[dict[str, Any]]:
    modelo = carregar_modelo_embedding()
    colecao_chroma = carregar_colecao_chroma()
    embedding_consulta = modelo.encode([consulta])[0].tolist()

    resultado = colecao_chroma.query(
        query_embeddings=[embedding_consulta],
        n_results=top_k,
        where={"fase": int(numero_fase)},
        include=["documents", "metadatas", "distances"],
    )

    documentos = resultado.get("documents", [[]])[0]
    metadados = resultado.get("metadatas", [[]])[0]
    distancias = resultado.get("distances", [[]])[0]

    print("\n===== DEBUG CHROMADB =====")
    print(f"Fase consultada: {numero_fase}")
    for distancia in distancias:
        print(
            f"Distância: {distancia:.4f} | "
            f"Similaridade: {distancia_para_similaridade(distancia):.4f}"
        )
    print("==========================\n")

    chunks = []

    for indice, texto_chunk in enumerate(documentos):
        metadata = metadados[indice] if indice < len(metadados) else {}
        distancia = distancias[indice] if indice < len(distancias) else 999

        chunks.append(
            {
                "ranking": indice + 1,
                "texto_chunk": texto_chunk,
                "metadata": metadata,
                "distancia": distancia,
                "similaridade": distancia_para_similaridade(distancia),
            }
        )

    return chunks


def calcular_analise_semantica(
    frase_principal: str,
    fases_validas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    modelo = carregar_modelo_embedding()
    embedding_principal = modelo.encode([frase_principal])
    textos_fases = [item["texto_fase"] for item in fases_validas]
    embeddings_fases = modelo.encode(textos_fases)

    similaridades = cosine_similarity(embedding_principal, embeddings_fases)[0]
    analise = []

    for indice, item in enumerate(fases_validas):
        numero_fase = item["numero_fase"]
        texto_fase = item["texto_fase"]
        chunks = consultar_chromadb_por_fase(
            consulta=frase_principal,
            numero_fase=numero_fase,
            top_k=TOP_K_CHUNKS,
        )

        score_fase = float(similaridades[indice])
        score_documento = chunks[0]["similaridade"] if chunks else 0.0
        qualidade = avaliar_qualidade_informacao(texto_fase)

        analise.append(
            {
                "numero_fase": numero_fase,
                "texto_fase": texto_fase,
                "score_fase": score_fase,
                "score_documento": score_documento,
                "interpretacao_score_fase": interpretar_score(score_fase),
                "interpretacao_score_documento": interpretar_score(score_documento),
                "chunks_documento": chunks,
                "tem_documento": bool(chunks),
                "qualidade_informacao": qualidade["qualidade_informacao"],
                "qtd_palavras": qualidade["qtd_palavras"],
                "tem_modelo_padrao": qualidade["tem_modelo_padrao"],
                "tem_verbo_acao": qualidade["tem_verbo_acao"],
                "tem_termo_tecnico": qualidade["tem_termo_tecnico"],
                "recomendacao_qualidade": qualidade["recomendacao_qualidade"],
            }
        )

    return analise


def consultar_llm(prompt: str) -> str:
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
                    "num_ctx": 4096,
                },
            },
            timeout=600,
        )
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Não foi possível conectar ao Ollama. Verifique se ele está aberto.") from exc

    resposta.raise_for_status()
    dados = resposta.json()

    if "response" not in dados:
        raise RuntimeError(f"Resposta inesperada do Ollama: {dados}")

    return dados["response"]


def montar_bloco_chunks(chunks: list[dict[str, Any]]) -> str:
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


def montar_contexto_para_llm(analise_semantica: list[dict[str, Any]]) -> str:
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

Qualidade da informação da fase:
{item["qualidade_informacao"]}

Quantidade de palavras:
{item["qtd_palavras"]}

Tem modelo padronizado:
{'Sim' if item["tem_modelo_padrao"] else 'Não'}

Tem verbo de ação:
{'Sim' if item["tem_verbo_acao"] else 'Não'}

Tem termo técnico:
{'Sim' if item["tem_termo_tecnico"] else 'Não'}

Recomendação sobre qualidade:
{item["recomendacao_qualidade"]}

Trechos recuperados no ChromaDB filtrados somente pela Fase {item["numero_fase"]}:
{montar_bloco_chunks(item["chunks_documento"])}
"""

    return contexto


def extrair_json(texto: str) -> Any:
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    padrao = r"\[\s*\{.*?\}\s*\]"
    encontrado = re.search(padrao, texto, re.DOTALL)

    if encontrado:
        return json.loads(encontrado.group())

    raise RuntimeError(f"Não foi possível extrair JSON válido da resposta:\n{texto}")


def validar_decisoes(
    decisoes_llm: list[dict[str, Any]],
    analise_semantica: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    analise_por_fase = {item["numero_fase"]: item for item in analise_semantica}
    fases_esperadas = set(analise_por_fase.keys())
    fases_retornadas = set()
    decisoes_validas = []

    for item in decisoes_llm:
        try:
            fase = int(item.get("fase"))
            fases_retornadas.add(fase)

            if fase in analise_por_fase:
                if not analise_por_fase[fase]["tem_documento"]:
                    item["evidencia_documento"] = "Sem evidência"

                item["qualidade_informacao"] = analise_por_fase[fase]["qualidade_informacao"]

                if analise_por_fase[fase]["qualidade_informacao"] == "Baixa":
                    item["alerta_qualidade"] = (
                        "Descrição curta ou incompleta. Recomenda-se validação humana."
                    )
                else:
                    item["alerta_qualidade"] = "Qualidade suficiente para análise."

            decisoes_validas.append(item)
        except (TypeError, ValueError):
            continue

    fases_faltantes = fases_esperadas - fases_retornadas

    for fase in fases_faltantes:
        decisoes_validas.append(
            {
                "fase": fase,
                "esta_contida": "ERRO LLM",
                "grau_relacao": "ERRO LLM",
                "evidencia_documento": "Não avaliado",
                "justificativa": "O LLM não retornou decisão estruturada para esta fase.",
            }
        )

    return sorted(decisoes_validas, key=lambda item: int(item["fase"]))


def decidir_com_llm(
    frase_principal: str,
    analise_semantica: list[dict[str, Any]],
) -> list[dict[str, Any]]:
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

QUALIDADE DA INFORMAÇÃO

Antes de decidir se a fase pertence ao escopo, avalie a qualidade da informação disponível.

Se a qualidade da informação for "Baixa":

- Evite decisões categóricas quando a descrição for curta ou ambígua.
- Não classifique automaticamente como "Não" apenas por falta de contexto.
- Se houver correspondência direta de objeto, verbo ou sistema com a atividade principal, considere "Parcialmente" ou "Sim", conforme o caso.
- Use "Parcialmente" quando a fase parecer relacionada, mas a descrição não fornecer elementos suficientes para confirmar totalmente.
- A justificativa deve mencionar que a qualidade da informação é baixa.

Exemplo:

Atividade principal:
Substituição de manilhas em fim de vida útil.

Fase:
Troca de manilhas DN1200.

Decisão esperada:
"Sim", pois "troca" e "substituição" são equivalentes e "manilhas" é o objeto principal.

Fase:
Locação de retroescavadeira.

Decisão esperada:
"Parcialmente", pois pode ser recurso de apoio à substituição, mas a descrição é insuficiente para confirmar.

Fase:
Troca de grelhas pluviais.

Decisão esperada:
"Não", pois o objeto principal é diferente.

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
"qualidade_informacao": "Baixa",
"alerta_qualidade": "Descrição curta, mas contém objeto diretamente relacionado ao escopo.",
"justificativa": "A fase menciona troca de manilhas, que é equivalente à substituição de manilhas prevista na atividade principal."
}}
]

Você deve responder todas as fases existentes nos dados.
"""

    resposta_texto = consultar_llm(prompt)
    decisoes = extrair_json(resposta_texto)
    return validar_decisoes(decisoes, analise_semantica)


# =========================
# INTERFACE TKINTER
# =========================

class RagLocalApp:
    def __init__(self, janela: tk.Tk) -> None:
        self.janela = janela
        self.entradas_frases: list[tk.Text] = []
        self._criar_interface()

    def _criar_interface(self) -> None:
        self.janela.title("RAG Local - ChromaDB Filtrado por Fase")
        self.janela.geometry("1450x850")

        titulo = tk.Label(
            self.janela,
            text="RAG Local - ChromaDB com Metadados: arquivo + fase",
            font=("Arial", 16, "bold"),
        )
        titulo.pack(pady=10)

        label_principal = tk.Label(
            self.janela,
            text="Atividade principal:",
            font=("Arial", 11, "bold"),
        )
        label_principal.pack(anchor="w", padx=20)

        self.entrada_principal = tk.Text(self.janela, height=4, width=160)
        self.entrada_principal.pack(padx=20, pady=5)

        for indice in range(5):
            label = tk.Label(
                self.janela,
                text=f"Fase candidata {indice + 1}:",
                font=("Arial", 10, "bold"),
            )
            label.pack(anchor="w", padx=20)

            entrada = tk.Text(self.janela, height=2, width=160)
            entrada.pack(padx=20, pady=3)
            self.entradas_frases.append(entrada)

        botao_run = tk.Button(
            self.janela,
            text="Run RAG - ChromaDB por Fase",
            font=("Arial", 12, "bold"),
            bg="#1F618D",
            fg="white",
            width=35,
            command=self.executar_rag,
        )
        botao_run.pack(pady=10)

        label_tabela = tk.Label(
            self.janela,
            text="Tabela estruturada:",
            font=("Arial", 11, "bold"),
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
            "justificativa",
        )

        frame_tabela = tk.Frame(self.janela)
        frame_tabela.pack(padx=20, pady=5, fill="both", expand=True)

        self.tabela_resultado = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            height=6,
        )

        scroll_vertical = ttk.Scrollbar(
            frame_tabela,
            orient="vertical",
            command=self.tabela_resultado.yview,
        )
        scroll_horizontal = ttk.Scrollbar(
            frame_tabela,
            orient="horizontal",
            command=self.tabela_resultado.xview,
        )

        self.tabela_resultado.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set,
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
            "justificativa": "Justificativa",
        }

        for coluna in colunas:
            self.tabela_resultado.heading(coluna, text=cabecalhos[coluna])

        self.tabela_resultado.column("fase", width=60)
        self.tabela_resultado.column("texto", width=380)
        self.tabela_resultado.column("documento", width=120)
        self.tabela_resultado.column("score_fase", width=100)
        self.tabela_resultado.column("score_documento", width=120)
        self.tabela_resultado.column("decisao", width=120)
        self.tabela_resultado.column("grau", width=90)
        self.tabela_resultado.column("evidencia", width=140)
        self.tabela_resultado.column("justificativa", width=520)

        self.tabela_resultado.grid(row=0, column=0, sticky="nsew")
        scroll_vertical.grid(row=0, column=1, sticky="ns")
        scroll_horizontal.grid(row=1, column=0, sticky="ew")

        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)

        label_resultado = tk.Label(
            self.janela,
            text="Resultado detalhado:",
            font=("Arial", 11, "bold"),
        )
        label_resultado.pack(anchor="w", padx=20)

        self.resultado_texto = tk.Text(self.janela, height=13, width=160)
        self.resultado_texto.pack(padx=20, pady=5)

    def limpar_tabela(self) -> None:
        for item in self.tabela_resultado.get_children():
            self.tabela_resultado.delete(item)

    def preencher_tabela(
        self,
        analise_semantica: list[dict[str, Any]],
        decisoes_llm: list[dict[str, Any]],
    ) -> None:
        self.limpar_tabela()
        decisoes_por_fase = {int(item["fase"]): item for item in decisoes_llm}

        for item in analise_semantica:
            numero_fase = item["numero_fase"]
            decisao = decisoes_por_fase.get(numero_fase, {})

            self.tabela_resultado.insert(
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
                    decisao.get("justificativa", "Sem justificativa")[:180],
                ),
            )

    def executar_rag(self) -> None:
        frase_principal = self.entrada_principal.get("1.0", tk.END).strip()

        if not frase_principal:
            messagebox.showwarning("Aviso", "Digite a atividade principal.")
            return

        fases_validas = []

        for indice, entrada in enumerate(self.entradas_frases):
            texto_fase = entrada.get("1.0", tk.END).strip()

            if texto_fase:
                fases_validas.append(
                    {
                        "numero_fase": indice + 1,
                        "texto_fase": texto_fase,
                    }
                )

        if not fases_validas:
            messagebox.showwarning("Aviso", "Digite pelo menos uma fase candidata.")
            return

        self.resultado_texto.delete("1.0", tk.END)
        self.limpar_tabela()
        self.resultado_texto.insert(tk.END, "Consultando ChromaDB filtrado por fase...\n")
        self.janela.update_idletasks()

        try:
            analise_semantica = calcular_analise_semantica(frase_principal, fases_validas)
            decisoes_llm = decidir_com_llm(frase_principal, analise_semantica)
            self.preencher_tabela(analise_semantica, decisoes_llm)
            self._exibir_resultado(analise_semantica, decisoes_llm)
        except Exception as erro:  # noqa: BLE001 - erro exibido ao usuário final na interface.
            self.resultado_texto.delete("1.0", tk.END)
            self.resultado_texto.insert(
                tk.END,
                f"Erro ao executar a análise.\n\nErro técnico:\n{erro}",
            )

    def _exibir_resultado(
        self,
        analise_semantica: list[dict[str, Any]],
        decisoes_llm: list[dict[str, Any]],
    ) -> None:
        self.resultado_texto.delete("1.0", tk.END)
        self.resultado_texto.insert(
            tk.END,
            "=== ANÁLISE COM CHROMADB FILTRADO POR FASE ===\n\n",
        )

        for item in analise_semantica:
            self.resultado_texto.insert(
                tk.END,
                f"Fase {item['numero_fase']}:\n"
                f"{item['texto_fase']}\n\n"
                f"Score fase/atividade: {item['score_fase']:.4f} "
                f"({item['interpretacao_score_fase']})\n"
                f"Score documento ChromaDB: {item['score_documento']:.4f} "
                f"({item['interpretacao_score_documento']})\n"
                f"Documento encontrado para a fase: "
                f"{'Sim' if item['tem_documento'] else 'Não'}\n\n",
            )

            for chunk in item["chunks_documento"]:
                arquivo = chunk["metadata"].get("arquivo", "Arquivo não informado")
                self.resultado_texto.insert(
                    tk.END,
                    f"- Arquivo: {arquivo} | "
                    f"Fase metadata: {chunk['metadata'].get('fase')} | "
                    f"Distância: {chunk['distancia']:.4f} | "
                    f"Similaridade: {chunk['similaridade']:.4f}\n",
                )

            self.resultado_texto.insert(tk.END, "\n")

        self.resultado_texto.insert(
            tk.END,
            "\n=== DECISÃO FINAL DO LLM EM JSON ===\n\n",
        )
        self.resultado_texto.insert(
            tk.END,
            json.dumps(decisoes_llm, indent=4, ensure_ascii=False),
        )


def main() -> None:
    janela = tk.Tk()
    RagLocalApp(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
