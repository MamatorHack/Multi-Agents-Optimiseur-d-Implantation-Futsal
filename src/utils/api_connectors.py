import os
import time
import requests
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

class APIBudgetManager:
    """Gestionnaire de budget (Axel) : Protection des ressources et logs historiques."""
    def __init__(self):
        self.current_calls = 0
        self.history = []

    def call_api(self, target: str, url: str, params: dict = None) -> dict:
        max_calls = int(os.getenv("MAX_DAILY_API_CALLS", 100))
        if self.current_calls >= max_calls:
            raise Exception("API Budget Exceeded")
        
        self.current_calls += 1
        sncf_key = os.getenv("SNCF_API_KEY")
        
        # Nettoyage du nom pour l'API (ex: "Nantes 01" -> "Nantes")
        if params and 'q' in params:
            params['q'] = params['q'].split(' ')[0]

        try:
            auth = (sncf_key, '') if target == "SNCF" else None
            response = requests.get(url, params=params, auth=auth, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            self.history.append({"target": target, "time": time.strftime("%H:%M:%S"), "status": "Succès"})
            
            if target == "SNCF":
                places = data.get("places", [])
                nb = len([p for p in places if p.get('embedded_type') == 'stop_area'])
                return {"transport_score": min(100, 40 + (nb * 15))}
            
            return data # BAN
            
        except Exception as e:
            self.history.append({"target": target, "time": time.strftime("%H:%M:%S"), "status": "Erreur"})
            return {"transport_score": 0}

api_manager = APIBudgetManager()