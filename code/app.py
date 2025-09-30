import streamlit as st
import os
import random
from pathlib import Path

# --- CONFIGURATION DE BASE ---
# Utilisation de pathlib pour une meilleure gestion des chemins
BASE_DIR = Path("ranges")

st.set_page_config(page_title="Poker Range Trainer", page_icon="♠️", layout="wide")


# --- FONCTIONS UTILITAIRES ---


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
elif page == "Draw My Range":
    st.title("✍️ Draw My Range")

    # --- Initialisation (votre code est bon) ---
    if "draw_answer" not in st.session_state:
        path, answer = get_random_range_from_structure(ALL_RANGES)
        st.session_state.draw_answer = answer
        st.session_state.draw_image_path = path
        st.session_state.show_draw_correction = False
        # Effacer la grille précédente
        for key in list(st.session_state.keys()):
            if key.startswith("draw_cb_"):
                del st.session_state[key]

    correct = st.session_state.draw_answer
    st.info(
        f"Dessiner la range pour **{correct['depth']} / {correct['pos']} / {correct['action']}**"
    )

    # --- Grille de 13x13 (PARTIE CORRIGÉE) ---
    ranks = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

    # Injecter un peu de CSS pour rendre la grille plus compacte et jolie
    st.markdown(
        """
        <style>
            /* Cible les conteneurs des colonnes pour réduire l'espacement */
            div.st-emotion-cache-1r6slb0 {
                gap: 0.1rem;
            }
            /* Centre le contenu des checkboxes et réduit la marge */
            div[data-testid="stCheckbox"] label {
                justify-content: center;
                text-align: center;
                font-size: 0.8rem;
                margin: 0;
                padding: 0.2rem;
                width: 100%;
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.25rem;
                min-width: 35px;           /* Définit une largeur minimale pour la cellule */
                white-space: nowrap;       /* Empêche le texte de passer à la ligne */
        }
            /* Cache le carré de la checkbox elle-même */
            div[data-testid="stCheckbox"] input {
                display: none;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    for r1_idx, r1 in enumerate(ranks):
        # Crée une ligne de 13 colonnes
        cols = st.columns(13)
        for r2_idx, r2 in enumerate(ranks):
            # Logique pour déterminer la main (votre code est bon)
            if r1_idx > r2_idx:
                hand = f"{r2}{r1}o"  # Suited
            elif r1_idx < r2_idx:
                hand = f"{r1}{r2}s"  # Offsuit
            else:
                hand = f"{r1}{r2}"  # Pair

            # Place une checkbox dans sa colonne dédiée
            with cols[r2_idx]:
                # On utilise la main comme label et on ne le cache PAS
                st.checkbox(hand, key=f"draw_cb_{hand}")

    # --- Boutons de contrôle (votre code est bon) ---
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Valider / Voir la réponse", use_container_width=True):
            st.session_state.show_draw_correction = True

    with col2:
        if st.button("➡️ Range Suivante", use_container_width=True):
            del st.session_state.draw_answer
            st.rerun()

    # --- Affichage de la correction (votre code est bon) ---
    if st.session_state.get("show_draw_correction"):
        st.subheader("Range correcte")
        st.warning(
            "La validation automatique n'est pas possible. Comparez visuellement votre grille avec l'image ci-dessous."
        )
        st.image(st.session_state.draw_image_path)
