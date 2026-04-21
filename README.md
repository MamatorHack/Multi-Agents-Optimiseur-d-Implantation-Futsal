# ⚽ Multi-Agents Optimizer : Implantation Stratégique Futsal

Ce projet implémente un **Système Multi-Agents (SMA)** complexe dédié à l'optimisation d'implantation commerciale. Il transforme des données brutes hétérogènes (démographie, transport, infrastructures) en décisions d'investissement qualifiées.

---

## 🏗️ Architecture et Philosophie du Système

Le système est conçu selon le paradigme de la **Distribution du Risque**. Contrairement à une IA linéaire, ce SMA fait cohabiter des agents aux intérêts divergents pour garantir la robustesse du verdict final.



### 1. Ingestion et Nettoyage (Data Engineering)
* **Volume de données :** Traitement de la base nationale (35 000+ communes).
* **Optimisation RAM :** Utilisation de `pandas` avec le paramètre `usecols` et `low_memory=False`. On ne charge que 5 colonnes stratégiques sur les centaines présentes pour éviter le crash mémoire.
* **Filtres Métier Stricts :** * **Seuil de Population :** Seules les villes de > 20 000 habitants sont conservées (viabilité économique).
    * **Exclusion Foncière :** Exclusion automatique des "Arrondissements" (Paris, Lyon, Marseille intra-muros). Le coût du foncier y est incompatible avec les surfaces requises pour le Futsal (2500m²+).
    * **Jointure de données :** Réconciliation des codes INSEE et des noms de communes entre deux bases aux nomenclatures différentes.

### 2. Stratégie de Sobriété API (L'Ordonnanceur)
Pour protéger le budget (OpenAI et SNCF), le système n'analyse pas tout.
* **Le Ratio de Carence :** Formule mathématique exclusive : $Ratio = \frac{\sqrt{Population}}{Infrastructures + 1}$. 
* **Lissage Statistique :** L'utilisation de la racine carrée sur la population permet de ne pas sur-évaluer les mégalopoles et de laisser leur chance aux villes moyennes à fort potentiel.
* **L'Entonnoir :** Seul le Top 10 national (les 10 villes les plus en manque de Futsal) accède aux couches d'IA coûteuses.

---

## 👥 Détail Technique des Agents

### Agent 2 : Mathis H. (Data Ingestion)
Le "Nettoyeur". Il gère les pipelines `Pandas`. Sa mission est de transformer le "bruit" des fichiers `.txt` de l'État en un `Master Dataset` propre. Il résout les erreurs d'encodage (UTF-8/Latin-1) et prépare les dictionnaires de mapping.

### Agent 1 : Axel (Ordonnanceur)
Le "Garde-barrière". Il applique les algorithmes de tri et décide quelles villes méritent d'être approfondies. C'est lui qui garantit que le système ne consommera jamais plus que le budget défini dans le fichier `.env`.

### Agent 3 : Axel (Evaluateur de Transport)
Le "Géographe". Il communique avec les APIs **SNCF (Hove)** et **BAN (Base Adresse Nationale)**. 
* **Normalisation :** Il nettoie les noms de villes avant envoi (ex: suppression des extensions).
* **Fail-safe :** En cas d'erreur API (504 Timeout), il ne bloque pas le système mais dégrade gracieusement la note avec une alerte "Accessibilité nulle".

### Agent 4 : Mathias (Analyste Sémantique LLM)
Le "Cerveau". Via l'API GPT-4o, il apporte le contexte humain. Il analyse si les 16 infrastructures détectées par la data sont de vrais concurrents ou de simples équipements publics non commerciaux. Il donne un "sentiment" de marché.

### Agent 5 : Mathis M. (Arbitre de Risque)
Le "Juge". C'est l'agent le plus critique. Il calcule l'**Écart de Risque**. 
* **Logique :** Si $Ecart = |Score_{Data} - Score_{IA}| > 40$, il considère que le système est en contradiction. 
* **Action :** Il bloque le calcul du score final pour forcer une **Escalade Humaine**, protégeant ainsi l'investisseur d'une erreur algorithmique.

### Agent 6 : Louis (Modérateur)
Le "Décideur". Il traduit les scores en actions concrètes :
* **INVESTISSEMENT VALIDÉ :** Score > 80 + Consensus.
* **ÉTUDE COMPLÉMENTAIRE :** Score 70-80.
* **DOSSIER REJETÉ :** Score < 70 (Protection du capital).

---

## 💻 Interface et Transparence (Streamlit)

L'interface a été conçue pour offrir une **Traceabilité Totale** (Audit Trail). Un utilisateur novice peut comprendre chaque décision grâce au Journal d'Audit qui expose les "pensées" de chaque agent en temps réel.



* **Monitoring API :** Visualisation en direct de la consommation du budget.
* **Indicateur de Risque :** Affichage dynamique des consensus ou des conflits d'arbitrage.
* **Rapport Stratégique :** Synthèse automatique élisant la meilleure ville de France pour l'investissement.

---

## 🛠️ Installation

### 1. Préparation des données
Téléchargez les bases suivantes :
1. [INSEE - Populations légales 2021](https://www.insee.fr/fr/statistiques/8205247) -> Placer dans `data/insee_demographie.txt`
2. [Ministère des Sports - Equipements](https://www.data.gouv.fr/datasets/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques-2) -> Placer dans `data/equipements_sportifs.txt`

### 2. Déploiement
```bash
git clone https://github.com/MamatorHack/Multi-Agents-Optimiseur-d-Implantation-Futsal
pip install -r requirements.txt
streamlit run app.py
```

### 3. Variables d'Environnement (.env)
```env
OPENAI_API_KEY=votre_cle
SNCF_API_KEY=votre_cle
MAX_DAILY_API_CALLS=100
```

---
**Développé par l'équipe : Mathis M., Mathis H., Axel, Mathias, Louis.**