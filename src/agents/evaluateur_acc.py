import logging
from typing import List, Dict, Any
from src.utils.api_connectors import api_manager

class AgentEvaluateurAccessibilite:
    """Agent 3 (Axel) : Heuristique. Interroge les APIs BAN et SNCF."""
    def __init__(self):
        self.candidates = []
        self.evaluated = []

    def perceive(self, top_candidates: List[Dict[str, Any]]):
        self.candidates = top_candidates
        # 🛠️ CORRECTION ICI : On vide la mémoire avant chaque nouvelle action
        self.evaluated = [] 

    def decide(self):
        for city in self.candidates:
            nom_ville = city['ville']
            
            # Nettoyage pour les APIs : "Paris 15e Arrondissement" devient "Paris"
            nom_recherche = nom_ville.split(" ")[0] if "Arrondissement" in nom_ville else nom_ville
            
            try:
                # 1. API BAN avec le nom nettoyé
                geo_data = api_manager.call_api("BAN", f"https://api-adresse.data.gouv.fr/search/?q={nom_recherche}")
                
                # 2. API SNCF avec le nom nettoyé
                transport_data = api_manager.call_api("SNCF", f"https://api.sncf.com/v1/coverage/sncf/places?q={nom_recherche}")
                
                score_final = transport_data.get('transport_score', 0)
                city['score_accessibilite'] = score_final
                
                if score_final == 0:
                    logging.warning(f"⚠️ [ÉVALUATEUR] Accessibilité nulle ou erreur pour {nom_ville}.")
                else:
                    logging.info(f"✅ [ÉVALUATEUR] Score transport pour {nom_ville} : {score_final}/100")
                    
            except Exception as e:
                logging.warning(f"Impossible d'évaluer {nom_ville} : {str(e)}")
                city['score_accessibilite'] = 0
                
            self.evaluated.append(city)

    def act(self, top_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.perceive(top_candidates)
        self.decide()
        return self.evaluated