# modules/gemini_handler.py
import streamlit as st
import google.generativeai as genai
import json
import re

# --- Configuration de l'API Gemini ---
def configure_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(f"Erreur de configuration de Gemini : {e}")
        st.error("Veuillez vous assurer que votre clé API est correctement configurée dans .streamlit/secrets.toml")
        st.stop()

# --- Fonctions de Génération ---

def _extract_json_from_response(text):
    """
    Fonction utilitaire pour extraire un bloc JSON d'un texte potentiellement mal formaté.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None


# Dans modules/gemini_handler.py

def generate_lesson_and_quiz(classe, matiere):
    """Génère une leçon et un quiz (version simplifiée sans suggestion d'image)."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Agis comme un professeur particulier expert, pédagogue et amusant pour un élève en classe de {classe}.
    Ta mission est de créer une mini-leçon et un quiz.

    SUJET :
    Choisis un sujet FONDAMENTAL et précis de la matière "{matiere}" adapté au niveau "{classe}".

    LEÇON :
    Rédige une leçon courte, engageante et facile à comprendre en utilisant des analogies simples.

    QUIZ :
    Crée un quiz de 10 questions QCM pour évaluer la compréhension de la leçon. Associe chaque question à un "concept" clé.

    FORMAT DE SORTIE (JSON Valide) :
    {{
      "sujet": "Le sujet précis que tu as choisi",
      "lecon_markdown": "Le contenu de la leçon en format Markdown.",
      "quiz_10_questions": [
        {{
          "question": "Texte de la question 1",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_answer": "La bonne réponse exacte",
          "concept": "Le concept évalué"
        }}
      ]
    }}
    """
    # Le reste de la fonction avec l'extraction JSON reste identique.
    raw_text = ""
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        json_str = _extract_json_from_response(raw_text)
        if json_str:
            return json.loads(json_str)
        else:
            st.error("Aucun bloc JSON valide n'a été trouvé dans la réponse de l'IA pour la leçon.")
            st.code(raw_text)
            return None
    except Exception as e:
        st.error(f"Erreur API lors de la génération de la leçon : {e}")
        return None

    except json.JSONDecodeError as e:
        st.error(f"Erreur de décodage JSON lors de la génération de la leçon: {e}")
        st.info("La réponse de l'IA n'était pas un JSON valide. Voici la réponse brute reçue :")
        st.code(raw_text)
        return None
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue avec l'API Gemini : {e}")
        return None

# Les fonctions generate_remediation_and_quiz et generate_appreciation restent inchangées
def generate_remediation_and_quiz(classe, failed_concepts):
    """Génère une explication ciblée et un mini-quiz de 5 questions."""
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    concepts_str = ", ".join(failed_concepts)
    prompt = f"""
    Agis comme un coach scolaire patient et encourageant pour un élève en {classe}.
    L'élève vient de rater des questions sur les concepts suivants : **{concepts_str}**.

    TA MISSION :
    1.  Rédige une explication TRÈS SIMPLE, claire et concise pour l'aider à comprendre SPÉCIFIQUEMENT ces concepts. Utilise une autre analogie ou un autre exemple que la leçon initiale. Si c'est une langue, tu peux utiliser du français pour l'explication.
    2.  Crée un nouveau mini-quiz de 5 questions QCM très ciblées, uniquement sur ces concepts, pour vérifier qu'il a compris.

    FORMAT DE SORTIE :
    Réponds OBLIGATOIREMENT en utilisant un format JSON valide, sans aucun texte avant ou après.
    {{
      "remediation_markdown": "Le contenu de l'explication ciblée en Markdown.",
      "quiz_5_questions": [
        {{
          "question": "Texte de la question 1",
          "options": ["Option A", "Option B", "Option C"],
          "correct_answer": "La bonne réponse exacte"
        }}
      ]
    }}
    """
    raw_text = ""
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        json_str = _extract_json_from_response(raw_text)
        
        if json_str:
            return json.loads(json_str)
        else:
            st.error("Aucun bloc JSON valide n'a été trouvé dans la réponse de l'IA pour la remédiation.")
            st.code(raw_text)
            return None

    except json.JSONDecodeError as e:
        st.error(f"Erreur de décodage JSON lors de la génération de la remédiation: {e}")
        st.info("La réponse de l'IA n'était pas un JSON valide. Voici la réponse brute reçue :")
        st.code(raw_text)
        return None
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue avec l'API Gemini : {e}")
        return None


def generate_appreciation(score, total_questions, sujet, a_ete_remedie=False):
    """Génère une appréciation finale personnalisée."""
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    contexte = f"L'élève a eu {score}/{total_questions} sur le quiz concernant '{sujet}'."
    if a_ete_remedie:
        contexte += " Ce résultat a été obtenu après une session de remédiation, ce qui montre de la persévérance."

    prompt = f"""
    Agis comme un commentateur bienveillant et motivant.
    Rédige une appréciation courte (2-3 phrases) pour un élève en te basant sur le contexte suivant : {contexte}.
    - Si le score est bon, sois très positif et félicite.
    - Si le score est moyen, souligne l'effort et la progression.
    - Si le score est faible, mets l'accent sur la persévérance et le fait que l'échec fait partie de l'apprentissage.
    Ne retourne que le texte de l'appréciation, rien d'autre.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Erreur API lors de la génération de l'appréciation : {e}")
        return "N'oublie pas de toujours faire de ton mieux !"
