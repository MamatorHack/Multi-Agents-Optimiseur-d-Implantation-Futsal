import streamlit as st
import pandas as pd
import os
import concurrent.futures
from src.agents.extracteur_demo import AgentExtracteurDemographique
from src.agents.ordonnanceur import AgentOrdonnanceur
from src.agents.evaluateur_acc import AgentEvaluateurAccessibilite
from src.agents.analyste_llm import AgentAnalysteLLM
from src.agents.arbitre import AgentArbitre
from src.agents.moderateur import AgentModerateur
from src.utils.api_connectors import api_manager

st.set_page_config(page_title="Optimiseur SMA Futsal", layout="wide")

st.title("Système Multi-Agents : Optimiseur d'Implantation Futsal")
st.caption("Outil d'aide à la décision stratégique - Validation de projet")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    max_calls = st.slider("Budget API Maximum autorisé", 10, 100, 100)
    os.environ["MAX_DAILY_API_CALLS"] = str(max_calls)
    
    st.header("Monitoring API")
    # Placeholder for dynamic updates
    api_monitor_placeholder = st.empty()
    
    def update_sidebar_monitor():
        """Helper to redraw the sidebar API stats dynamically."""
        usage = api_manager.current_calls
        with api_monitor_placeholder.container():
            st.progress(min(usage/max_calls, 1.0), text=f"Consommation : {usage}/{max_calls}")
            if api_manager.history:
                st.write("Derniers appels :")
                st.table(pd.DataFrame(api_manager.history).tail(3))
                
    update_sidebar_monitor() # Initial draw

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
    
    col_init1, col_init2 = st.columns(2)
    with col_init1:
        with st.expander("Journal d'Ingestion - Mathis H.", expanded=True):
            raw_data = ag_extracteur.act()
            st.write(f"Chargement de {len(raw_data)} communes.")
    with col_init2:
        with st.expander("Journal de Filtrage - Axel", expanded=True):
            shortlist = ag_ordonnanceur.act(raw_data)
            st.write(f"Sélection du Top {len(shortlist)}.")

    st.subheader("Analyse Concurrente par Dossier")
    
    for city in shortlist:
        with st.container(border=True):
            st.write(f"### Ville : {city.get('ville', 'Inconnue')}")
            
            # --- THE BLACKBOARD & THREADING ---
            blackboard = city.copy()
            
            with st.spinner(f"Agents Axel et Mathias en cours d'évaluation asynchrone..."):
                # Execute Agent 3 (API) and Agent 4 (LLM) concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    future_acc = executor.submit(ag_evaluateur.act, city)
                    future_llm = executor.submit(ag_analyste.act, city)
                    
                    # Wait for both agents to finish and update the blackboard
                    acc_result = future_acc.result()
                    llm_result = future_llm.result()
                    
                    blackboard.update(acc_result)
                    blackboard.update(llm_result)
                    
            # Update UI immediately after concurrent API calls
            update_sidebar_monitor()
            
            # Sequential Arbitrage and Moderation
            dossier = ag_arbitre.act(blackboard)
            final = ag_moderateur.act(dossier)
            
            s_acc = final.get('score_accessibilite', 0)
            s_llm = final.get('score_opportunite_llm', 0)
            diff = abs(s_acc - s_llm)
            raw_score = final.get('score_final')
            display_score = f"{raw_score:.1f}/100" if isinstance(raw_score, (int, float)) else "Bloqué"

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Transport (Axel)", f"{s_acc}/100")
            m2.metric("Potentiel IA (Mathias)", f"{s_llm}/100")
            
            if diff > 40:
                m3.metric("Ecart de Risque", f"{diff} pts", delta="Conflit majeur", delta_color="inverse")
            else:
                m3.metric("Ecart de Risque", f"{diff} pts", delta="Consensus", delta_color="normal")
            
            m4.metric("Verdict (Louis)", final.get('STATUT_EXECUTION', 'Inconnu'))

            with st.expander("Consulter le journal d'audit des agents"):
                st.write(f"**Analyse sémantique (Mathias) :** {final.get('sentiment', 'N/A')}")
                st.write(f"**Justification Arbitrage (Mathis M.) :** {final.get('justification_arbitrage', 'N/A')}")
                
                if final.get('confiance_systeme') == "Faible":
                    st.error("Alerte Sécurité : Divergence trop forte détectée. L'investissement est gelé.")
                else:
                    st.success("Note : Les indicateurs techniques et sémantiques sont alignés.")

            results.append(final)

    st.divider()
    st.header("Synthèse de l'Optimiseur")
    
    df = pd.DataFrame(results)
    if "score_final" not in df.columns: df["score_final"] = None
    
    df_show = df[["ville", "population", "score_final", "STATUT_EXECUTION", "confiance_systeme"]]
    df_show.columns = ["Commune", "Population", "Score Final", "Verdict", "Confiance"]
    
    st.table(df_show.sort_values("Score Final", ascending=False, na_position='last'))

    go_cities = [r for r in results if "RECOMMANDATION_FORTE" in r.get('STATUT_EXECUTION', '')]
    if go_cities:
        best = max(go_cities, key=lambda x: x.get('score_final', 0))
        st.success(f"### Recommandation d'implantation prioritaire : **{best.get('ville')}**")
    else:
        st.error("Aucune ville ne remplit les critères de sécurité pour un investissement immédiat.")