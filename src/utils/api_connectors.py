import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

class APIBudgetManager:
    """Gestionnaire de budget (Axel) : Protection des ressources et logs historiques."""
    def __init__(self):
        self.current_calls = 0
        self.history = []

    def record_call(self, target: str, status: str = "Succès"):
        """Méthode universelle pour logger un appel (utile pour le LLM)."""
        max_calls = int(os.getenv("MAX_DAILY_API_CALLS", 100))
        if self.current_calls >= max_calls:
            raise Exception("API Budget Exceeded")
            
        self.current_calls += 1
        self.history.append({"target": target, "time": time.strftime("%H:%M:%S"), "status": status})

    def call_api(self, target: str, url: str, params: dict = None) -> dict:
        # 1. On enregistre d'abord l'intention d'appel
        self.record_call(target)
        
        sncf_key = os.getenv("SNCF_API_KEY")
        if params and 'q' in params:
            params['q'] = params['q'].split(' ')[0]

        try:
            auth = (sncf_key, '') if target == "SNCF" else None
            response = requests.get(url, params=params, auth=auth, timeout=5)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            # En cas d'échec, on modifie le dernier statut inséré
            self.history[-1]["status"] = "Erreur"
            return {"transport_score": 0}

api_manager = APIBudgetManager()