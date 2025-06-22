# --------------------------------------------------------------------------
# 🏠_Tableau_de_Bord.py
# Version finale avec correction du bug de modification du session_state.
# --------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import altair as alt
from modules import database, style_handler
import time
# --- Configuration de la Page ---
st.set_page_config(
    page_title="Tableau de Bord | Leçon du Jour",
    page_icon="🏠",
    layout="wide"
)

# --- Initialisation de la Base de Données ---
database.init_db()

# --- Fonctions Utilitaires avec Cache ---
@st.cache_data
def load_student_data(student_name):
    return database.get_student_data(student_name)

@st.cache_data
def load_student_list():
    base_list = database.get_student_list()
    return ["➕ Ajouter un nouvel élève..."] + base_list

# --- Interface Principale du Tableau de Bord ---
st.title("🏠 Mon Tableau de Bord")

# --- Sélecteur de Profil ---
student_list_with_add = load_student_list()
eleve_selectionne = st.selectbox(
    "Pour qui est ce tableau de bord ?",
    student_list_with_add,
    key="select_eleve"
)

# --- Logique d'ajout de profil ---
if eleve_selectionne == "➕ Ajouter un nouvel élève...":
    st.header("Création d'un nouveau profil")
    with st.form("new_student_form"):
        new_name = st.text_input("Prénom du nouvel élève :")
        ALL_CLASSES = ("CP", "CE1", "CE2", "CM1", "CM2", "6ème", "5ème", "4ème", "3ème", "Seconde")
        new_class = st.selectbox("Classe :", ALL_CLASSES)
        
        submitted = st.form_submit_button("Enregistrer le profil")
        if submitted:
            if new_name:
                success, message = database.add_student(new_name, new_class)
                if success:
                    st.success(f"Profil pour {new_name} créé avec succès ! Vous pouvez maintenant le sélectionner dans la liste ci-dessus.")
                    # Vider le cache pour recharger la nouvelle liste d'élèves
                    st.cache_data.clear()
                    # On ne modifie PAS st.session_state, on laisse l'utilisateur choisir.
                    # On peut même forcer un rechargement pour rafraîchir le selectbox.
                    time.sleep(2) # Laisse le temps de lire le message de succès
                    st.rerun()
                else:
                    st.error(f"Erreur : {message}")
            else:
                st.error("Veuillez entrer un prénom.")

else:
    # --- Code existant si un profil est sélectionné ---
    
    style_handler.apply_custom_css(eleve_selectionne)
    st.markdown(f"### Bienvenue {eleve_selectionne} ! Voici tes super progrès.")
    progress_data = load_student_data(eleve_selectionne)

    if progress_data.empty:
        st.info(f"👋 Il semble que tu n'aies pas encore terminé de leçon. Va dans la section **'🎓 Leçon du Jour'** pour commencer ton aventure !")
    else:
        # Affichage du bilan et des graphiques (code identique à avant)
        # ... (le reste du fichier est identique)
        st.markdown("---")
        st.header("Bilan Global 🌍")
        col1, col2, col3 = st.columns(3)
        total_lecons = len(progress_data)
        score_moyen_global = progress_data['score_quiz_1'].mean()
        matiere_preferee = progress_data.groupby('matiere')['score_quiz_1'].mean().idxmax()
        with col1:
            st.metric(label="Leçons terminées", value=f"{total_lecons} 🚀")
        with col2:
            st.metric(label="Score moyen global", value=f"{score_moyen_global:.1f}/10")
        with col3:
            st.metric(label="Ta matière favorite", value=f"{matiere_preferee} 🥇")
        st.markdown("---")
        st.header("Progression par Matière 📊")
        score_par_matiere = progress_data.groupby('matiere')['score_quiz_1'].mean().reset_index()
        lecons_par_matiere = progress_data.groupby('matiere').size().reset_index(name='nombre_lecons')
        col_graph1, col_graph2 = st.columns(2)
        with col_graph1:
            st.subheader("Score Moyen")
            bar_chart = alt.Chart(score_par_matiere).mark_bar().encode(
                x=alt.X('matiere:N', title='Matière', sort='-y'),
                y=alt.Y('score_quiz_1:Q', title='Score Moyen', scale=alt.Scale(domain=[0, 10])),
                color=alt.Color('matiere:N', legend=None),
                tooltip=['matiere', alt.Tooltip('score_quiz_1:Q', format='.1f')]
            ).properties(height=300)
            st.altair_chart(bar_chart, use_container_width=True)
        with col_graph2:
            st.subheader("Nombre de Leçons")
            bar_chart_count = alt.Chart(lecons_par_matiere).mark_bar().encode(
                x=alt.X('matiere:N', title='Matière', sort='-y'),
                y=alt.Y('nombre_lecons:Q', title='Nombre de leçons terminées'),
                color=alt.Color('matiere:N', legend=None),
                tooltip=['matiere', 'nombre_lecons']
            ).properties(height=300)
            st.altair_chart(bar_chart_count, use_container_width=True)
        st.markdown("---")
        col1_details, col2_details = st.columns(2)
        with col1_details:
            st.subheader("🏆 Ton Panthéon des Réussites")
            reussites = progress_data[progress_data['score_quiz_1'] >= 8].sort_values(by='date', ascending=False)
            if reussites.empty:
                st.info("Continue tes efforts pour remplir ton panthéon !")
            else:
                for _, row in reussites.head(5).iterrows():
                    st.success(f"**{row['matiere']}** : Super score de **{row['score_quiz_1']}/10** sur '{row['sujet']}' !")
        with col2_details:
            st.subheader("💪 Tes Prochains Défis")
            defis = progress_data[progress_data['points_a_revoir'].notna() & (progress_data['points_a_revoir'] != '')].sort_values(by='date', ascending=False)
            if defis.empty:
                st.info("Aucun défi spécifique pour le moment, bravo !")
            else:
                for _, row in defis.head(5).iterrows():
                    st.warning(f"En **{row['matiere']}**, on pourra revoir : **{row['points_a_revoir']}**.")


st.sidebar.header("Prêt(e) pour aujourd'hui ?")
st.sidebar.info("Clique sur **'🎓 Leçon du Jour'** pour commencer une nouvelle leçon !")