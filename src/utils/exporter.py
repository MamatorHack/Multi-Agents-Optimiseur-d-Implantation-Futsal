import os
from datetime import datetime

class ReportExporter:
    """Génère un rapport détaillé de l'analyse multi-agents."""
    
    @staticmethod
    def generate_markdown(results: list) -> str:
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        md = f"# 📋 Rapport d'Analyse - Optimiseur Futsal\n"
        md += f"*Généré le : {date_str}*\n\n"
        
        md += "## 🏆 Résumé du Portefeuille\n"
        md += "| Ville | Score Final | Statut | Confiance |\n"
        md += "| :--- | :---: | :--- | :---: |\n"
        
        for res in results:
            score = f"{res.get('score_final', 0):.1f}" if res.get('confiance_systeme') == 'Haute' else "N/A"
            md += f"| {res['ville']} | {score} | {res['STATUT_EXECUTION']} | {res['confiance_systeme']} |\n"
        
        md += "\n---\n\n## 🔍 Détails par Agent\n"
        
        for res in results:
            md += f"### 📍 {res['ville']}\n"
            md += f"**Analyse de l'Agent LLM (Mathias) :**\n> {res.get('sentiment', 'N/A')}\n\n"
            md += "**Détails Techniques :**\n"
            md += f"- Population : {res.get('population', 0):,}\n"
            md += f"- Infrastructures existantes : {res.get('infrastructures_existantes', 0)}\n"
            md += f"- Score Accessibilité (Axel) : {res.get('score_accessibilite', 0)}/100\n"
            md += f"- Score Opportunité (Mathias) : {res.get('score_opportunite_llm', 0)}/100\n"
            md += f"**Verdict Arbitrage (L'Étudiant) :** {res.get('statut_arbitrage', 'N/A')}\n\n"
            md += "---\n"
            
        return md