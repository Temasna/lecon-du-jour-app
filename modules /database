# modules/database.py (version avec ajout d'élève)
import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st

# --- Configuration du chemin de la base de données ---
DB_FOLDER = Path(__file__).parent.parent / "data"
DB_FILE = DB_FOLDER / "progress.db"

# --- Fonctions de la Base de Données ---

def init_db():
    """Initialise la BDD et crée les tables si elles n'existent pas."""
    try:
        DB_FOLDER.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eleves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prenom TEXT NOT NULL UNIQUE,
                classe TEXT 
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lecons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                eleve_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                classe TEXT NOT NULL,
                matiere TEXT NOT NULL,
                sujet TEXT NOT NULL,
                score_quiz_1 INTEGER,
                score_quiz_2 INTEGER,
                appreciation_ia TEXT,
                points_a_revoir TEXT,
                FOREIGN KEY (eleve_id) REFERENCES eleves (id)
            )
        """)

        # Pré-remplir la table avec les élèves par défaut s'ils n'existent pas.
        # INSERT OR IGNORE ne fait rien si le prénom existe déjà.
        eleves_par_defaut = [
            ('Tessnim', 'CM1'),
            ('Rayan', '4ème')
        ]
        cursor.executemany("INSERT OR IGNORE INTO eleves (prenom, classe) VALUES (?, ?)", eleves_par_defaut)

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données lors de l'initialisation : {e}")

# --- NOUVELLE FONCTION ---
def add_student(prenom, classe):
    """Ajoute un nouvel élève à la base de données."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO eleves (prenom, classe) VALUES (?, ?)", (prenom, classe))
        conn.commit()
        conn.close()
        return True, f"L'élève {prenom} a été ajouté."
    except sqlite3.IntegrityError:
        # Cette erreur se produit si le prénom est déjà dans la BDD (à cause de la contrainte UNIQUE)
        conn.close()
        return False, f"Le prénom '{prenom}' existe déjà."
    except sqlite3.Error as e:
        conn.close()
        return False, f"Erreur de base de données : {e}"

# --- Fonctions existantes (get_student_data, get_student_list, save_lesson_result) ---
def get_student_data(eleve_prenom):
    # ... (fonction inchangée)
    try:
        conn = sqlite3.connect(DB_FILE)
        query = """
            SELECT l.date, l.matiere, l.sujet, l.score_quiz_1, l.points_a_revoir
            FROM lecons l
            JOIN eleves e ON l.eleve_id = e.id
            WHERE e.prenom = ?
            ORDER BY l.date ASC
        """
        df = pd.read_sql_query(query, conn, params=(eleve_prenom,))
        conn.close()
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données lors de la récupération des données : {e}")
        return pd.DataFrame()

def get_student_list():
    # ... (fonction inchangée)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT prenom FROM eleves ORDER BY prenom")
        eleves = [row[0] for row in cursor.fetchall()]
        conn.close()
        return eleves
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données lors de la récupération des élèves : {e}")
        return []

def save_lesson_result(data):
    # ... (fonction inchangée)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM eleves WHERE prenom = ?", (data['eleve'],))
        result = cursor.fetchone()
        if result is None:
            st.error(f"L'élève {data['eleve']} n'a pas été trouvé dans la base de données.")
            return False
        eleve_id = result[0]
        insert_query = """
            INSERT INTO lecons (eleve_id, date, classe, matiere, sujet, score_quiz_1, score_quiz_2, appreciation_ia, points_a_revoir)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        lesson_data_tuple = (
            eleve_id, data['date'], data['classe'], data['matiere'],
            data['sujet'], data['score_quiz_1'], data.get('score_quiz_2'),
            data['appreciation_ia'], data['points_a_revoir']
        )
        cursor.execute(insert_query, lesson_data_tuple)
        conn.commit()
        conn.close()
        st.toast("Progrès sauvegardés ! ✅", icon="💾")
        return True
    except sqlite3.Error as e:
        st.error(f"Erreur de base de données lors de la sauvegarde : {e}")
        return False
# Dans modules/database.py

# AJOUTEZ CE BLOC À LA FIN DE modules/database.py

def get_student_class(prenom):
    """Récupère la classe d'un élève spécifique depuis la base de données."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # On sélectionne la colonne 'classe' pour l'élève correspondant
        cursor.execute("SELECT classe FROM eleves WHERE prenom = ?", (prenom,))
        result = cursor.fetchone() # On récupère la première ligne de résultat
        conn.close()
        # Si un résultat a été trouvé, on retourne la première colonne (la classe), sinon None
        return result[0] if result else None
    except sqlite3.Error as e:
        st.error(f"Erreur de BDD lors de la récupération de la classe : {e}")
        return None
