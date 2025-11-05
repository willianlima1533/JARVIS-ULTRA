
import requests
import json
import os
from typing import Optional, Dict, Any, List

# Placeholder para o gerenciador de memória e TTS
class MockMemoryManager:
    def log_activity(self, message, level="INFO"):
        print(f"[MemoryManager] {level}: {message}")

class MockVoiceAssistant:
    def notify_tts(self, message):
        print(f"[TTS] {message}")

memory_manager = MockMemoryManager()
voice_assistant = MockVoiceAssistant()

class RealtimeInfoManager:
    def __init__(self):
        # Chaves de API - idealmente carregadas de um arquivo de configuração seguro ou variáveis de ambiente
        self.OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")
        self.NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY", "YOUR_NEWSAPI_API_KEY")
        # Para APIs de localização, pode-se usar OpenStreetMap Nominatim ou Google Places API (com chave)
        # Para este exemplo, vou simular ou usar uma API mais simples.

    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Levanta exceção para status de erro (4xx ou 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            memory_manager.log_activity(f"Erro na requisição para {url}: {e}", "ERROR")
            voice_assistant.notify_tts(f"Erro ao obter informações em tempo real. Verifique a conexão.")
            return None

    def get_weather(self, city: str = "Sao Paulo", country_code: str = "BR") -> Optional[str]:
        """
        Obtém informações meteorológicas para uma cidade específica usando OpenWeatherMap.
        """
        if self.OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
            memory_manager.log_activity("OPENWEATHER_API_KEY não configurada.", "WARNING")
            return "Chave de API OpenWeatherMap não configurada. Não foi possível obter o clima."

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},{country_code}",
            "appid": self.OPENWEATHER_API_KEY,
            "units": "metric", # Celsius
            "lang": "pt_br"
        }
        data = self._make_request(base_url, params)

        if data and data.get("main"):
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            city_name = data["name"]
            return f"O clima em {city_name} é de {description}, com temperatura de {temp:.1f} graus Celsius, sensação térmica de {feels_like:.1f} graus."
        return "Não foi possível obter informações meteorológicas para a cidade especificada."

    def get_news_headlines(self, query: str = "tecnologia", language: str = "pt") -> Optional[List[str]]:
        """
        Obtém manchetes de notícias usando NewsAPI.
        """
        if self.NEWSAPI_API_KEY == "YOUR_NEWSAPI_API_KEY":
            memory_manager.log_activity("NEWSAPI_API_KEY não configurada.", "WARNING")
            return ["Chave de API NewsAPI não configurada. Não foi possível obter notícias."]

        base_url = "https://newsapi.org/v2/top-headlines"
        params = {
            "q": query,
            "language": language,
            "apiKey": self.NEWSAPI_API_KEY
        }
        data = self._make_request(base_url, params)

        if data and data.get("articles"):
            headlines = [article["title"] for article in data["articles"][:5]] # Pegar as 5 primeiras
            return headlines
        return ["Não foi possível obter manchetes de notícias para o tópico especificado."]

    def get_nearby_places(self, latitude: float, longitude: float, radius_km: float = 1.0, query: str = "restaurante") -> Optional[List[str]]:
        """
        Simula a obtenção de lugares próximos usando OpenStreetMap Nominatim ou uma API similar.
        Para uso real, uma chave de API para Google Places ou Foursquare seria necessária.
        Aqui, usaremos uma simulação ou uma API mais simples que não exija chave para requisições básicas.
        
        Usaremos OpenStreetMap Nominatim para uma busca básica, mas é importante notar que ela não é otimizada para "lugares próximos" por raio como o Google Places.
        Para um raio de 1km, o ideal seria uma API de busca de POIs (Pontos de Interesse).
        """
        memory_manager.log_activity(f"Buscando lugares próximos a {latitude}, {longitude} num raio de {radius_km}km...")
        
        # Exemplo de uso do Nominatim para buscar por texto em uma área aproximada
        # Esta não é uma busca por raio exata, mas pode servir como um placeholder.
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query, # Ex: "restaurante", "farmácia", "parque"
            "format": "json",
            "limit": 5, # Limitar resultados
            "lat": latitude,
            "lon": longitude,
            "bounded": 1 # Tenta limitar a busca à área da bounding box, mas não é um raio
        }
        
        # Para uma busca por raio mais precisa, seria necessário:
        # 1. Uma API como Google Places API (requer chave e billing)
        # 2. Um banco de dados local de POIs e cálculo de distância

        try:
            headers = {"User-Agent": "JarvisUltraSentient/1.0 (contact@example.com)"} # Requer User-Agent para Nominatim
            response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            places = []
            if data:
                for place in data:
                    display_name = place.get("display_name")
                    # Filtrar por proximidade (aproximado, Nominatim não dá raio exato)
                    # Para um raio de 1km, precisaríamos calcular a distância manualmente ou usar uma API mais adequada.
                    places.append(display_name)
            if places:
                return places
            return [f"Nenhum {query} encontrado próximo."]
        except requests.exceptions.RequestException as e:
            memory_manager.log_activity(f"Erro na requisição para Nominatim: {e}", "ERROR")
            voice_assistant.notify_tts(f"Erro ao buscar lugares próximos. Verifique a conexão.")
            return ["Não foi possível buscar lugares próximos."]

if __name__ == "__main__":
    # Exemplo de uso
    info_manager = RealtimeInfoManager()

    # Testar clima
    print("\n--- Teste de Clima ---")
    weather_report = info_manager.get_weather("Rio de Janeiro")
    print(weather_report)

    # Testar notícias
    print("\n--- Teste de Notícias ---")
    news_headlines = info_manager.get_news_headlines("inteligência artificial")
    if news_headlines:
        for i, headline in enumerate(news_headlines):
            print(f"{i+1}. {headline}")

    # Testar lugares próximos (usando coordenadas de exemplo para São Paulo)
    print("\n--- Teste de Lugares Próximos ---")
    example_lat = -23.5505
    example_lon = -46.6333
    nearby_restaurants = info_manager.get_nearby_places(example_lat, example_lon, query="restaurante")
    if nearby_restaurants:
        print(f"Restaurantes próximos a {example_lat}, {example_lon}:")
        for i, place in enumerate(nearby_restaurants):
            print(f"{i+1}. {place}")

    nearby_pharmacies = info_manager.get_nearby_places(example_lat, example_lon, query="farmácia")
    if nearby_pharmacies:
        print(f"Farmácias próximas a {example_lat}, {example_lon}:")
        for i, place in enumerate(nearby_pharmacies):
            print(f"{i+1}. {place}")

    # Lembre-se de configurar as chaves de API como variáveis de ambiente ou em um arquivo de configuração seguro.
    # export OPENWEATHER_API_KEY="sua_chave"
    # export NEWSAPI_API_KEY="sua_chave"

