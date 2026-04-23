import os
import logging
import pandas as pd
from typing import List, Dict, Any

class AgentExtracteurDemographique:
    """Agent 2 (Mathis H.) : Perçoit les sources brutes, décide de leur fiabilité, constitue le portefeuille initial."""

    FUTSAL_KEYWORDS = ['futsal', 'soccer', 'foot 5', 'foot à 5']
    CODES_EXCLUS = ['75056', '13055', '69123']

    def __init__(self):
        self.df_insee = None
        self.df_equip = None
        self.df_master = None

    def perceive(self) -> bool:
        """Charge les deux sources brutes. Retourne False si une source est inaccessible."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        insee_path = os.path.join(base_dir, "data", "insee_demographie.txt")
        equip_path = os.path.join(base_dir, "data", "equipements_sportifs.txt")

        try:
            self.df_equip = pd.read_csv(equip_path, sep=';', encoding='utf-8',
                                        dtype={'Commune INSEE': str}, low_memory=False)
            self.df_equip = self.df_equip.rename(columns={
                'Commune INSEE': 'code_commune', 'Commune Nom': 'ville'
            })
            logging.info(f"[EXTRACTION] Source équipements : {len(self.df_equip)} lignes chargées.")
        except Exception as e:
            logging.error(f"[EXTRACTION] Source équipements inaccessible : {e}")
            return False

        try:
            self.df_insee = pd.read_csv(insee_path, sep=';', encoding='utf-8',
                                        usecols=['CODGEO', 'P21_POP'], dtype={'CODGEO': str})
            self.df_insee = self.df_insee.rename(columns={'CODGEO': 'code_commune', 'P21_POP': 'population'})
            self.df_insee['population'] = pd.to_numeric(self.df_insee['population'], errors='coerce').fillna(0)
            logging.info(f"[EXTRACTION] Source INSEE : {len(self.df_insee)} communes chargées.")
        except Exception as e:
            logging.error(f"[EXTRACTION] Source INSEE inaccessible : {e}")
            return False

        return True

    def decide(self):
        """Fusionne les données et applique les filtres métier pour constituer le portefeuille."""
        city_mapping = self.df_equip.drop_duplicates('code_commune').set_index('code_commune')['ville'].to_dict()

        mask = self.df_equip["Nom de l'équipement sportif"].str.contains(
            '|'.join(self.FUTSAL_KEYWORDS), case=False, na=False
        )
        equip_counts = self.df_equip[mask].groupby('code_commune').size().reset_index(name='infrastructures_existantes')

        df = pd.merge(self.df_insee, equip_counts, on='code_commune', how='left')
        df['infrastructures_existantes'] = df['infrastructures_existantes'].fillna(0).astype(int)
        df['ville'] = df['code_commune'].map(city_mapping).fillna("Inconnue")

        df = df[
            (df['population'] >= 20000) &
            (~df['code_commune'].isin(self.CODES_EXCLUS)) &
            (~df['ville'].str.contains('Arrondissement', case=False, na=False)) &
            (df['ville'] != "Inconnue")
        ]

        df['densite_jeunesse'] = df['population'] * 0.25
        logging.info(f"[EXTRACTION] Portefeuille constitué : {len(df)} communes retenues.")

        self.df_master = df

    def act(self) -> List[Dict[str, Any]]:
        sources_ok = self.perceive()
        if not sources_ok:
            raise RuntimeError("[EXTRACTION] Sources inaccessibles — pipeline interrompu.")
        self.decide()
        return self.df_master.to_dict(orient='records')