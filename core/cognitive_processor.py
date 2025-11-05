
#!/usr/bin/env python3
# core/cognitive_processor.py
"""
Processador Cognitivo do J.A.R.V.I.S.
Responsável por raciocínio, aprendizado, contextualização e tomada de decisão.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import memory_manager
from core.utils import notify_tts

class CognitiveProcessor:
    def __init__(self):
        memory_manager.ensure_memory() # Garante que a memória está inicializada

    def _analyze_context(self, current_command: str) -> Dict[str, Any]:
        """
        Analisa o contexto atual a partir da memória de trabalho e do comando atual.
        """
        working_memory = memory_manager.get_working_memory()
        context = {
            "current_command": current_command,
            "recent_events": working_memory,
            "preferences": memory_manager.load_memory().get("preferences", {})
        }
        memory_manager.log_activity("Contexto analisado.", "DEBUG")
        return context

    def _reason(self, context: Dict[str, Any]) -> str:
        """
        Realiza raciocínio básico com base no contexto e na memória semântica.
        Esta é uma simplificação e pode ser expandida com modelos de linguagem mais complexos.
        """
        command = context["current_command"].lower()
        response = "Não tenho certeza de como responder a isso." # Resposta padrão

        # Exemplo de raciocínio baseado em padrões e conhecimento semântico
        if "clima" in command or "tempo" in command:
            city = context["preferences"].get("default_city", "sua localização")
            response = f"Para o clima, preciso saber a cidade. Posso verificar o clima em {city} para você?"
        elif "noticias" in command:
            response = "Sobre qual tópico você gostaria de notícias?"
        elif "humor" in command or "emoção" in command:
            response = "Entendi. Você quer que eu analise seu humor pela câmera."
        elif "quem é você" in command or "o que você faz" in command:
            response = "Eu sou o J.A.R.V.I.S, um assistente inteligente projetado para te ajudar com diversas tarefas, desde gerenciar projetos até fornecer informações em tempo real e analisar seu humor."
            memory_manager.store_semantic_knowledge("Jarvis_identity", response)
        
        # Tentar recuperar conhecimento semântico
        for key_phrase, knowledge in memory_manager.load_memory().get("semantic_memory", {}).items():
            if key_phrase.lower() in command:
                response = f"Pelo que sei sobre '{key_phrase}', {knowledge['data']}"
                break

        memory_manager.log_activity(f"Raciocínio concluído. Resposta: {response}", "DEBUG")
        return response

    def _learn_from_interaction(self, command: str, result: Dict[str, Any]):
        """
        Aprende com interações bem-sucedidas ou falhas para melhorar futuras respostas.
        """
        if result.get("success"): # Se a ação foi bem-sucedida
            memory_manager.learn_pattern(f"command_success:{command}", {"command": command, "result": result})
            memory_manager.log_activity(f"Aprendi com o sucesso do comando: {command}")
        else:
            memory_manager.learn_pattern(f"command_failure:{command}", {"command": command, "error": result.get("error")})
            memory_manager.log_activity(f"Aprendi com a falha do comando: {command}", "WARNING")
        
        # Limpar memória de trabalho após a interação ser processada
        memory_manager.clear_working_memory()

    def process_command_cognitively(self, command: str, action_router_func: Callable) -> Dict[str, Any]:
        """
        Processa um comando utilizando raciocínio cognitivo antes de rotear para uma ação.
        """
        memory_manager.log_event("command_received", {"command": command})
        context = self._analyze_context(command)
        
        # Primeiro, tentar rotear o comando diretamente se for uma ação conhecida
        # O action_router já lida com a execução e notificação TTS
        action_result = action_router_func(command)

        if action_result.get("success") or action_result.get("result", {}).get("success"):
            # Se o action_router conseguiu lidar com o comando, aprendemos com isso
            self._learn_from_interaction(command, action_result)
            
            return action_result
        else:
            # Se o action_router não conseguiu, o processador cognitivo tenta gerar uma resposta mais inteligente
            memory_manager.log_activity(f"Action Router não conseguiu lidar com o comando: {command}. Tentando raciocínio cognitivo.", "INFO")
            cognitive_response = self._reason(context)
            notify_tts(cognitive_response)
            self._learn_from_interaction(command, {"success": False, "error": "Cognitive response generated", "response": cognitive_response})
            return {"success": False, "error": "Comando não roteado, resposta cognitiva gerada.", "response": cognitive_response}

if __name__ == "__main__":
    # Teste do CognitiveProcessor
    print("Testando Cognitive Processor...")
    
    cp = CognitiveProcessor()

    # Função dummy para simular o action_router
    def dummy_action_router(cmd: str, **kwargs) -> Dict[str, Any]:
        if "clima em são paulo" in cmd.lower():
            return {"success": True, "result": "O clima em São Paulo está ensolarado."}
        elif "noticias sobre tecnologia" in cmd.lower():
            return {"success": True, "result": ["Novos avanços em IA", "Lançamento de smartphones"]}
        else:
            return {"success": False, "error": "Comando não reconhecido pelo router."}

    # Teste 1: Comando que o router pode lidar
    print("\n--- Teste 1: Comando reconhecido pelo router ---")
    result1 = cp.process_command_cognitively("Jarvis, clima em São Paulo", dummy_action_router)
    print(f"Resultado do processamento: {result1}")

    # Teste 2: Comando que o router NÃO pode lidar, mas o cognitivo pode raciocinar
    print("\n--- Teste 2: Comando com raciocínio cognitivo ---")
    result2 = cp.process_command_cognitively("Jarvis, quem é você?", dummy_action_router)
    print(f"Resultado do processamento: {result2}")

    # Teste 3: Comando que o router NÃO pode lidar, e o cognitivo dá uma resposta padrão
    print("\n--- Teste 3: Comando com resposta padrão ---")
    result3 = cp.process_command_cognitively("Jarvis, me conte uma piada", dummy_action_router)
    print(f"Resultado do processamento: {result3}")

    print("\nMemória de trabalho após testes:")
    print(memory_manager.get_working_memory())

    print("\nPadrões aprendidos:")
    print(memory_manager.load_memory().get("learned_patterns"))

    print("\nCognitive Processor testado com sucesso!")


