import streamlit as st
import pandas as pd
import os
import time
from src.agents.extracteur_demo import AgentExtracteurDemographique
from src.agents.ordonnanceur import AgentOrdonnanceur
from src.agents.evaluateur_acc import AgentEvaluateurAccessibilite
from src.agents.analyste_llm import AgentAnalysteLLM
from src.agents.arbitre import AgentArbitre
from src.agents.moderateur import AgentModerateur
from src.utils.api_connectors import api_manager

st.set_page_config(page_title="Optimiseur SMA Futsal", layout="wide")

# --- TITRE ET ENTÊTE ---
st.title("Système Multi-Agents : Optimiseur d'Implantation Futsal")
st.caption("Outil d'aide à la décision stratégique - Validation de projet")
st.markdown("---")

# --- SIDEBAR : CONFIGURATION & MONITORING ---
with st.sidebar:
    st.header("Configuration")
    max_calls = st.slider("Budget API Maximum autorisé", 10, 100, 100)
    os.environ["MAX_DAILY_API_CALLS"] = str(max_calls)
    
    st.header("Monitoring API")
    usage = api_manager.current_calls
    st.progress(min(usage/max_calls, 1.0), text=f"Consommation : {usage}/{max_calls}")
    
    if api_manager.history:
        st.write("Derniers appels :")
        st.table(pd.DataFrame(api_manager.history).tail(3))

# --- HIERARCHIE DES AGENTS ---
st.subheader("Organisation de l'Intelligence Distribuée")
c_arch = st.columns(6)
roles = [
    {"n": "Mathis H.", "r": "Extraction Data", "c": "📥"},
    {"n": "Axel", "r": "Ordonnanceur", "c": "🚦"},
    {"n": "Axel", "r": "Analyste Transport", "c": "🌐"},
    {"n": "Mathias", "r": "Analyste IA", "c": "🧠"},
    {"n": "Mathis M.", "r": "Arbitre Risque", "c": "⚖️"},
    {"n": "Louis", "r": "Modérateur", "c": "🛡️"}
]
for i, col in enumerate(c_arch):
    with col:
        st.info(f"**{roles[i]['n']}**\n\n{roles[i]['r']}")

st.markdown("---")

# --- INITIALISATION ---
ag_extracteur = AgentExtracteurDemographique()
ag_ordonnanceur = AgentOrdonnanceur()
ag_evaluateur = AgentEvaluateurAccessibilite()
ag_analyste = AgentAnalysteLLM()
ag_arbitre = AgentArbitre()
ag_moderateur = AgentModerateur()

if st.button("Lancer l'Analyse du Marché National", width='stretch'):
    results = []
    
    # PHASE 1 & 2
    col_init1, col_init2 = st.columns(2)
    with col_init1:
        with st.expander("Journal d'Ingestion - Mathis H.", expanded=True):
            raw_data = ag_extracteur.act()
            st.write(f"Chargement de {len(raw_data)} communes de plus de 20 000 habitants.")
    with col_init2:
        with st.expander("Journal de Filtrage - Axel", expanded=True):
            shortlist = ag_ordonnanceur.act(raw_data)
            st.write(f"Sélection du Top {len(shortlist)} des zones à plus fort potentiel de carence.")

    st.subheader("Analyse Détaillée par Dossier")
    
    for city in shortlist:
        with st.container(border=True):
            st.write(f"### Ville : {city['ville']}")
            
            # Exécution des agents
            city_acc = ag_evaluateur.act([city])[0]
            city_llm = ag_analyste.act(city_acc)
            dossier = ag_arbitre.act(city_llm)
            final = ag_moderateur.act(dossier)
            
            s_acc = city_acc.get('score_accessibilite', 0)
            s_llm = city_llm.get('score_opportunite_llm', 0)
            diff = abs(s_acc - s_llm)
            raw_score = dossier.get('score_final')
            display_score = f"{raw_score:.1f}/100" if isinstance(raw_score, (int, float)) else "Bloqué"

            # Affichage des métriques
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Transport (Axel)", f"{s_acc}/100")
            m2.metric("Potentiel IA (Mathias)", f"{s_llm}/100")
            
            # Affichage du risque (Mathis M.)
            if diff > 40:
                m3.metric("Ecart de Risque", f"{diff} pts", delta="Conflit majeur", delta_color="inverse")
            else:
                m3.metric("Ecart de Risque", f"{diff} pts", delta="Consensus", delta_color="normal")
            
            m4.metric("Verdict (Louis)", final['STATUT_EXECUTION'])

            # Journal d'audit détaillé
            with st.expander("Consulter le journal d'audit des agents"):
                st.write(f"**Analyse sémantique de Mathias :** {city_llm.get('sentiment')}")
                st.write(f"**Décision d'arbitrage de Mathis M. :** {dossier.get('statut_arbitrage')}")
                
                if final['confiance_systeme'] == "Faible":
                    st.error("Alerte Sécurité : Le système a détecté une divergence trop forte entre les chiffres et l'IA. L'investissement est gelé.")
                elif s_acc < 50:
                    st.warning("Note : Le projet est viable sur le papier mais l'accessibilité transports est jugée insuffisante.")
                else:
                    st.success("Note : Les indicateurs techniques et sémantiques sont alignés.")

            results.append(final)

    # --- SYNTHÈSE FINALE ---
    st.divider()
    st.header("Synthèse de l'Optimiseur")
    
    df = pd.DataFrame(results)
    if "score_final" not in df.columns: df["score_final"] = None
    
    df_show = df[["ville", "population", "score_final", "STATUT_EXECUTION", "confiance_systeme"]]
    df_show.columns = ["Commune", "Population", "Score Final", "Verdict", "Confiance"]
    
    st.table(df_show.sort_values("Score Final", ascending=False, na_position='last'))

    # Recommandation Finale
    go_cities = [r for r in results if "RECOMMANDATION_FORTE" in r.get('STATUT_EXECUTION', '')]
    if go_cities:
        best = max(go_cities, key=lambda x: x.get('score_final', 0))
        st.success(f"### Recommandation d'implantation prioritaire : **{best['ville']}**")
        st.write(f"Cette ville présente le meilleur équilibre entre population cible ({best['population']:,} hab.) et accessibilité.")
    else:
        st.error("Aucune ville ne remplit les critères de sécurité pour un investissement immédiat.")