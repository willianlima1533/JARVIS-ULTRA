#!/usr/bin/env python3
# engineer/patch_generator.py
"""
Gerador de patches de código com suporte a API de IA e fallback mock.
"""
import os
import json
from typing import Dict
from engineer.logger import get_logger

logger = get_logger("patch_generator")

# Token da API Hugging Face (se disponível)
HF_TOKEN = os.environ.get("HF_API_TOKEN", None)

def _mock_suggest(file_path: str, diff_context: str = "") -> Dict:
    """
    Gerador de sugestões mock (fallback).
    
    Args:
        file_path: Caminho do arquivo
        diff_context: Contexto do diff
        
    Returns:
        Dicionário com sugestão de patch
    """
    logger.info(f"Usando gerador mock para: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return {
            "suggestion": "",
            "confidence": 0.0,
            "method": "mock_error",
            "error": str(e)
        }
    
    # Estratégias simples de melhoria
    suggestions = []
    
    # 1. Adicionar docstrings se faltando
    if 'def ' in content and '"""' not in content and "'''" not in content:
        suggestions.append("Adicionar docstrings às funções")
    
    # 2. Adicionar type hints se faltando
    if 'def ' in content and '->' not in content:
        suggestions.append("Adicionar type hints")
    
    # 3. Melhorar tratamento de erros
    if 'try:' not in content and ('open(' in content or 'json.load' in content):
        suggestions.append("Adicionar tratamento de exceções")
    
    # 4. Adicionar logging
    if 'import logging' not in content and 'def ' in content:
        suggestions.append("Adicionar logging")
    
    # Gerar sugestão baseada nas estratégias
    if suggestions:
        suggestion_text = content + f"\n\n# Sugestões de melhoria:\n"
        for i, sug in enumerate(suggestions, 1):
            suggestion_text += f"# {i}. {sug}\n"
        
        return {
            "suggestion": suggestion_text,
            "confidence": 0.6,
            "method": "mock_analysis",
            "improvements": suggestions
        }
    else:
        return {
            "suggestion": content + "\n# Código parece estar bem estruturado\n",
            "confidence": 0.3,
            "method": "mock_no_changes"
        }

def _hf_suggest(file_path: str, diff_context: str = "") -> Dict:
    """
    Gerador de sugestões usando Hugging Face API.
    
    Args:
        file_path: Caminho do arquivo
        diff_context: Contexto do diff
        
    Returns:
        Dicionário com sugestão de patch
    """
    logger.info(f"Tentando usar Hugging Face API para: {file_path}")
    
    try:
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=HF_TOKEN)
        
        # Ler o arquivo
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        
        # Construir prompt
        prompt = f"""Analyze the following code and suggest improvements for better quality, readability, and maintainability.

Context: {diff_context if diff_context else 'General code review'}

File: {os.path.basename(file_path)}

Code:
```
{file_content[:2000]}  # Limitar tamanho
```

Provide specific, actionable suggestions."""
        
        # Chamar API (usando modelo pequeno para compatibilidade)
        try:
            response = client.text_generation(
                model="gpt2",
                inputs=prompt,
                max_new_tokens=300,
                temperature=0.7
            )
        except Exception as api_error:
            logger.warning(f"Erro na API: {api_error}")
            return None
        
        # Processar resposta
        if isinstance(response, list) and response:
            generated = response[0].get("generated_text", "")
        elif isinstance(response, dict):
            generated = response.get("generated_text", "") or str(response)
        elif response is None:
            return None
        else:
            generated = str(response)
        
        if generated:
            return {
                "suggestion": generated,
                "confidence": 0.75,
                "method": "hf_api",
                "model": "gpt2"
            }
        else:
            return None
            
    except ImportError:
        logger.warning("huggingface_hub não está instalado")
        return None
    except Exception as e:
        logger.error(f"Erro ao usar Hugging Face API: {e}")
        return None

def suggest_patch(file_path: str, diff_context: str = "") -> Dict:
    """
    Sugere um patch para um arquivo.
    
    Args:
        file_path: Caminho do arquivo
        diff_context: Contexto do diff (opcional)
        
    Returns:
        Dicionário com sugestão de patch
    """
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return {
            "suggestion": "",
            "confidence": 0.0,
            "method": "error",
            "error": "File not found"
        }
    
    logger.info(f"Gerando patch para: {file_path}")
    
    # Tentar usar API de IA se disponível
    if HF_TOKEN:
        result = _hf_suggest(file_path, diff_context)
        if result:
            logger.info(f"Patch gerado via HF API (confiança: {result['confidence']})")
            return result
    
    # Fallback para mock
    result = _mock_suggest(file_path, diff_context)
    logger.info(f"Patch gerado via mock (confiança: {result['confidence']})")
    return result

def apply_patch(file_path: str, patch_content: str, backup: bool = True) -> bool:
    """
    Aplica um patch a um arquivo.
    
    Args:
        file_path: Caminho do arquivo
        patch_content: Conteúdo do patch
        backup: Se deve criar backup
        
    Returns:
        True se bem-sucedido
    """
    try:
        # Criar backup se solicitado
        if backup and os.path.exists(file_path):
            backup_path = file_path + ".backup"
            with open(file_path, "r", encoding="utf-8") as f:
                original = f.read()
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(original)
            logger.info(f"Backup criado: {backup_path}")
        
        # Aplicar patch
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(patch_content)
        
        logger.info(f"Patch aplicado com sucesso: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao aplicar patch: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerador de patches")
    parser.add_argument("file", help="Arquivo para analisar")
    parser.add_argument("--context", default="", help="Contexto adicional")
    parser.add_argument("--apply", action="store_true", help="Aplicar o patch sugerido")
    parser.add_argument("--no-backup", action="store_true", help="Não criar backup ao aplicar")
    args = parser.parse_args()
    
    # Gerar sugestão
    result = suggest_patch(args.file, args.context)
    
    print("\n" + "="*60)
    print("PATCH SUGERIDO")
    print("="*60)
    print(f"Método: {result.get('method')}")
    print(f"Confiança: {result.get('confidence', 0):.2f}")
    
    if "improvements" in result:
        print("\nMelhorias sugeridas:")
        for imp in result["improvements"]:
            print(f"  - {imp}")
    
    print("\n" + "-"*60)
    print(result.get("suggestion", "Nenhuma sugestão"))
    print("="*60)
    
    # Aplicar se solicitado
    if args.apply:
        if input("\nAplicar este patch? (s/n): ").lower() == 's':
            success = apply_patch(args.file, result.get("suggestion", ""), backup=not args.no_backup)
            if success:
                print("Patch aplicado com sucesso!")
            else:
                print("Falha ao aplicar patch")

