import pandas as pd
import logging
import os
from typing import List, Dict, Any

class DataIngestionPipe:
    """Pipelines de données nationaux (Mathis H.) : Ingestion massive et filtrage métier."""

    @staticmethod
    def load_data() -> pd.DataFrame:
        logging.info("[INGESTION] Nettoyage et fusion des bases nationales...")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        insee_path = os.path.join(base_dir, "data", "insee_demographie.txt")
        equip_path = os.path.join(base_dir, "data", "equipements_sportifs.txt")

        try:
            # 1. Chargement des équipements (pour les noms des villes)
            cols_equip = ['Commune INSEE', 'Commune Nom', "Nom de l'équipement sportif", 
                          "Type d'équipement sportif", "Famille d'équipement sportif"]
            df_equip = pd.read_csv(equip_path, sep=';', encoding='utf-8', dtype={'Commune INSEE': str}, low_memory=False)
            df_equip = df_equip.rename(columns={'Commune INSEE': 'code_commune', 'Commune Nom': 'ville'})

            # Mapping des noms pour éviter les "Commune_XXXX"
            city_mapping = df_equip.drop_duplicates('code_commune').set_index('code_commune')['ville'].to_dict()

            # Filtrage strict Foot à 5 / Futsal
            mask = df_equip["Nom de l'équipement sportif"].str.contains('futsal|soccer|foot 5|foot à 5', case=False, na=False)
            equip_counts = df_equip[mask].groupby('code_commune').size().reset_index(name='infrastructures_existantes')

            # 2. Chargement Démographie (INSEE)
            df_insee = pd.read_csv(insee_path, sep=';', encoding='utf-8', usecols=['CODGEO', 'P21_POP'], dtype={'CODGEO': str})
            df_insee = df_insee.rename(columns={'CODGEO': 'code_commune', 'P21_POP': 'population'})
            df_insee['population'] = pd.to_numeric(df_insee['population'], errors='coerce').fillna(0)

            # 3. Fusion et Filtrage de Sécurité
            df_master = pd.merge(df_insee, equip_counts, on='code_commune', how='left')
            df_master['infrastructures_existantes'] = df_master['infrastructures_existantes'].fillna(0).astype(int)
            df_master['ville'] = df_master['code_commune'].map(city_mapping).fillna("Inconnue")

            # REGLES METIER : 
            # - Plus de 20 000 habitants
            # - Pas les codes globaux de Paris/Lyon/Marseille (car ils faussent l'analyse)
            # - Pas de zones "Arrondissement" (foncier trop cher)
            codes_exclus = ['75056', '13055', '69123']
            df_master = df_master[
                (df_master['population'] >= 20000) & 
                (~df_master['code_commune'].isin(codes_exclus)) &
                (~df_master['ville'].str.contains('Arrondissement', case=False, na=False)) &
                (df_master['ville'] != "Inconnue")
            ]
            
            df_master['densite_jeunesse'] = df_master['population'] * 0.25 
            return df_master.to_dict(orient='records')

        except Exception as e:
            logging.error(f"Erreur Ingestion : {e}")
            raise

    @staticmethod
    def act() -> List[Dict[str, Any]]:
        return DataIngestionPipe.load_data()