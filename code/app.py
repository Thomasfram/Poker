import base64


import streamlit as st

import random
from pathlib import Path


# --- CONFIGURATION DE BASE ---
# Utilisation de pathlib pour une meilleure gestion des chemins
BASE_DIR = Path("ranges")

st.set_page_config(page_title="Poker Range Trainer", page_icon="♠️", layout="wide")


# --- FONCTIONS UTILITAIRES ---


def get_image_as_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        print("Image OK:", path)
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.error(
            f"Erreur: Le fichier image n'a pas été trouvé à l'emplacement '{path}'. Vérifiez que le chemin est correct."
        )
        return None


@st.cache_data
def get_all_existing_ranges():
    """
    Parcourt une seule fois l'arborescence et retourne un dictionnaire structuré
    de toutes les combinaisons valides (profondeur > position > actions).
    Exemple de retour :
    {
        '100bb': {
            'BTNvsBB': ['RFI', '3bet'],
            'LJvsCO': ['4bet']
        },
        '20bb': { ... }
    }
    """
    structured_ranges = {}
    if not BASE_DIR.is_dir():
        return structured_ranges

    for depth_path in BASE_DIR.iterdir():
        if depth_path.is_dir():
            depth = depth_path.name
            structured_ranges[depth] = {}
            for pos_path in depth_path.iterdir():
                if pos_path.is_dir():
                    pos = pos_path.name
                    actions = [f.stem for f in pos_path.glob("*.png")]
                    if actions:
                        structured_ranges[depth][pos] = sorted(actions)

    # Filtrer les profondeurs ou positions qui seraient vides
    structured_ranges = {d: p for d, p in structured_ranges.items() if p}
    return structured_ranges


def get_random_range_from_structure(all_ranges):
    """
    Choisit une range au hasard à partir du dictionnaire structuré.
    """
    if not all_ranges:
        return None, None

    # Choisir une profondeur, puis une position, puis une action valides
    random_depth = random.choice(list(all_ranges.keys()))
    random_pos = random.choice(list(all_ranges[random_depth].keys()))
    random_action = random.choice(all_ranges[random_depth][random_pos])

    image_path = BASE_DIR / random_depth / random_pos / f"{random_action}.png"

    correct_answer = {"depth": random_depth, "pos": random_pos, "action": random_action}

    return str(image_path), correct_answer


# --- INTERFACE STREAMLIT ---

# Charger les ranges une seule fois
ALL_RANGES = get_all_existing_ranges()

if not ALL_RANGES:
    st.error(
        f"Le dossier '{BASE_DIR}' est introuvable, vide ou mal structuré. "
        f"Veuillez vérifier qu'il contient une arborescence de type : `ranges/profondeur/position/action.png`"
    )
    st.stop()


# Barre latérale pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisissez votre mode", ["Visualisation", "Quiz", "Draw My Range"]
)
st.sidebar.markdown("---")


# ==============================================================================
# PAGE 1 : VISUALISATION
# ==============================================================================
if page == "Visualisation":
    st.title("👁️ Visualisation des Ranges")

    col_img, col_controls = st.columns([3, 1])

    with col_controls:
        st.subheader("Sélectionnez une range")

        depth_list = sorted(ALL_RANGES.keys())
        depth = st.selectbox("Profondeur", depth_list, key="view_depth")

        # Le selectbox de la position dépend de la profondeur choisie
        positions_list = sorted(ALL_RANGES[depth].keys())
        pos = st.selectbox("Position", positions_list, key="view_pos")

        # Le selectbox de l'action dépend de la profondeur et de la position
        actions_list = sorted(ALL_RANGES[depth][pos])
        action = st.selectbox("Action / Sizing", actions_list, key="view_action")

    with col_img:
        image_path = BASE_DIR / depth / pos / f"{action}.png"
        if image_path.is_file():
            st.image(str(image_path))
        else:
            st.error("Image non trouvée.")


# ==============================================================================
# PAGE 2 : QUIZ
# ==============================================================================
elif page == "Quiz":
    st.title("Devinez la Range")

    # Initialisation de la question
    if "quiz_answer" not in st.session_state:
        random_path, correct_ans = get_random_range_from_structure(ALL_RANGES)
        if random_path is None:
            st.error("Aucune range trouvée !")
            st.stop()
        else:
            st.session_state.quiz_image_path = random_path
            st.session_state.quiz_answer = correct_ans

    col_img, col_controls = st.columns([3, 1])

    with col_img:
        st.image(st.session_state.quiz_image_path)

    with col_controls:
        st.subheader("Votre réponse")

        # Sélecteurs dépendants pour le quiz
        depth_list = sorted(ALL_RANGES.keys())
        depth_guess = st.selectbox("Profondeur", depth_list, key="depth_guess")

        positions_list = sorted(ALL_RANGES.get(depth_guess, {}).keys())
        pos_guess = st.selectbox("Position", positions_list, key="pos_guess")

        actions_list = sorted(ALL_RANGES.get(depth_guess, {}).get(pos_guess, []))
        action_guess = st.selectbox("Action", actions_list, key="action_guess")

        st.markdown("---")

        # Boutons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✔️ Valider", use_container_width=True):
                correct = st.session_state.quiz_answer
                is_correct = (
                    depth_guess == correct["depth"]
                    and pos_guess == correct["pos"]
                    and action_guess == correct["action"]
                )

                if is_correct:
                    st.success("🎉 Bravo ! C'est la bonne réponse !")
                else:
                    st.error("❌ Incorrect.")
                    st.info(
                        f"La bonne réponse était : \n\n"
                        f"**{correct['depth']} / {correct['pos']} / {correct['action']}**"
                    )

        with col_btn2:
            if st.button("➡️ Next", use_container_width=True):
                if "quiz_answer" in st.session_state:
                    del st.session_state["quiz_answer"]
                st.rerun()

# ==============================================================================
# PAGE 3 : DRAW MY RANGE (NOUVEAU)
# ==============================================================================
"""if page == "Draw My Range":
    st.title("✍️ Draw My Range")
    # ... (votre code d'initialisation de session_state reste le même) ...
    st.info("Dessinez la range en traçant des rectangles sur la grille.")

    # --- NOUVELLE GRILLE INTERACTIVE AVEC DRAWABLE CANVAS ---

    # 1. Charger votre image de fond avec la librairie PIL

    bg_image = PIL.Image.open("ranges/base.png")

    # 2. Configurer le canvas te
    canvas_result = st_canvas(
        fill_color="rgba(30, 144, 255, 0.4)",  # Couleur de remplissage des rectangles
        stroke_width=0,  # Pas de bordure pour les rectangles
        stroke_color="rgba(0, 0, 0, 0)",
        background_image=bg_image,
        update_streamlit=True,  # Met à jour en temps réel
        height=600,  # Doit correspondre à la hauteur de votre image
        width=600,  # Doit correspondre à la largeur de votre image
        drawing_mode="rect",  # Mode pour dessiner des rectangles
        key="canvas",
    )

    # 3. (Optionnel) Afficher les données dessinées pour le débogage
    if canvas_result.json_data is not None:
        # st.write("Données des sélections :")
        # st.json(canvas_result.json_data) # Décommentez pour voir les coordonnées des rectangles
        pass

    # --- Boutons de contrôle (inchangés) ---
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Valider / Voir la réponse", use_container_width=True):
            st.session_state.show_draw_correction = True

    with col2:
        if st.button("➡️ Range Suivante", use_container_width=True):
            # Il n'y a plus de checkboxes à effacer, mais on peut vouloir reset le canvas
            # Pour l'instant, changer de range relancera la page et donc le canvas.
            del st.session_state.draw_answer
            st.rerun()

    # --- Affichage de la correction (inchangé) ---
    if st.session_state.get("show_draw_correction"):
        st.subheader("Range correcte")
        st.warning("Comparez visuellement votre grille avec l'image ci-dessous.")
        # st.image(st.session_state.draw_image_path) # Assurez-vous que cette variable est bien définie
"""
