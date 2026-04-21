import os
import sys
import logging
from dotenv import load_dotenv

# Ajout magique pour que les imports 'src.utils...' marchent 'First Try' peu importe d'où tu lances le script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.extracteur_demo import AgentExtracteurDemographique
from src.agents.ordonnanceur import AgentOrdonnanceur
from src.agents.evaluateur_acc import AgentEvaluateurAccessibilite
from src.agents.analyste_llm import AgentAnalysteLLM
from src.agents.arbitre import AgentArbitre
from src.agents.moderateur import AgentModerateur

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

def main():
    print("="*60)
    print("🚀 DÉMARRAGE DU PIPELINE SMA : OPTIMISEUR FUTSAL")
    print("="*60)
    
    ag_extracteur = AgentExtracteurDemographique()
    ag_ordonnanceur = AgentOrdonnanceur()
    ag_evaluateur = AgentEvaluateurAccessibilite()
    ag_analyste = AgentAnalysteLLM()
    ag_arbitre = AgentArbitre()
    ag_moderateur = AgentModerateur()
    
    raw_data = ag_extracteur.act()
    shortlist = ag_ordonnanceur.act(raw_data)
    
    print("\n--- Phase d'Évaluation sur les meilleures cibles ---")
    cities_with_acc = ag_evaluateur.act(shortlist)
    
    print("\n--- Phase de Confrontation (LLM vs Data) ---")
    dossiers_finaux = []
    
    for city in cities_with_acc:
        city_with_llm = ag_analyste.act(city)
        dossier_arbitre = ag_arbitre.act(city_with_llm)
        dossier_final = ag_moderateur.act(dossier_arbitre)
        dossiers_finaux.append(dossier_final)

    print("\n" + "="*60)
    print("🏆 RÉSULTATS GLOBAUX DU PORTEFEUILLE")
    print("="*60)
    for res in sorted(dossiers_finaux, key=lambda x: x.get('score_final', 0), reverse=True):
        status = res.get('STATUT_EXECUTION')
        ville = res.get('ville', 'Inconnue')
        score = f"{res.get('score_final', 0):.1f}" if res.get('confiance_systeme') == 'Haute' else "N/A "
        # Remplacement de l'ancienne ligne icon = ... par :
        if status == "RECOMMANDATION_FORTE (Go)":
            icon = "✅"
        elif status == "RECOMMANDATION (À l'étude)":
            icon = "🟡"
        elif status == "SIMPLE_INFORMATION":
            icon = "🔵"
        elif status == "ESCALADE_HUMAINE_REQUISE":
            icon = "⚠️"
        else:
            icon = "❌"
            
        print(f"{icon} VILLE: {ville:<10} | SCORE: {score:<4} | STATUT: {status}")

if __name__ == "__main__":
    main()
