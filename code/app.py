import streamlit as st
import os
import random

# --- CONFIGURATION DE BASE ---
# Le répertoire où sont stockées vos images de ranges.
BASE_DIR = "Ranges"

st.set_page_config(page_title="Poker Range Trainer", page_icon="♠️", layout="centered")


# --- FONCTIONS UTILITAIRES ---


# Nouvelle fonction pour trouver toutes les images et en choisir une au hasard.
def get_random_range():
    """
    Parcourt l'arborescence du dossier BASE_DIR, trouve toutes les images .png,
    en choisit une au hasard et extrait les informations (profondeur, pos, action)
    à partir de son chemin.
    """
    all_ranges_paths = []
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".png"):
                all_ranges_paths.append(os.path.join(root, file))

    if not all_ranges_paths:
        return None, None  # Gère le cas où aucun fichier n'est trouvé

    # Choix d'un chemin d'image au hasard
    random_path = random.choice(all_ranges_paths)

    # Extraction des informations depuis le chemin du fichier
    parts = random_path.split(os.sep)
    # parts sera comme ['Ranges', '100bb', 'BTNvsBB', 'RFI.png']
    depth = parts[-3]
    pos = parts[-2]
    action = os.path.splitext(parts[-1])[0]  # Enlève l'extension .png

    correct_answer = {"depth": depth, "pos": pos, "action": action}

    return random_path, correct_answer


# --- INTERFACE STREAMLIT ---

# Barre latérale pour la navigation entre les pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choisissez votre mode", ["Visualisation", "Quiz"])

st.sidebar.markdown("---")


# ==============================================================================
# PAGE 1 : VISUALISATION (votre code original, légèrement adapté)
# ==============================================================================
if page == "Visualisation":
    st.title("👁️ Visualisation des Ranges")

    # Sélecteurs dynamiques pour la visualisation
    try:
        depth_list = sorted(os.listdir(BASE_DIR))
        depth = st.sidebar.selectbox("Profondeur", depth_list)

        positions_list = sorted(os.listdir(os.path.join(BASE_DIR, depth)))
        pos = st.sidebar.selectbox("Position", positions_list)

        files_list = sorted(os.listdir(os.path.join(BASE_DIR, depth, pos)))
        # Nettoyage des noms de fichiers pour l'affichage
        actions_list = [f.split(".")[0] for f in files_list if f.endswith(".png")]
        image_name = st.sidebar.selectbox("Action / Sizing", actions_list)

        # Affichage de l'image sélectionnée
        image_path = os.path.join(BASE_DIR, depth, pos, image_name + ".png")
        st.image(image_path)

    except FileNotFoundError:
        st.error(
            f"Le dossier '{BASE_DIR}' est introuvable ou mal structuré. Veuillez vérifier votre arborescence."
        )
    except IndexError:
        st.warning(
            "Il semble manquer des sous-dossiers ou des images. Assurez-vous que chaque dossier de profondeur contient des dossiers de position."
        )


# ==============================================================================
# PAGE 2 : QUIZ (nouvelle page)
# ==============================================================================
elif page == "Quiz":
    st.title("🧠 Quiz : Devinez la Range !")

    # Initialisation de la question si elle n'existe pas dans la session
    if "correct_answer" not in st.session_state:
        # On tire une nouvelle image et on stocke la bonne réponse dans la session
        random_path, correct_ans = get_random_range()
        if random_path is None:
            st.error(
                "Aucune range trouvée ! Vérifiez que le dossier 'Ranges' contient bien des images .png"
            )
        else:
            st.session_state.image_path = random_path
            st.session_state.correct_answer = correct_ans

    # Affichage de l'image de la question actuelle
    st.image(st.session_state.image_path)

    st.markdown("---")

    st.subheader("Quelle est cette range ?")

    # Création des listes complètes pour les menus déroulants du quiz
    # (pour que l'utilisateur ait tous les choix possibles)
    all_depths = sorted(os.listdir(BASE_DIR))
    all_positions = sorted(
        list(set(p for d in all_depths for p in os.listdir(os.path.join(BASE_DIR, d))))
    )
    all_actions = sorted(
        list(
            set(
                os.path.splitext(f)[0]
                for d in all_depths
                for p in all_positions
                if os.path.exists(os.path.join(BASE_DIR, d, p))
                for f in os.listdir(os.path.join(BASE_DIR, d, p))
                if f.endswith(".png")
            )
        )
    )

    # Menus déroulants pour la réponse de l'utilisateur
    col1, col2, col3 = st.columns(3)
    with col1:
        user_depth = st.selectbox("Profondeur", all_depths, key="depth_guess")
    with col2:
        user_pos = st.selectbox("Position", all_positions, key="pos_guess")
    with col3:
        user_action = st.selectbox("Action / Sizing", all_actions, key="action_guess")

    # Boutons de validation et pour passer à la question suivante
    col1_btn, col2_btn = st.columns([1, 1])

    with col1_btn:
        if st.button("✔️ Valider ma réponse"):
            # Logique de vérification
            correct = st.session_state.correct_answer
            if (
                user_depth == correct["depth"]
                and user_pos == correct["pos"]
                and user_action == correct["action"]
            ):
                st.success("🎉 Bravo ! C'est la bonne réponse !")
                st.balloons()
            else:
                st.error("❌ Incorrect.")
                st.info(
                    f"La bonne réponse était : **{correct['depth']} / {correct['pos']} / {correct['action']}**"
                )

    with col2_btn:
        if st.button("➡️ Range suivante"):
            # On efface l'ancienne réponse pour forcer le tirage d'une nouvelle
            if "correct_answer" in st.session_state:
                del st.session_state["correct_answer"]
            st.rerun()
