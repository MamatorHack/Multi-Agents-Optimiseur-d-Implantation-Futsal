import logging
from typing import Dict, Any

class AgentArbitre:
    """Agent 5 : Hybride (Mathis M.). Confronte les scores numériques et l'analyse sémantique."""
    
    def act(self, city_profile: Dict[str, Any]) -> Dict[str, Any]:
        score_acc = city_profile.get('score_accessibilite', 0)
        score_llm = city_profile.get('score_opportunite_llm', 0)
        
        gap = abs(score_acc - score_llm)
        verdict = city_profile.copy()
        
        if gap > 40:
            logging.warning(f"[ARBITRAGE] Conflit détecté pour {city_profile.get('ville')}. Acc: {score_acc} vs LLM: {score_llm}")
            verdict['statut_arbitrage'] = "Conflit_A_L_Etude"
            verdict['confiance_systeme'] = "Faible"
            verdict['justification_arbitrage'] = f"Écart inacceptable ({gap} pts) entre l'analyse transport et l'analyse marché."
        else:
            # Pondération : 40% Accessibilité (Data), 60% Potentiel Marché (IA)
            final_score = (score_acc * 0.4) + (score_llm * 0.6)
            verdict['statut_arbitrage'] = "Consensus_Trouve"
            verdict['score_final'] = final_score
            verdict['confiance_systeme'] = "Haute"
            verdict['justification_arbitrage'] = f"Consensus validé (écart {gap} pts). Application de la pondération standard 40/60."

        return verdict