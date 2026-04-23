# ⚽ Multi-Agents Optimizer : Implantation Stratégique Futsal

Ce projet implémente un **Système Multi-Agents (SMA) Asynchrone** dédié à l'optimisation d'implantation commerciale. Il transforme des données brutes hétérogènes (démographie, transport, infrastructures) en décisions d'investissement qualifiées, sous de fortes contraintes de ressources informationnelles.

---

## 🏗️ Architecture et Philosophie du Système

Le système est conçu selon deux paradigmes majeurs de l'ingénierie distribuée : la **Distribution de la Complexité** (Entonnoir de données) et la **Distribution du Risque** (Confrontation d'agents).

### 1. Modèle Blackboard et Multithreading
Contrairement à un pipeline de traitement linéaire classique, le système déploie un design pattern **Blackboard**. L'Agent Transport (API SNCF) et l'Agent IA (OpenAI) sont exécutés dans des threads parallèles (`ThreadPoolExecutor`). Ils travaillent simultanément sur la même ville et inscrivent leurs résultats de manière indépendante sur un état partagé.

### 2. Ingestion et Filtrage (Distribution de la Complexité)
* **Volume de données :** Traitement de la base nationale (35 000+ communes).
* **Optimisation RAM :** Utilisation de `pandas` avec le paramètre `usecols` pour ne charger que la donnée utile en mémoire.
* **Filtres Métier Stricts :** Seules les villes de > 20 000 habitants sont conservées. Les arrondissements des grandes villes (Paris, Lyon, Marseille) sont algorithmiquement exclus car le coût du foncier y est incompatible avec la surface requise pour le Futsal (2500m²+).

### 3. Ordonnancement et Contrainte API (Sobriété)
Le cahier des charges impose une limite stricte de 100 appels API par exécution.
* **Le Ratio de Carence :** Pour définir quelles villes méritent une requête réseau coûteuse, le système classe la France entière via une heuristique propriétaire : $Ratio = \frac{\sqrt{Population}}{Infrastructures\_Existantes + 1}$. 
* **Lissage Statistique :** La racine carrée empêche les mégalopoles d'écraser l'algorithme et révèle le potentiel des villes moyennes. Seul le "Top 10" est transmis aux agents d'évaluation.

---

## 👥 Rôle et Modélisation des Agents

### Agent 1 : Mathis H. (Extracteur & Nettoyeur)
**Le Data Engineer.** Il ingère les fichiers `.txt` de l'INSEE et de Data.gouv, applique les filtres sémantiques (futsal, soccer) et prépare le `Master Dataset` via des jointures sécurisées, tout en gérant les exceptions de fichiers manquants.

### Agent 2 : Axel (Ordonnanceur)
**Le Garde-barrière.** Il applique le calcul du *Ratio de Carence* sur l'ensemble du territoire et tronque le portefeuille pour garantir que le système ne dépassera jamais son quota budgétaire (API).

### Agent 3 : Axel (Évaluateur de Transport)
**Le Géographe (Thread-Safe).** Il interroge l'API **SNCF (Hove)** pour mesurer l'accessibilité réelle. Il nettoie la donnée (noms de communes) et applique une formule d'évaluation stricte : $40 + (Nb\_Gares \times 15)$. Il possède un mécanisme *fail-safe* attribuant un score de 0 en cas de timeout réseau, évitant le crash du système.

### Agent 4 : Mathias (Analyste Sémantique IA)
**Le Cerveau Qualitatif.** Exécuté en asynchrone via l'API OpenAI (`gpt-4o-mini`). 
* **Décorrélation :** Il évalue la ville "à l'aveugle" (uniquement sur le nom) pour ne pas reproduire le calcul mathématique de l'Ordonnanceur. 
* **Self-Reflection :** L'agent analyse sa propre sortie JSON. S'il détecte une dissonance entre son texte (pessimiste) et son score numérique (élevé), il lève un drapeau d'hallucination (`coherence_llm = False`).

### Agent 5 : Mathis M. (Arbitre de Risque)
**Le Juge du Blackboard.** C'est le cœur de la distribution du risque. Il lit les scores asynchrones de l'Agent 3 (Data pure) et de l'Agent 4 (IA).
* **Consensus :** Si l'écart est $\leq 40$, il valide le dossier avec une pondération (40% Transport, 60% IA).
* **Conflit :** Si l'écart est $> 40$, il annule le calcul moyen. Il considère que l'un des agents se trompe lourdement, marque la confiance comme "Faible", et justifie textuellement ce désaccord.

### Agent 6 : Louis (Modérateur)
**Le Décideur.** Il gouverne la sortie finale du système en statuant sur le risque :
* **ESCALADE_HUMAINE_REQUISE :** En cas de conflit (Dossier gelé).
* **RECOMMANDATION_FORTE (Go) :** Score $\geq 80$ validé.
* **RECOMMANDATION (À l'étude) / SIMPLE_INFORMATION :** Scores intermédiaires.

---

## 💻 Observabilité et Paradigme "Boîte de Verre"

Contrairement aux systèmes d'IA dits "boîte noire", notre SMA offre une traçabilité totale des décisions via une interface de gouvernance **Streamlit**.

* **Monitoring Transversal :** L'outil `APIBudgetManager` écoute tous les agents via une méthode universelle (`record_call`) et actualise en temps réel la consommation API sur l'interface (preuve de la sobriété à ~20/100).
* **Journal d'Audit Interactif :** Les décideurs peuvent auditer les justifications de l'Arbitre (Mathis M.) et l'analyse brute du LLM (Mathias) pour chaque dossier évalué.
* **Export Markdown :** Un module dédié (`exporter.py`) génère un rapport final consignant le Ratio de Carence initial, les verdicts et les alertes de sécurité.

---

## 🛠️ Installation et Déploiement

### 1. Préparation des données brutes
* [INSEE - Populations légales 2021](https://www.insee.fr/fr/statistiques/8205247) $\rightarrow$ `data/insee_demographie.txt`
* [Ministère des Sports - Équipements](https://www.data.gouv.fr/datasets/recensement-des-equipements-sportifs-espaces-et-sites-de-pratiques-2) $\rightarrow$ `data/equipements_sportifs.txt`

### 2. Variables d'Environnement (`.env`)
Créez un fichier `.env` à la racine :
```env
OPENAI_API_KEY=sk-xxxx...
SNCF_API_KEY=votre_cle_hove
MAX_DAILY_API_CALLS=100