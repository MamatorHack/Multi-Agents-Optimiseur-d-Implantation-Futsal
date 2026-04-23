import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from src.utils.api_connectors import api_manager

class AgentAnalysteLLM:
    """Agent 4 (Mathias) : IA. Analyse Sémantique à l'aveugle via API OpenAI."""
    
    def __init__(self):
        # Initialisation du client (s'assure que OPENAI_API_KEY est dans le .env)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def act(self, city: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue une seule ville à la fois. Méthode Stateless (Thread-Safe)."""
        villename = city.get('ville', 'Inconnue')
        pop = city.get('population', 0)
        result = city.copy()

        # 1. Ajustement sémantique selon la taille de la ville
        if pop > 100_000:
            focus = (
                "Concentre ton analyse sur le risque de saturation du marché : "
                "présence probable de clubs existants, concurrence structurée, "
                "difficulté à s'imposer dans une grande agglomération."
            )
        else:
            focus = (
                "Concentre ton analyse sur le potentiel de développement : "
                "appétence sportive locale, capacité d'une ville moyenne à porter "
                "ce type de projet, dynamisme associatif."
            )

        prompt = f"""Tu es un analyste expert en développement de franchises de sport indoor (Futsal).
        Évalue le potentiel d'implantation d'un club de Futsal dans cette ville française :
        - Ville : {villename}

        {focus}
        Raisonne uniquement à partir de tes connaissances générales sur cette ville.
        Ne cite pas de chiffres précis que tu ne connais pas avec certitude.

        Renvoie UNIQUEMENT un objet JSON valide avec ces clés :
        - "sentiment" : Une phrase d'analyse qualitative.
        - "score_opportunite_llm" : Un entier entre 0 et 100 évaluant la viabilité du projet.
        Ne mets pas de balises markdown, juste le JSON brut."""

        logging.info(f"[ANALYSE LLM] Évaluation sémantique en cours pour {villename}...")

        # 2. Sécurité du Budget API
        try:
            api_manager.record_call("OpenAI_GPT4")
        except Exception as e:
            logging.error(f"[ANALYSE LLM] Budget API dépassé avant l'analyse de {villename}.")
            result.update({
                "sentiment": "Budget API OpenAI épuisé.",
                "score_opportunite_llm": 50,
                "coherence_llm": False
            })
            return result

        # 3. Exécution et Parsing
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            raw_content = response.choices[0].message.content.strip()
            
            # Nettoyage de sécurité si GPT s'obstine à mettre des balises ```json
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3].strip()
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:-3].strip()
                
            analysis_result = json.loads(raw_content)

            # 4. Décision : valider la cohérence interne de la réponse LLM
            score = analysis_result.get('score_opportunite_llm', 50)
            sentiment = analysis_result.get('sentiment', '').lower()

            mots_positifs = ['potentiel', 'dynamique', 'opportunité', 'favorable', 'fort', 'idéal', 'prometteur']
            mots_negatifs = ['carence', 'difficile', 'faible', 'saturé', 'limité', 'défavorable', 'risque']

            signal_positif = any(mot in sentiment for mot in mots_positifs)
            signal_negatif = any(mot in sentiment for mot in mots_negatifs)

            coherence_llm = True
            if signal_positif and score < 30:
                coherence_llm = False  # sentiment optimiste mais score très bas
            elif signal_negatif and score > 70:
                coherence_llm = False  # sentiment pessimiste mais score très haut

            analysis_result['coherence_llm'] = coherence_llm
            result.update(analysis_result)

        except Exception as e:
            logging.error(f"[ANALYSE LLM] Échec pour {villename} : {str(e)}")
            # Enregistrement de l'erreur dans l'historique API
            if api_manager.history:
                api_manager.history[-1]["status"] = "Erreur IA"
                
            result.update({
                "sentiment": "Erreur d'analyse IA",
                "score_opportunite_llm": 50,
                "coherence_llm": False
            })

        return result