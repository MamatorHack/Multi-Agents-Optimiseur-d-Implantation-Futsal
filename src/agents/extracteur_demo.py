from typing import List, Dict, Any
from src.utils.ingestion import DataIngestionPipe

class AgentExtracteurDemographique:
    """Agent 2 (Mathis H.) : Extrait, nettoie et fusionne les vraies données (INSEE + Data.gouv)."""
    
    def act(self) -> List[Dict[str, Any]]:
        # Fait appel au pipeline optimisé
        return DataIngestionPipe.act()