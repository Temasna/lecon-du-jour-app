# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 18:51:43 2025

@author: samet
"""

# modules/style_handler.py
import streamlit as st
import os
import base64
from pathlib import Path

# On définit le chemin racine du projet pour trouver les assets de manière fiable
PROJECT_ROOT = Path(__file__).parent.parent
THEMES = {
    "Tessnim": PROJECT_ROOT / "assets/themes/tessnim_theme.jpg",
    "Rayan": PROJECT_ROOT / "assets/themes/rayan_theme.jpg",
}

@st.cache_data
def get_image_as_base64(path):
    """Charge un fichier image, détecte son type, et le convertit en chaîne Base64."""
    if not os.path.exists(path):
        return None
    ext = Path(path).suffix.lower()
    if ext == ".png":
        mime_type = "image/png"
    elif ext in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    else:
        return None
    with open(path, "rb") as f:
        data = f.read()
    base64_data = base64.b64encode(data).decode()
    return f"data:{mime_type};base64,{base64_data}"

def apply_custom_css(student_name):
    """Injecte le CSS complet et final pour le fond d'écran et la police."""
    default_path = PROJECT_ROOT / "assets/themes/default_theme.png" 
    theme_path = THEMES.get(student_name, default_path)
    
    img_base64_uri = get_image_as_base64(theme_path)
    
    # On ajoute une couleur de fond au cas où l'image ne se charge pas
    fallback_background = "background-color: #0e1117;"
    background_style = f'background-image: url("{img_base64_uri}");' if img_base64_uri else fallback_background

    st.markdown(f"""
        <style>
        /* 1. Fond d'écran et surcouche sombre (avec sélecteur puissant) */
        [data-testid="stAppViewContainer"] {{
            {background_style}
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .main::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(14, 17, 23, 0.6); /* Noir Streamlit avec 60% d'opacité */
            z-index: 0; 
        }}
        /* S'assurer que le contenu est devant la surcouche */
        [data-testid="stVerticalBlock"] {{
            position: relative;
            z-index: 1;
        }}
        
        /* 2. Règles complètes et robustes pour la police */
        html, body, [class*="st-"] {{ font-size: 18px !important; }}
        h1 {{ font-size: 2.8rem !important; }}
        h2 {{ font-size: 2.2rem !important; }}
        h3 {{ font-size: 1.8rem !important; }}
        [data-testid="stMarkdownContainer"] p, li {{ font-size: 1.1rem !important; }}
        .st-emotion-cache-1y4p8pa {{ font-size: 1.2rem !important; }}
        .stButton>button {{ font-size: 1.1rem !important; }}
        [data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stSuccess"], [data-testid="stException"] {{ font-size: 1.1rem !important; }}
        [data-testid="stMetricValue"] {{ font-size: 3rem !important; }}
        [data-testid="stMetricLabel"] {{ font-size: 1.2rem !important; }}
        </style>
    """, unsafe_allow_html=True)