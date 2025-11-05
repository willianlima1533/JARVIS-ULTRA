#!/usr/bin/env python3
# core/rag_core.py
"""
Módulo RAG (Retrieval Augmented Generation) Core.
Implementa indexação e recuperação de documentos com fallback para Annoy.
"""
import json
import os
import hashlib
import math
from typing import List, Dict, Tuple
import random

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def load_docs(docs_file: str = None) -> List[Dict]:
    """
    Carrega documentos do arquivo JSON.
    
    Args:
        docs_file: Caminho do arquivo de documentos (opcional)
        
    Returns:
        Lista de documentos
    """
    if docs_file is None:
        docs_file = os.path.join(DATA_DIR, "docs_store.json")
    
    if not os.path.exists(docs_file):
        print(f"[RAG] Arquivo de documentos não encontrado: {docs_file}")
        return []
    
    with open(docs_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_docs(docs: List[Dict], docs_file: str = None):
    """
    Salva documentos no arquivo JSON.
    
    Args:
        docs: Lista de documentos
        docs_file: Caminho do arquivo de documentos (opcional)
    """
    if docs_file is None:
        docs_file = os.path.join(DATA_DIR, "docs_store.json")
    
    os.makedirs(os.path.dirname(docs_file), exist_ok=True)
    
    with open(docs_file, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    
    print(f"[RAG] Documentos salvos em: {docs_file}")

def simple_embed(text: str, dim: int = 16) -> List[float]:
    """
    Cria um embedding simples baseado em hash.
    
    Args:
        text: Texto para embedar
        dim: Dimensão do embedding
        
    Returns:
        Vetor de embedding normalizado
    """
    h = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)
    
    # Gerar valores pseudo-aleatórios baseados no hash
    rnd = [((h >> (i * 8)) & 0xFF) / 255.0 for i in range(dim)]
    
    # Normalizar o vetor
    norm = math.sqrt(sum(x * x for x in rnd))
    return [x / (norm + 1e-9) for x in rnd]

def build_index(docs: List[Dict], dim: int = 16) -> List[Dict]:
    """
    Constrói um índice de embeddings para os documentos.
    
    Args:
        docs: Lista de documentos
        dim: Dimensão dos embeddings
        
    Returns:
        Lista de itens indexados com embeddings
    """
    print(f"[RAG] Construindo índice para {len(docs)} documentos...")
    
    index = []
    for i, doc in enumerate(docs):
        text = doc.get("text", "")
        emb = simple_embed(text, dim)
        
        index.append({
            "id": doc.get("id", str(i)),
            "emb": emb,
            "meta": {
                "title": doc.get("title", ""),
                "source": doc.get("source", ""),
                "text": text[:200]  # Armazenar preview do texto
            }
        })
    
    print(f"[RAG] Índice construído com sucesso")
    return index

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calcula a similaridade de cosseno entre dois vetores.
    
    Args:
        vec1: Primeiro vetor
        vec2: Segundo vetor
        
    Returns:
        Similaridade de cosseno (0 a 1)
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    return dot_product

def retrieve(query: str, index: List[Dict], top_k: int = 3) -> List[Tuple[Dict, float]]:
    """
    Recupera os documentos mais relevantes para a consulta.
    
    Args:
        query: Consulta textual
        index: Índice de documentos
        top_k: Número de documentos a retornar
        
    Returns:
        Lista de tuplas (metadados, score)
    """
    print(f"[RAG] Recuperando documentos para: '{query}'")
    
    query_emb = simple_embed(query)
    
    similarities = []
    for item in index:
        sim = cosine_similarity(query_emb, item["emb"])
        similarities.append((sim, item))
    
    # Ordenar por similaridade (maior primeiro)
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    # Retornar top_k resultados
    results = [(item["meta"], float(score)) for score, item in similarities[:top_k]]
    
    print(f"[RAG] {len(results)} documentos recuperados")
    return results

def generate_answer(query: str, retrieved: List[Tuple[Dict, float]]) -> str:
    """
    Gera uma resposta baseada nos documentos recuperados.
    
    Args:
        query: Consulta original
        retrieved: Lista de documentos recuperados
        
    Returns:
        Resposta gerada
    """
    if not retrieved:
        return f"Nenhum documento relevante encontrado para: '{query}'"
    
    # Construir resposta com base nos documentos recuperados
    parts = []
    for meta, score in retrieved:
        title = meta.get("title", "Sem título")
        source = meta.get("source", "Desconhecida")
        parts.append(f"**{title}** (fonte: {source}, relevância: {score:.2f})")
    
    references = "\n".join(f"- {p}" for p in parts)
    
    answer = f"""**Resposta para:** "{query}"

**Documentos relevantes encontrados:**

{references}

**Nota:** Esta é uma resposta gerada pelo sistema RAG mock. Para respostas mais precisas, integre com um modelo de linguagem real."""
    
    return answer

def add_document(title: str, text: str, source: str = "manual", docs_file: str = None) -> Dict:
    """
    Adiciona um novo documento ao repositório.
    
    Args:
        title: Título do documento
        text: Conteúdo do documento
        source: Fonte do documento
        docs_file: Caminho do arquivo de documentos (opcional)
        
    Returns:
        Documento adicionado
    """
    docs = load_docs(docs_file)
    
    # Gerar ID único
    doc_id = hashlib.md5(f"{title}{text}".encode("utf-8")).hexdigest()[:12]
    
    new_doc = {
        "id": doc_id,
        "title": title,
        "text": text,
        "source": source
    }
    
    docs.append(new_doc)
    save_docs(docs, docs_file)
    
    print(f"[RAG] Documento adicionado: {title} (ID: {doc_id})")
    return new_doc

def query_rag(query: str, top_k: int = 3, docs_file: str = None) -> str:
    """
    Função de alto nível para consultar o sistema RAG.
    
    Args:
        query: Consulta textual
        top_k: Número de documentos a recuperar
        docs_file: Caminho do arquivo de documentos (opcional)
        
    Returns:
        Resposta gerada
    """
    docs = load_docs(docs_file)
    
    if not docs:
        return "Nenhum documento disponível no sistema. Adicione documentos primeiro."
    
    index = build_index(docs)
    retrieved = retrieve(query, index, top_k)
    answer = generate_answer(query, retrieved)
    
    return answer

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema RAG Core")
    parser.add_argument("--query", help="Consulta para o sistema RAG")
    parser.add_argument("--add-doc", action="store_true", help="Adicionar um novo documento")
    parser.add_argument("--title", help="Título do documento")
    parser.add_argument("--text", help="Texto do documento")
    parser.add_argument("--source", default="manual", help="Fonte do documento")
    parser.add_argument("--top-k", type=int, default=3, help="Número de documentos a recuperar")
    args = parser.parse_args()
    
    if args.add_doc:
        if not args.title or not args.text:
            print("Erro: --title e --text são obrigatórios para adicionar documento")
            exit(1)
        add_document(args.title, args.text, args.source)
    elif args.query:
        answer = query_rag(args.query, args.top_k)
        print("\n" + "="*60)
        print(answer)
        print("="*60)
    else:
        print("Use --query para consultar ou --add-doc para adicionar documento")
        print("Execute com --help para mais informações")

