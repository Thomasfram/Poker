# pages/2_🧠_Quiz.py

import streamlit as st
import random
from utils import get_all_existing_ranges, BASE_DIR

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Range Quiz", page_icon="🧠", layout="wide")
st.title("🧠 Quiz de Ranges")

# --- DATA LOADING ---
ALL_RANGES = get_all_existing_ranges()
QUIZ_LENGTH = 20
ANY = "-- Toutes --"

if not ALL_RANGES:
    st.error(
        f"Le dossier '{BASE_DIR}' est introuvable ou mal structuré. "
        "Veuillez vérifier votre configuration avant de commencer le quiz."
    )
    st.stop()

# --- INITIALIZE SESSION STATE ---
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.question_list = []
    st.session_state.current_question_index = 0
    st.session_state.user_score = 0
    st.session_state.last_answer_feedback = ""


# --- HELPER FUNCTION TO RESET THE QUIZ ---
def reset_quiz():
    """Resets the session state to go back to the setup screen."""
    st.session_state.quiz_started = False
    st.session_state.question_list = []
    st.session_state.current_question_index = 0
    st.session_state.user_score = 0
    st.session_state.last_answer_feedback = ""


# ==============================================================================
# SCREEN 1: QUIZ SETUP
# ==============================================================================
if not st.session_state.quiz_started:
    st.subheader("Configurez votre série de questions")

    # --- FILTERING OPTIONS ---
    depth_list = [ANY] + sorted(ALL_RANGES.keys())
    selected_depth = st.selectbox("Choisissez une profondeur (stack) :", depth_list)

    all_pos = sorted(list(set(p for d in ALL_RANGES.values() for p in d.keys())))
    pos_list = [ANY] + all_pos
    selected_pos = st.selectbox("Choisissez une position :", pos_list)

    # --- START BUTTON ---
    if st.button(
        f"🚀 Commencer une série de {QUIZ_LENGTH} questions",
        use_container_width=True,
        type="primary",
    ):
        possible_questions = []
        for depth, positions in ALL_RANGES.items():
            if selected_depth == ANY or depth == selected_depth:
                for pos, actions in positions.items():
                    if selected_pos == ANY or pos == selected_pos:
                        for action in actions:
                            possible_questions.append(
                                {"depth": depth, "pos": pos, "action": action}
                            )

        if not possible_questions:
            st.error(
                "Aucune range ne correspond à vos filtres. Veuillez élargir votre sélection."
            )
        else:
            is_mixed_quiz = selected_depth == ANY or selected_pos == ANY

            # Generate a list of 20 questions
            if len(possible_questions) < QUIZ_LENGTH:
                st.warning(
                    f"Moins de {QUIZ_LENGTH} ranges correspondent à vos filtres. Certaines questions pourront se répéter."
                )
                sampled_questions = random.choices(possible_questions, k=QUIZ_LENGTH)
            else:
                sampled_questions = random.sample(possible_questions, k=QUIZ_LENGTH)

            # Assign a question type to each question
            final_question_list = []
            for q in sampled_questions:
                if is_mixed_quiz:
                    q["type"] = random.choice(["guess_action", "guess_context"])
                else:
                    q["type"] = "guess_action"
                final_question_list.append(q)

            st.session_state.question_list = final_question_list
            st.session_state.quiz_started = True
            st.rerun()

# ==============================================================================
# SCREEN 2: QUIZ IN PROGRESS
# ==============================================================================
elif st.session_state.current_question_index < QUIZ_LENGTH:
    question = st.session_state.question_list[st.session_state.current_question_index]
    image_path = (
        BASE_DIR / question["depth"] / question["pos"] / f"{question['action']}.png"
    )

    st.progress(
        (st.session_state.current_question_index) / QUIZ_LENGTH,
        text=f"Question {st.session_state.current_question_index + 1}/{QUIZ_LENGTH}  |  Score: {st.session_state.user_score}",
    )

    if st.session_state.last_answer_feedback:
        st.info(st.session_state.last_answer_feedback)

    col_img, col_form = st.columns([2, 1])

    with col_img:
        # Changed to use_container_width=False as requested
        st.image(str(image_path), use_container_width=False)

    with col_form:
        # --- SUB-SCREEN 2.1: GUESS THE ACTION ---
        if question["type"] == "guess_action":
            st.caption(f"Situation: {question['depth']} - {question['pos']}")
            with st.form(key="action_form"):
                st.subheader("Quelle est l'action ?")
                possible_actions = sorted(
                    ALL_RANGES[question["depth"]][question["pos"]]
                )
                user_guess = st.selectbox("Votre réponse :", options=possible_actions)

                if st.form_submit_button("✔️ Valider", use_container_width=True):
                    if user_guess == question["action"]:
                        st.session_state.user_score += 1
                        st.session_state.last_answer_feedback = f"✅ Correct ! L'action était bien **{question['action']}**."
                    else:
                        st.session_state.last_answer_feedback = f"❌ Incorrect. La bonne réponse était **{question['action']}**."

                    st.session_state.current_question_index += 1
                    st.rerun()

        # --- SUB-SCREEN 2.2: GUESS THE CONTEXT (DEPTH & POSITION) ---
        else:  # question['type'] == 'guess_context'
            st.caption(f"Action: {question['action']} - {question['pos']}")
            with st.form(key="context_form"):
                st.subheader("Quelle est la situation ?")
                all_depths = sorted(ALL_RANGES.keys())

                guess_depth = st.selectbox("Profondeur :", options=all_depths)

                if st.form_submit_button("✔️ Valider", use_container_width=True):
                    is_correct = guess_depth == question["depth"]
                    if is_correct:
                        st.session_state.user_score += 1
                        st.session_state.last_answer_feedback = f"✅ Correct ! La situation était bien **{question['depth']} / {question['pos']}**."
                    else:
                        st.session_state.last_answer_feedback = f"❌ Incorrect. La bonne réponse était **{question['depth']} / {question['pos']}**."

                    st.session_state.current_question_index += 1
                    st.rerun()

    if st.button("↩️ Abandonner et retourner au menu"):
        reset_quiz()
        st.rerun()

# ==============================================================================
# SCREEN 3: QUIZ FINISHED
# ==============================================================================
else:
    st.balloons()
    st.title("🎉 Quiz Terminé !")
    score = st.session_state.user_score
    percentage = (score / QUIZ_LENGTH) * 100

    st.metric(
        label="Votre Score Final",
        value=f"{score}/{QUIZ_LENGTH}",
        delta=f"{percentage:.1f}%",
    )

    if percentage >= 80:
        st.success("Excellent travail ! Vous maîtrisez bien ces ranges.")
    elif percentage >= 50:
        st.warning("Pas mal ! Continuez à vous entraîner pour améliorer votre score.")
    else:
        st.error(
            "Il y a encore du travail. N'hésitez pas à utiliser le mode Visualisation pour réviser."
        )

    if st.button(
        "🔁 Changer les filtres et commencer un nouveau quiz",
        use_container_width=True,
        type="primary",
    ):
        reset_quiz()
        st.rerun()
