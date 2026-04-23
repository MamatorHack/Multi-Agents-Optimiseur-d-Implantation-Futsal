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
            score = f"{res.get('score_final', 0):.1f}" if res.get('confiance_systeme') == 'Haute' else "Bloqué"
            md += f"| {res['ville']} | {score} | {res.get('STATUT_EXECUTION', 'N/A')} | {res.get('confiance_systeme', 'N/A')} |\n"
        
        md += "\n---\n\n## 🔍 Détails par Agent\n"
        
        for res in results:
            md += f"### 📍 {res['ville']}\n"
            md += f"**Analyse de l'Agent LLM (Mathias) :**\n> {res.get('sentiment', 'N/A')}\n\n"
            md += "**Détails Techniques :**\n"
            md += f"- Population : {res.get('population', 0):,}\n"
            md += f"- Infrastructures existantes : {res.get('infrastructures_existantes', 0)}\n"
            
            # Correction : Ajout de la métrique d'ordonnancement
            ratio = res.get('ratio_carence', 0)
            md += f"- Ratio de Carence (Axel) : {ratio:.2f}\n"
            
            md += f"- Score Accessibilité (Axel) : {res.get('score_accessibilite', 0)}/100\n"
            md += f"- Score Opportunité (Mathias) : {res.get('score_opportunite_llm', 0)}/100\n"
            
            # Correction : Vrai nom de l'arbitre et justification
            md += f"\n**Verdict Arbitrage (Mathis M.) :** {res.get('statut_arbitrage', 'N/A')}\n"
            md += f"*Justification : {res.get('justification_arbitrage', 'Non spécifiée')}*\n\n"
            
            # Correction : Mise en valeur visuelle de l'escalade
            if res.get('confiance_systeme') == 'Faible':
                md += "⚠️ **ESCALADE HUMAINE :** Le dossier a été gelé en raison d'une contradiction majeure entre les indicateurs Data et IA.\n\n"
                
            md += "---\n"
            
        return md