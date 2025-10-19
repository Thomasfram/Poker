import streamlit as st
import random
import time
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from utils import get_all_existing_ranges, BASE_DIR

# ======================================================================
# CONFIGURATION GLOBALE
# ======================================================================
st.set_page_config(page_title="Range Quiz", page_icon="🧠", layout="wide")
st.title("🧠 Quiz de Ranges")

QUIZ_LENGTH = 5
ANY = "-- Toutes --"
HISTORY_FILE = Path(BASE_DIR) / "quiz_history.json"  # sauvegarde locale


# ======================================================================
# FONCTIONS DE SAUVEGARDE / CHARGEMENT
# ======================================================================
def load_history():
    """Charge l’historique depuis un fichier JSON si présent."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # convertir les dates en datetime
            for d in data:
                d["date"] = datetime.fromisoformat(d["date"])
            return data
        except Exception:
            return []
    return []


def save_history(history_list):
    """Sauvegarde l’historique complet dans un JSON."""
    try:
        export_data = [
            {"date": d["date"].isoformat(), "score": d["score"]} for d in history_list
        ]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"⚠️ Impossible d’enregistrer l’historique : {e}")


# ======================================================================
# CHARGEMENT DES RANGES (cache)
# ======================================================================
@st.cache_data
def load_ranges():
    return get_all_existing_ranges()


ALL_RANGES = load_ranges()
if not ALL_RANGES:
    st.error(f"Le dossier '{BASE_DIR}' est introuvable ou mal structuré.")
    st.stop()

# ======================================================================
# INITIALISATION DU SESSION STATE
# ======================================================================
_initial_state = {
    "quiz_started": False,
    "question_list": [],
    "current_question_index": 0,
    "user_score": 0,
    "last_answer_feedback": "",
    "last_answer_correct": False,
    "responses": [],
    "streak": 0,
    "question_start": None,
    "quiz_history": load_history(),
}
for k, v in _initial_state.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ======================================================================
# UTILITAIRES
# ======================================================================
def feedback_box(message, correct=True):
    """Affichage stylé d’un message de feedback."""
    theme = "dark"
    if correct:
        color = "#145214" if theme == "dark" else "#d4edda"
    else:
        color = "#6b0000" if theme == "dark" else "#f8d7da"
    st.markdown(
        f"<div style='background-color:{color};padding:0.9em;border-radius:10px;margin-bottom:10px'>{message}</div>",
        unsafe_allow_html=True,
    )


def reset_quiz():
    """Retour au menu."""
    for k, v in _initial_state.items():
        st.session_state[k] = v


def generate_questions(selected_depth, selected_pos):
    """Génère la liste de questions."""
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
        return []

    sampled = (
        random.choices(possible_questions, k=QUIZ_LENGTH)
        if len(possible_questions) < QUIZ_LENGTH
        else random.sample(possible_questions, k=QUIZ_LENGTH)
    )

    is_mixed = selected_depth == ANY or selected_pos == ANY
    for q in sampled:
        q["type"] = (
            random.choice(["guess_action", "guess_context", "hand_included"])
            if is_mixed
            else "guess_action"
        )
    return sampled


# ======================================================================
# ÉCRANS
# ======================================================================
def show_setup_screen():
    st.subheader("Configurez votre série de questions")
    depth_list = [ANY] + sorted(ALL_RANGES.keys())
    selected_depth = st.selectbox("Profondeur (stack) :", depth_list)

    all_pos = sorted(list(set(p for d in ALL_RANGES.values() for p in d.keys())))
    pos_list = [ANY] + all_pos
    selected_pos = st.selectbox("Position :", pos_list)

    if st.button(
        f"🚀 Commencer une série de {QUIZ_LENGTH} questions",
        use_container_width=True,
        type="primary",
    ):
        qs = generate_questions(selected_depth, selected_pos)
        if not qs:
            st.error("Aucune range ne correspond à vos filtres.")
        else:
            st.session_state.quiz_started = True
            st.session_state.question_list = qs
            st.session_state.current_question_index = 0
            st.session_state.user_score = 0
            st.session_state.responses = []
            st.session_state.streak = 0
            st.session_state.question_start = time.time()
            st.rerun()


def show_quiz_screen():
    i = st.session_state.current_question_index
    qlist = st.session_state.question_list
    total = len(qlist)
    question = qlist[i]
    score = st.session_state.user_score
    streak = st.session_state.streak
    image_path = (
        BASE_DIR / question["depth"] / question["pos"] / f"{question['action']}.png"
    )

    st.progress(i / total, text=f"Question {i+1}/{total} | Score: {score}")
    if st.session_state.last_answer_feedback:
        feedback_box(
            st.session_state.last_answer_feedback, st.session_state.last_answer_correct
        )

    col_img, col_form = st.columns([2, 1])
    with col_img:
        try:
            st.image(str(image_path), use_container_width=False)
        except Exception:
            st.caption("Image introuvable.")

    st.caption(f"🔥 Streak : {streak}")

    with col_form:
        if question["type"] == "guess_action":
            st.caption(f"Situation: {question['depth']} - {question['pos']}")
            with st.form(key=f"form_{i}"):
                st.subheader("Quelle est l'action ?")
                possible_actions = sorted(
                    ALL_RANGES[question["depth"]][question["pos"]]
                )
                guess = st.selectbox("Votre réponse :", options=possible_actions)
                if st.form_submit_button("✔️ Valider", use_container_width=True):
                    update_quiz_state(guess == question["action"], question, guess)
        elif question["type"] == "guess_context":
            st.caption(f"Action: {question['action']} - {question['pos']}")
            with st.form(key=f"form_{i}"):
                st.subheader("Quelle est la situation ?")
                guess_depth = st.selectbox(
                    "Profondeur :", options=sorted(ALL_RANGES.keys())
                )
                if st.form_submit_button("✔️ Valider", use_container_width=True):
                    update_quiz_state(
                        guess_depth == question["depth"], question, guess_depth
                    )
        else:
            st.caption(f"Profondeur: {question['depth']} - Position: {question['pos']}")
            with st.form(key=f"form_{i}"):
                st.subheader("Cette main est-elle dans la range ?")
                guess = st.radio("Votre réponse :", ["Oui", "Non"], horizontal=True)
                if st.form_submit_button("✔️ Valider", use_container_width=True):
                    correct = random.choice(
                        [True, False]
                    )  # à remplacer par ta logique réelle
                    update_quiz_state(correct, question, guess)

    if st.button("↩️ Abandonner et retourner au menu"):
        reset_quiz()
        st.rerun()


def update_quiz_state(correct, question, guess):
    if correct:
        st.session_state.user_score += 1
        st.session_state.streak += 1
        fb = f"✅ Correct ! ({question['action']})"
    else:
        st.session_state.streak = 0
        fb = f"❌ Incorrect. Réponse correcte : {question['action']}."
    st.session_state.last_answer_feedback = fb
    st.session_state.last_answer_correct = correct
    st.session_state.responses.append(
        {"question": question, "user_guess": str(guess), "correct": correct}
    )
    st.session_state.current_question_index += 1
    st.session_state.question_start = time.time()
    st.rerun()


def show_result_screen():
    total = len(st.session_state.question_list)
    score = st.session_state.user_score
    pct = (score / total) * 100 if total else 0

    st.balloons()
    st.title("🎉 Quiz Terminé !")
    st.metric("Score final", f"{score}/{total}", delta=f"{pct:.1f}%")

    # Résumé
    data = [
        {
            "N°": i + 1,
            "Profondeur": r["question"]["depth"],
            "Position": r["question"]["pos"],
            "Action correcte": r["question"]["action"],
            "Votre réponse": r["user_guess"],
            "Résultat": "✅" if r["correct"] else "❌",
        }
        for i, r in enumerate(st.session_state.responses)
    ]
    df = pd.DataFrame(data)
    st.dataframe(df)

    # Historique persisté
    st.session_state.quiz_history.append(
        {"date": datetime.today(), "score": round(pct, 2)}
    )
    save_history(st.session_state.quiz_history)
    hist_df = pd.DataFrame(st.session_state.quiz_history)
    st.line_chart(hist_df.set_index("date")["score"], use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔁 Rejouer erreurs", use_container_width=True):
            wrong_q = [
                r["question"] for r in st.session_state.responses if not r["correct"]
            ]
            if not wrong_q:
                st.info("Aucune erreur à rejouer 🎯")
            else:
                st.session_state.question_list = wrong_q
                st.session_state.current_question_index = 0
                st.session_state.user_score = 0
                st.session_state.responses = []
                st.session_state.streak = 0
                st.session_state.question_start = time.time()
                st.rerun()
    with col2:
        if st.button("🏠 Retour au menu", use_container_width=True, type="primary"):
            reset_quiz()
            st.rerun()
    with col3:
        if st.button("💾 Exporter l’historique (.csv)", use_container_width=True):
            csv_path = Path(BASE_DIR) / "quiz_history.csv"
            hist_df.to_csv(csv_path, index=False)
            st.success(f"Historique exporté vers : {csv_path}")


# ======================================================================
# ROUTAGE
# ======================================================================
if not st.session_state.quiz_started:
    show_setup_screen()
elif st.session_state.current_question_index < len(st.session_state.question_list):
    show_quiz_screen()
else:
    show_result_screen()
