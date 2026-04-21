import os
import logging
from typing import List, Dict, Any

class AgentOrdonnanceur:
    """Agent 1 : L'entonnoir. Applique les règles métier pour économiser le budget API."""
    def __init__(self):
        self.min_pop = int(os.getenv("MIN_POPULATION_THRESHOLD", 20000))
        self.top_k = int(os.getenv("MAX_CANDIDATES_TOP", 10))
        self.candidates = []
        self.top_candidates = []

    def perceive(self, data: List[Dict[str, Any]]):
        self.candidates = data

    def decide(self):
        logging.info("[ORDONNANCEMENT] Filtrage heuristique et lissage statistique.")
        filtered = [c for c in self.candidates if c.get('population', 0) >= self.min_pop]
        
        for c in filtered:
            infras = c.get('infrastructures_existantes', 0)
            pop = c.get('population', 0)
            
            c['ratio_carence'] = (pop ** 0.5) / (infras + 1)
            
        filtered.sort(key=lambda x: x['ratio_carence'], reverse=True)
        self.top_candidates = filtered[:self.top_k]

    def act(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.perceive(data)
        self.decide()
        logging.info(f"[ORDONNANCEMENT] {len(self.top_candidates)} villes retenues pour évaluation externe.")
        return self.top_candidates
