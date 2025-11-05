#!/usr/bin/env python3
# engineer/auto_engineer.py
"""
Orquestrador principal de engenharia assistida por IA.
Analisa projetos, gera patches, testa e aplica melhorias.
"""
import os
import sys
import time
import json
from typing import Dict, List
from pathlib import Path

# Adicionar o diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag_core import load_docs, build_index, retrieve, generate_answer
from core.sandbox import run_in_sandbox
from engineer.logger import get_logger
from engineer.metrics import record_run, record_patch, ensure_metrics
from engineer.patch_generator import suggest_patch, apply_patch
from engineer import git_ops

# Configurar logger
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "history")
os.makedirs(HISTORY_DIR, exist_ok=True)
logger = get_logger("auto_engineer", logfile=os.path.join(HISTORY_DIR, "auto_engineer.log"))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def analyze_with_rag(query: str) -> tuple:
    """
    Analisa uma consulta usando o sistema RAG.
    
    Args:
        query: Consulta textual
        
    Returns:
        Tupla (resposta, documentos_recuperados)
    """
    logger.info(f"Analisando consulta com RAG: {query}")
    
    try:
        docs = load_docs()
        if not docs:
            logger.warning("Nenhum documento disponível no RAG")
            return "Nenhum documento disponível", []
        
        index = build_index(docs)
        retrieved = retrieve(query, index, top_k=3)
        answer = generate_answer(query, retrieved)
        
        logger.info(f"Análise RAG concluída: {len(retrieved)} documentos recuperados")
        return answer, retrieved
        
    except Exception as e:
        logger.error(f"Erro na análise RAG: {e}", exc_info=True)
        return f"Erro: {str(e)}", []

def run_cycle_with_patch(query: str = "análise geral", target_file: str = None, auto_apply: bool = False) -> Dict:
    """
    Executa um ciclo completo de análise e aplicação de patch.
    
    Args:
        query: Consulta para o sistema RAG
        target_file: Arquivo alvo para patch (relativo ao PROJECT_ROOT)
        auto_apply: Se deve aplicar o patch automaticamente
        
    Returns:
        Dicionário com informações da execução
    """
    ensure_metrics()
    start_time = time.time()
    
    logger.info("="*60)
    logger.info("INICIANDO CICLO DE AUTO-ENGENHARIA")
    logger.info("="*60)
    
    # Análise RAG
    try:
        answer, retrieved = analyze_with_rag(query)
        success = True
        details = {
            "answer": answer,
            "retrieved_count": len(retrieved),
            "query": query
        }
        logger.info("Análise RAG concluída com sucesso")
    except Exception as e:
        success = False
        details = {"error": str(e), "query": query}
        logger.error("Erro na análise RAG", exc_info=True)
        answer = None
        retrieved = []
    
    # Geração e aplicação de patch
    patch_info = None
    patch_applied = False
    
    if target_file:
        target_path = os.path.join(PROJECT_ROOT, target_file)
        
        if not os.path.exists(target_path):
            logger.error(f"Arquivo alvo não encontrado: {target_path}")
            details["patch_error"] = "File not found"
        else:
            logger.info(f"Gerando patch para: {target_file}")
            
            # Gerar patch
            patch_info = suggest_patch(target_path, diff_context=f"Query: {query}")
            
            logger.info(f"Patch gerado: método={patch_info.get('method')}, confiança={patch_info.get('confidence', 0):.2f}")
            
            # Salvar sugestão em arquivo temporário
            tmp_patch_file = os.path.join(HISTORY_DIR, "suggested_patch.tmp")
            with open(tmp_patch_file, "w", encoding="utf-8") as f:
                f.write(patch_info.get("suggestion", ""))
            
            logger.info(f"Sugestão de patch salva em: {tmp_patch_file}")
            
            # Testar no sandbox
            logger.info("Testando patch no sandbox...")
            sandbox_ok, sandbox_output = run_in_sandbox(
                PROJECT_ROOT,
                ["python3", "-m", "py_compile", target_file],
                timeout=10
            )
            
            logger.info(f"Teste no sandbox: {'OK' if sandbox_ok else 'FALHOU'}")
            
            if sandbox_ok:
                # Inicializar Git e fazer commit pré-patch
                git_ops.init_repo(PROJECT_ROOT)
                current_commit = git_ops.get_current_commit(PROJECT_ROOT)
                git_ops.commit_all(PROJECT_ROOT, message="pre-patch commit")
                
                # Aplicar patch se auto_apply ou se confiança alta
                should_apply = auto_apply or patch_info.get("confidence", 0) > 0.7
                
                if should_apply:
                    logger.info("Aplicando patch...")
                    patch_applied = apply_patch(target_path, patch_info.get("suggestion", ""))
                    
                    if patch_applied:
                        git_ops.commit_all(PROJECT_ROOT, message=f"auto-patch applied to {target_file}")
                        logger.info("Patch aplicado e commitado")
                        
                        # Registrar patch
                        record_patch({
                            "file": target_file,
                            "method": patch_info.get("method"),
                            "confidence": patch_info.get("confidence"),
                            "applied": True,
                            "commit": git_ops.get_current_commit(PROJECT_ROOT)
                        })
                    else:
                        logger.error("Falha ao aplicar patch")
                else:
                    logger.info(f"Patch não aplicado (confiança: {patch_info.get('confidence', 0):.2f})")
            else:
                logger.warning(f"Patch falhou no sandbox; não aplicando. Output: {sandbox_output}")
                details["sandbox_output"] = sandbox_output
    
    # Calcular duração
    duration = time.time() - start_time
    
    # Montar resultado
    run_info = {
        "success": success,
        "details": details,
        "patch": patch_info,
        "patch_applied": patch_applied,
        "duration": duration
    }
    
    # Registrar execução
    record_run(run_info)
    
    logger.info("="*60)
    logger.info(f"CICLO CONCLUÍDO (duração: {duration:.2f}s)")
    logger.info("="*60)
    
    return run_info

def analyze_project(project_path: str) -> Dict:
    """
    Analisa um projeto e sugere melhorias.
    
    Args:
        project_path: Caminho do projeto
        
    Returns:
        Dicionário com análise e sugestões
    """
    logger.info(f"Analisando projeto: {project_path}")
    
    if not os.path.exists(project_path):
        return {"error": "Project not found"}
    
    # Coletar informações do projeto
    python_files = []
    for root, dirs, files in os.walk(project_path):
        # Ignorar diretórios comuns
        dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '.git', '__pycache__']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    analysis = {
        "project_path": project_path,
        "python_files": len(python_files),
        "suggestions": []
    }
    
    # Analisar alguns arquivos principais
    for py_file in python_files[:5]:  # Limitar a 5 arquivos
        patch_info = suggest_patch(py_file)
        if patch_info.get("improvements"):
            analysis["suggestions"].append({
                "file": py_file,
                "improvements": patch_info["improvements"]
            })
    
    logger.info(f"Análise concluída: {len(analysis['suggestions'])} arquivos com sugestões")
    return analysis

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Engineer: Engenharia assistida por IA")
    parser.add_argument("--query", type=str, default="análise geral", help="Consulta para o sistema RAG")
    parser.add_argument("--file", type=str, default=None, help="Arquivo alvo para patch (relativo ao projeto)")
    parser.add_argument("--auto-apply", action="store_true", help="Aplicar patch automaticamente")
    parser.add_argument("--analyze-project", type=str, help="Analisar um projeto específico")
    parser.add_argument("--cycles", type=int, default=1, help="Número de ciclos a executar")
    args = parser.parse_args()
    
    if args.analyze_project:
        # Modo de análise de projeto
        result = analyze_project(args.analyze_project)
        print("\n" + "="*60)
        print("ANÁLISE DO PROJETO")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="*60)
    else:
        # Modo de ciclo normal
        for i in range(args.cycles):
            if args.cycles > 1:
                print(f"\n{'='*60}")
                print(f"CICLO {i+1}/{args.cycles}")
                print(f"{'='*60}\n")
            
            result = run_cycle_with_patch(
                query=args.query,
                target_file=args.file,
                auto_apply=args.auto_apply
            )
            
            print("\n" + "="*60)
            print("RESULTADO DO CICLO")
            print("="*60)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            print("="*60)
            
            if args.cycles > 1 and i < args.cycles - 1:
                time.sleep(2)  # Pausa entre ciclos

