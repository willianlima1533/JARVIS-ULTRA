
import cv2
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Adicionar o diretório pai ao path para importações relativas
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import memory_manager
from core.utils import notify_tts

# Tentar importar DeepFace para análise de emoções
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("[CAMERA] DeepFace não está instalado. Análise de emoções será limitada.")

class CameraPerception:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            memory_manager.log_activity("Erro ao carregar haarcascade_frontalface_default.xml", "ERROR")

    def _capture_frame(self, camera_index: int = 0) -> Optional[Any]:
        """
        Captura um único frame da câmera.
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            memory_manager.log_activity(f"Erro ao abrir a câmera {camera_index}.", "ERROR")
            return None
        
        ret, frame = cap.read()
        cap.release()
        if not ret:
            memory_manager.log_activity("Erro ao capturar frame da câmera.", "ERROR")
            return None
        return frame

    def recognize_face(self, frame: Any) -> bool:
        """
        Detecta faces em um frame e tenta reconhecer (placeholder para reconhecimento).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            memory_manager.log_activity(f"Face(s) detectada(s). Total: {len(faces)}")
            # Aqui poderia ser integrada uma lógica de reconhecimento facial mais avançada
            # com modelos pré-treinados ou banco de dados de faces conhecidas.
            return True
        memory_manager.log_activity("Nenhuma face detectada.")
        return False

    def analyze_emotion(self, frame: Any) -> Optional[Dict[str, Any]]:
        """
        Analisa a emoção em faces detectadas usando DeepFace.
        """
        if not DEEPFACE_AVAILABLE:
            return {"error": "DeepFace não está disponível para análise de emoções.", "dominant_emotion": "desconhecida"}

        try:
            # DeepFace pode detectar múltiplas faces, mas vamos focar na primeira para simplificar
            results = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
            if results:
                # DeepFace retorna uma lista de dicionários, um para cada face detectada
                first_face_result = results[0]
                dominant_emotion = first_face_result.get("dominant_emotion", "desconhecida")
                memory_manager.log_activity(f"Emoção detectada: {dominant_emotion}")
                return {"success": True, "dominant_emotion": dominant_emotion, "full_analysis": first_face_result}
            memory_manager.log_activity("Nenhuma emoção detectada.")
            return {"success": False, "dominant_emotion": "desconhecida"}
        except Exception as e:
            memory_manager.log_activity(f"Erro na análise de emoções com DeepFace: {e}", "ERROR")
            return {"success": False, "dominant_emotion": "erro", "error_message": str(e)}

    def perceive_user_mood(self, camera_index: int = 0) -> Dict[str, Any]:
        """
        Captura uma imagem, detecta faces e analisa a emoção.
        """
        frame = self._capture_frame(camera_index)
        if frame is None:
            return {"success": False, "message": "Não foi possível capturar imagem da câmera.", "dominant_emotion": "desconhecida"}

        face_detected = self.recognize_face(frame)
        if not face_detected:
            return {"success": True, "message": "Nenhuma face detectada.", "dominant_emotion": "desconhecida"}

        emotion_analysis = self.analyze_emotion(frame)
        if emotion_analysis and emotion_analysis.get("success"):
            dominant_emotion = emotion_analysis["dominant_emotion"]
            response_text = f"Pelo que vejo, você parece estar {dominant_emotion}."
            notify_tts(response_text)
            return {"success": True, "message": response_text, "dominant_emotion": dominant_emotion}
        else:
            return {"success": False, "message": "Falha na análise de emoções.", "dominant_emotion": "desconhecida"}

if __name__ == "__main__":
    # Exemplo de uso
    cp = CameraPerception()
    print("Iniciando percepção de humor...")
    result = cp.perceive_user_mood()
    print(result)

    if result.get("dominant_emotion") != "desconhecida":
        print(f"Jarvis diz: Você parece estar {result.get('dominant_emotion')}.")
    else:
        print("Jarvis não conseguiu determinar seu humor.")

