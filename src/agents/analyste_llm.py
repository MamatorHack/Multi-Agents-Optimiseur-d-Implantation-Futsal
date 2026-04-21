import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI # Nécessite pip install openai

class AgentAnalysteLLM:
    """Agent 4 : LLM. Analyse Sémantique des risques et atouts via API."""
    def __init__(self):
        self.city = None
        self.analysis_result = {}
        # Initialisation du client (s'assure que OPENAI_API_KEY est dans le .env)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def perceive(self, city: Dict[str, Any]):
        self.city = city

    def decide(self):
        villename = self.city.get("ville", "Inconnue")
        pop = self.city.get("population", 0)
        infras = self.city.get("infrastructures_existantes", 0)
        
        logging.info(f"[ANALYSE LLM] Évaluation sémantique en cours pour {villename}...")
        
        # Le prompt d'instruction stricte
        prompt = f"""
        Tu es un analyste expert en développement de franchises de sport indoor (Futsal).
        Évalue le potentiel d'implantation pour cette ville :
        - Ville : {villename}
        - Population cible : {pop} habitants
        - Concurrence (infrastructures existantes) : {infras}
        
        Génère une analyse stricte et renvoie UNIQUEMENT un objet JSON valide avec ces clés :
        - "sentiment" : Une phrase d'analyse qualitative (ex: "Forte carence malgré un bassin de population idéal").
        - "score_opportunite_llm" : Un entier entre 0 et 100 évaluant la viabilité du projet.
        Ne mets pas de balises markdown, juste le JSON brut.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Modèle rapide et peu coûteux
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2 # Faible température pour des résultats constants
            )
            
            # Parsing de la réponse JSON du LLM
            raw_content = response.choices[0].message.content.strip()
            self.analysis_result = json.loads(raw_content)
            
        except Exception as e:
            logging.error(f"[ANALYSE LLM] Échec pour {villename} : {str(e)}")
            # Fallback en cas d'erreur API pour ne pas crasher le pipeline
            self.analysis_result = {"sentiment": "Erreur d'analyse", "score_opportunite_llm": 50}

    def act(self, city: Dict[str, Any]) -> Dict[str, Any]:
        self.perceive(city)
        self.decide()
        res = city.copy()
        res.update(self.analysis_result)
        return res