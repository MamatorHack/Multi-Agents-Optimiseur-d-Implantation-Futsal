import logging
from typing import Dict, Any
from src.utils.api_connectors import api_manager

class AgentEvaluateurAccessibilite:
    """Agent 3 (Axel) : Analyse technique de l'accessibilité SNCF/Transports."""

    def act(self, city: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue une seule ville à la fois (conçu pour le multithreading)."""
        nom_ville = city.get('ville', 'Inconnue')
        nom_recherche = nom_ville.split(" ")[0] if "Arrondissement" in nom_ville else nom_ville
        
        result = city.copy()
        
        try:
            # 1. On récupère la data brute via l'API manager
            transport_data = api_manager.call_api("SNCF", f"https://api.sncf.com/v1/coverage/sncf/places?q={nom_recherche}")
            
            # 2. Logique métier de l'Agent : Calcul du score
            if "transport_score" in transport_data:
                # Cas où le connecteur a renvoyé l'erreur de sécurité (0)
                score_final = transport_data["transport_score"]
            else:
                # Cas nominal : on compte les arrêts/gares
                places = transport_data.get("places", [])
                nb_gares = len([p for p in places if p.get('embedded_type') == 'stop_area'])
                # Formule : base de 40 points + 15 points par gare (max 100)
                score_final = min(100, 40 + (nb_gares * 15))
            
            result['score_accessibilite'] = score_final
            
            if score_final == 0:
                logging.warning(f"⚠️ [ÉVALUATEUR] Accessibilité nulle ou erreur pour {nom_ville}.")
            else:
                logging.info(f"✅ [ÉVALUATEUR] Score transport pour {nom_ville} : {score_final}/100")
                
        except Exception as e:
            logging.warning(f"Impossible d'évaluer {nom_ville} : {str(e)}")
            result['score_accessibilite'] = 0
            
        return result