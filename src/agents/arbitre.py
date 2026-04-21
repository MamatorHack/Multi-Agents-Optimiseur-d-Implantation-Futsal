import logging
from typing import Dict, Any

class AgentArbitre:
    """Agent 5 : Hybride (Mathis M.). Confronte les scores numériques et l'analyse sémantique."""
    def __init__(self):
        self.profile = None
        self.verdict = {}

    def perceive(self, city_profile: Dict[str, Any]):
        self.profile = city_profile

    def decide(self):
        score_acc = self.profile.get('score_accessibilite', 0)
        score_llm = self.profile.get('score_opportunite_llm', 0)
        
        gap = abs(score_acc - score_llm)
        self.verdict = self.profile.copy()
        
        if gap > 40:
            logging.warning(f"[ARBITRAGE] Conflit détecté pour {self.profile['ville']}. Acc: {score_acc} vs LLM: {score_llm}")
            self.verdict['statut_arbitrage'] = "Conflit_A_L_Etude"
            self.verdict['confiance_systeme'] = "Faible"
        else:
            final_score = (score_acc * 0.4) + (score_llm * 0.6)
            self.verdict['statut_arbitrage'] = "Consensus_Trouve"
            self.verdict['score_final'] = final_score
            self.verdict['confiance_systeme'] = "Haute"

    def act(self, city_profile: Dict[str, Any]) -> Dict[str, Any]:
        self.perceive(city_profile)
        self.decide()
        return self.verdict
