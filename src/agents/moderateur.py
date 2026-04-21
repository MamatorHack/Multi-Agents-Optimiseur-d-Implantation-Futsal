import logging
from typing import Dict, Any

class AgentModerateur:
    """Agent 6 : Contrôle final avec échelle de modération stricte."""
    def __init__(self):
        self.dossier = None
        self.dossier_final = {}

    def perceive(self, dossier_arbitre: Dict[str, Any]):
        self.dossier = dossier_arbitre

    def decide(self):
        self.dossier_final = self.dossier.copy()
        confiance = self.dossier.get('confiance_systeme', 'Faible')
        score = self.dossier.get('score_final', 0)
        
        if confiance == "Faible":
            self.dossier_final['STATUT_EXECUTION'] = "ESCALADE_HUMAINE_REQUISE"
            logging.warning(f"[MODÉRATION] Conflit d'agents sur {self.dossier['ville']}. Escalade requise.")
        else:
            # Application de la nouvelle échelle de modération
            if score >= 80:
                self.dossier_final['STATUT_EXECUTION'] = "RECOMMANDATION_FORTE (Go)"
                logging.info(f"[MODÉRATION] {self.dossier['ville']} : Validé avec statut haut.")
            elif score >= 70:
                self.dossier_final['STATUT_EXECUTION'] = "RECOMMANDATION (À l'étude)"
                logging.info(f"[MODÉRATION] {self.dossier['ville']} : Classé en recommandation simple.")
            elif score >= 50:
                self.dossier_final['STATUT_EXECUTION'] = "SIMPLE_INFORMATION"
                logging.info(f"[MODÉRATION] {self.dossier['ville']} : Classé pour information.")
            else:
                self.dossier_final['STATUT_EXECUTION'] = "REJETÉ"
                logging.error(f"[MODÉRATION] {self.dossier['ville']} : Dossier classé sans suite.")

    def act(self, dossier_arbitre: Dict[str, Any]) -> Dict[str, Any]:
        self.perceive(dossier_arbitre)
        self.decide()
        return self.dossier_final