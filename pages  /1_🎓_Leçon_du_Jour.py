# --------------------------------------------------------------------------
# pages/1_🎓_Leçon_du_Jour.py
# Version finale avec appel corrigé à la fonction de base de données.
# --------------------------------------------------------------------------

import streamlit as st
import time
from datetime import datetime
from modules import gemini_handler, database
from modules import style_handler
from pathlib import Path
import random
# --- Configuration de la Page et de l'API ---
st.set_page_config(page_title="Leçon du Jour", page_icon="🎓", layout="centered")

if 'GEMINI_API_KEY' not in st.secrets:
    st.error("❌ Clé API Gemini non trouvée !")
    st.stop()
gemini_handler.configure_gemini()

ALL_CLASSES = ("CP", "CE1", "CE2", "CM1", "CM2", "6ème", "5ème", "4ème", "3ème", "Seconde")

# --- Fonctions Utilitaires ---
def reset_lesson_state():
    keys_to_delete = ['lesson_stage', 'sujet', 'lesson_content', 'quiz_1_data', 'quiz_2_data', 'remediation_content', 'answers', 'score_quiz_1', 'score_quiz_2', 'failed_concepts']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.lesson_stage = 'config'

def display_session_header():
    if 'eleve' in st.session_state and 'classe' in st.session_state and 'matiere' in st.session_state:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1: st.markdown(f"👤 **Élève :** {st.session_state.eleve}")
            with col2: st.markdown(f"🏫 **Classe :** {st.session_state.classe}")
            with col3: st.markdown(f"📚 **Matière :** {st.session_state.matiere}")

# --- Machine à États : Fonctions pour chaque étape ---
def display_config():
    if 'eleve' in st.session_state:
        style_handler.apply_custom_css(st.session_state.eleve)
    st.title("🎓 Leçon du Jour")
    st.markdown("Choisis tes options et lance-toi !")
    
    student_list = database.get_student_list()
    dashboard_student = st.session_state.get('select_eleve')
    index = student_list.index(dashboard_student) if dashboard_student in student_list else 0
    st.session_state.eleve = st.selectbox("Qui es-tu ?", student_list, index=index)
    
    # --- CORRECTION CLÉ : On appelle la fonction via son module 'database' ---
    default_class = database.get_student_class(st.session_state.eleve)
    
    default_index = ALL_CLASSES.index(default_class) if default_class in ALL_CLASSES else 3
    st.session_state.classe = st.selectbox("Ta classe :", ALL_CLASSES, index=default_index)
    
    st.session_state.matiere = st.selectbox("Matière du jour :", ("Mathématiques", "Français", "Histoire", "Sciences", "Anglais", "Allemand", "Surprise !"))
    if st.button("🚀 C'est parti !", type="primary", use_container_width=True):
        st.session_state.lesson_stage = 'generating_lesson'
        st.rerun()

# --- Le reste du fichier est identique à la version précédente ---
# (display_generating_lesson, display_lesson, display_quiz, etc.)
# Je le recopie pour que vous ayez la version complète à copier/coller.

def display_generating_lesson():
    style_handler.apply_custom_css(st.session_state.eleve)
    display_session_header()
    with st.spinner("Ton professeur IA prépare une leçon sur mesure..."):
        response = gemini_handler.generate_lesson_and_quiz(st.session_state.classe, st.session_state.matiere)
    if response and 'sujet' in response:
        st.session_state.sujet = response.get('sujet')
        st.session_state.lesson_content = response.get('lecon_markdown')
        quiz_data = response.get('quiz_10_questions')
        if quiz_data:
            for q in quiz_data:
                if isinstance(q.get('options'), list):
                    random.shuffle(q['options'])
        st.session_state.quiz_1_data = quiz_data
        st.session_state.lesson_stage = 'display_lesson'
        st.rerun()
    else:
        st.error("La génération de la leçon a échoué. L'IA est peut-être occupée.")
        if st.button("Retourner à la configuration"):
            reset_lesson_state()
            st.rerun()

def display_lesson():
    style_handler.apply_custom_css(st.session_state.eleve)
    display_session_header()
    st.header(f"Leçon : {st.session_state.sujet}")
    illustration_dir = Path("assets/illustrations")
    if illustration_dir.exists() and any(f.is_file() for f in illustration_dir.iterdir()):
        illustrations = [f for f in illustration_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
        if illustrations:
            random_image_path = random.choice(illustrations)
            st.image(str(random_image_path), use_column_width=True)
            st.markdown("---")
    st.markdown(st.session_state.lesson_content)
    st.markdown("---")
    if st.button("J'ai tout lu, je suis prêt pour le quiz !", use_container_width=True):
        st.session_state.lesson_stage = 'quiz_1'
        st.rerun()

def display_quiz(quiz_key, quiz_data, next_stage):
    style_handler.apply_custom_css(st.session_state.eleve)
    display_session_header()
    st.header("📝 Quiz - Testons tes connaissances !")
    st.info("Tu dois répondre à toutes les questions pour valider.")
    with st.form(key=quiz_key):
        answers = {}
        for i, q in enumerate(quiz_data):
            string_options = [str(opt) for opt in q['options']]
            answers[i] = st.radio(f"**Question {i+1}:** {q['question']}", string_options, key=f"{quiz_key}_{i}", index=None)
        submitted = st.form_submit_button("J'ai fini, voir ma note !")
        if submitted:
            if None in answers.values():
                st.error("Attention ! Tu dois répondre à toutes les questions avant de valider.")
            else:
                st.session_state.answers = answers
                st.session_state.lesson_stage = next_stage
                st.rerun()

def evaluate_quiz(quiz_data, score_key, success_stage, fail_stage, threshold):
    style_handler.apply_custom_css(st.session_state.eleve)
    display_session_header()
    score = 0
    failed_concepts = []
    for i, q in enumerate(quiz_data):
        selected_answer_str = str(st.session_state.answers[i])
        correct_answer_str = str(q['correct_answer'])
        if selected_answer_str == correct_answer_str:
            score += 1
        elif 'concept' in q:
            failed_concepts.append(q['concept'])
    st.session_state[score_key] = score
    st.session_state.failed_concepts = list(set(failed_concepts))
    st.header(f"Résultat : {score}/{len(quiz_data)}")
    if score >= threshold:
        st.balloons()
        st.success("Bravo, c'est une excellente note !")
        st.session_state.lesson_stage = success_stage
    else:
        st.warning("Ce n'est pas grave ! On va revoir ensemble les points qui ont posé problème.")
        st.session_state.lesson_stage = fail_stage
    if st.button("Continuer"):
        st.rerun()

def display_remediation():
    style_handler.apply_custom_css(st.session_state.eleve)
    display_session_header()
    st.header("🧐 On fait le point")
    with st.spinner("L'IA prépare une explication juste pour toi..."):
        response = gemini_handler.generate_remediation_and_quiz(st.session_state.classe, st.session_state.failed_concepts)
    if response and 'remediation_markdown' in response:
        st.session_state.remediation_content = response.get('remediation_markdown')
        quiz_data_2 = response.get('quiz_5_questions')
        if quiz_data_2:
            for q in quiz_data_2:
                if isinstance(q.get('options'), list):
                    random.shuffle(q['options'])
        st.session_state.quiz_2_data = quiz_data_2
        st.markdown(st.session_state.remediation_content)
        if st.button("OK, j'ai compris, au 2ème quiz !", use_container_width=True):
            st.session_state.lesson_stage = 'quiz_2'
            st.rerun()
    else:
        st.error("La génération de la remédiation a échoué. On passe directement au résumé.")
        if st.button("Continuer vers le résumé"):
            st.session_state.lesson_stage = 'summary'
            st.rerun()

def display_summary():
    style_handler.apply_custom_css(st.session_state.eleve)
    display_session_header()
    st.header("🎉 Leçon terminée !")
    score_1 = st.session_state.score_quiz_1
    a_ete_remedie = 'score_quiz_2' in st.session_state
    with st.spinner("Ton coach IA rédige son appréciation..."):
        if a_ete_remedie:
            score_2 = st.session_state.score_quiz_2
            st.info(f"Score au 1er quiz : {score_1}/10")
            st.info(f"Score au 2ème quiz : {score_2}/5")
            appreciation = gemini_handler.generate_appreciation(score_2, 5, st.session_state.sujet, a_ete_remedie=True)
        else:
            st.info(f"Score final : {score_1}/10")
            appreciation = gemini_handler.generate_appreciation(score_1, 10, st.session_state.sujet)
    st.markdown("---")
    st.subheader("L'avis de ton coach IA :")
    st.markdown(f"> *{appreciation}*")
    st.markdown("---")
    points_a_revoir = ''
    if a_ete_remedie and st.session_state.score_quiz_2 < 3:
        points_a_revoir = ", ".join(st.session_state.failed_concepts)
    db_data = {
        "eleve": st.session_state.eleve, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "classe": st.session_state.classe, "matiere": st.session_state.matiere,
        "sujet": st.session_state.sujet, "score_quiz_1": score_1,
        "score_quiz_2": st.session_state.get('score_quiz_2'), "points_a_revoir": points_a_revoir,
        "appreciation_ia": appreciation
    }
    if database.save_lesson_result(db_data):
        st.cache_data.clear()
    if st.button("Faire une autre leçon", use_container_width=True):
        reset_lesson_state()
        st.rerun()

# --- ROUTEUR PRINCIPAL ---
if 'lesson_stage' not in st.session_state:
    st.session_state.lesson_stage = 'config'
stage = st.session_state.lesson_stage
if stage == 'config':
    display_config()
elif stage == 'generating_lesson':
    display_generating_lesson()
elif stage == 'display_lesson':
    display_lesson()
elif stage == 'quiz_1':
    display_quiz('quiz_1_form', st.session_state.quiz_1_data, 'eval_1')
elif stage == 'eval_1':
    evaluate_quiz(st.session_state.quiz_1_data, 'score_quiz_1', 'summary', 'remediation', 7)
elif stage == 'remediation':
    display_remediation()
elif stage == 'quiz_2':
    display_quiz('quiz_2_form', st.session_state.quiz_2_data, 'eval_2')
elif stage == 'eval_2':
    evaluate_quiz(st.session_state.quiz_2_data, 'score_quiz_2', 'summary', 'summary', 3)
elif stage == 'summary':
    display_summary()
