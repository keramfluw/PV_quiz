
import streamlit as st
import pandas as pd
import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

APP_TITLE = "Qrauts AG PV-Basiswissen – Online-Test"
LOGO_PATH = "assets/logo.png"
QUESTIONS_FILE = "questions.json"

st.set_page_config(page_title=APP_TITLE, layout="wide")

def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def init_state():
    if "mode" not in st.session_state:
        st.session_state.mode = None  # "exam" or "learn"
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "answers" not in st.session_state:
        st.session_state.answers = {}  # qid -> choice index
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "end_time" not in st.session_state:
        st.session_state.end_time = None
    if "duration_min" not in st.session_state:
        st.session_state.duration_min = 60
    if "current_idx" not in st.session_state:
        st.session_state.current_idx = 0
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "seed" not in st.session_state:
        st.session_state.seed = random.randint(1, 10_000)

def header():
    cols = st.columns([1,6,2])
    with cols[0]:
        st.image(LOGO_PATH, use_column_width=True)
    with cols[1]:
        st.title(APP_TITLE)
        st.caption("Sachkunde: Photovoltaikanlagen – Multiple-Choice basierend auf Seminarunterlagen")
    with cols[2]:
        st.write("")
        st.write("")
        st.link_button("📤 Export Antworten (CSV)", "#export")

def choose_mode():
    st.subheader("Modus wählen")
    st.write("- **Prüfungsmodus**: Timer, Lösungen erst nach Abgabe sichtbar.")
    st.write("- **Lernmodus**: Sofortiges Feedback nach jeder Antwort.")
    mode = st.radio("Modus", ["Prüfungsmodus", "Lernmodus"], index=0, horizontal=True)
    st.session_state.mode = "exam" if mode == "Prüfungsmodus" else "learn"

def configure_quiz(all_questions):
    with st.expander("🛠️ Einstellungen", expanded=True):
        n_default = min(30, len(all_questions))
        n_questions = st.slider("Anzahl Fragen", 5, len(all_questions), n_default, 1)
        duration = st.number_input("Dauer (Minuten, nur Prüfungsmodus)", min_value=5, max_value=180, value=60, step=5)
        topics = sorted(set(q["topic"] for q in all_questions))
        chosen_topics = st.multiselect("Themen (optional filtern)", topics, default=topics)
        difficulty = st.multiselect("Schwierigkeitsgrad", [1,2,3], default=[1,2,3], help="1=leicht, 3=schwer")
        shuffle = st.checkbox("Fragenreihenfolge mischen", value=True)

        filtered = [q for q in all_questions if q["topic"] in chosen_topics and q.get("difficulty",1) in difficulty]
        if shuffle:
            rnd = random.Random(st.session_state.seed)
            rnd.shuffle(filtered)
        selected = filtered[:n_questions]
        return selected, duration

def start_quiz(selected, duration):
    st.session_state.questions = selected
    st.session_state.answers = {}
    st.session_state.current_idx = 0
    st.session_state.submitted = False
    st.session_state.duration_min = duration
    if st.session_state.mode == "exam":
        st.session_state.start_time = datetime.utcnow()
        st.session_state.end_time = st.session_state.start_time + timedelta(minutes=duration)
    else:
        st.session_state.start_time = datetime.utcnow()
        st.session_state.end_time = None

def timer():
    if st.session_state.mode != "exam" or st.session_state.submitted:
        return
    now = datetime.utcnow()
    remaining = (st.session_state.end_time - now).total_seconds()
    if remaining <= 0:
        st.warning("⏰ Zeit abgelaufen – Test wird abgegeben.")
        st.session_state.submitted = True
        st.rerun()
    else:
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        st.markdown(f"**Verbleibende Zeit:** {mins:02d}:{secs:02d}")

def render_question(q, idx):
    st.subheader(f"Frage {idx+1} von {len(st.session_state.questions)}")
    st.write(q["question"])
    choice = st.session_state.answers.get(q["id"])
    choice = st.radio(
        "Antwort wählen",
        options=list(range(len(q["choices"]))),
        format_func=lambda i: q["choices"][i],
        index=choice if choice is not None else -1,
        key=f"radio_{q['id']}",
        label_visibility="collapsed"
    )
    st.session_state.answers[q["id"]] = choice

    if st.session_state.mode == "learn":
        if choice is not None:
            correct = q["answer_index"]
            if choice == correct:
                st.success("✅ Richtig")
            else:
                st.error(f"❌ Falsch – richtig ist **{q['choices'][correct]}**")
            if q.get("explanation"):
                st.info(q["explanation"])

def nav_controls():
    cols = st.columns(3)
    with cols[0]:
        if st.button("⟵ Zurück", disabled=st.session_state.current_idx == 0):
            st.session_state.current_idx -= 1
            st.rerun()
    with cols[1]:
        st.write("")
    with cols[2]:
        if st.session_state.current_idx < len(st.session_state.questions)-1:
            if st.button("Weiter ⟶"):
                st.session_state.current_idx += 1
                st.rerun()
        else:
            if st.session_state.mode == "exam":
                if st.button("🧾 Abgeben"):
                    st.session_state.submitted = True
                    st.rerun()

def evaluate():
    qs = st.session_state.questions
    ans = st.session_state.answers
    total = len(qs)
    correct = 0
    rows = []
    for q in qs:
        given = ans.get(q["id"])
        is_correct = given == q["answer_index"]
        correct += 1 if is_correct else 0
        rows.append({
            "id": q["id"],
            "topic": q["topic"],
            "difficulty": q.get("difficulty",1),
            "question": q["question"],
            "given": q["choices"][given] if given is not None else "",
            "correct": q["choices"][q["answer_index"]],
            "is_correct": is_correct
        })
    percent = round(100 * correct / total, 1) if total else 0.0
    df = pd.DataFrame(rows)
    return correct, total, percent, df

def export_csv(df):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("CSV herunterladen", csv, file_name="pv_quiz_results.csv", mime="text/csv")

def review(df, qs):
    st.subheader("Review")
    for _, row in df.iterrows():
        q = next(q for q in qs if q["id"] == row["id"])
        st.markdown(f"**{row['question']}**")
        st.write(f"Deine Antwort: {row['given'] or '—'}")
        st.write(f"Richtig: {row['correct']}")
        if q.get("explanation"):
            st.info(q["explanation"])
        st.divider()

def main():
    init_state()
    header()

    all_questions = load_questions()

    if st.session_state.mode is None:
        choose_mode()

    selected, duration = configure_quiz(all_questions)

    if st.button("▶️ Test starten"):
        start_quiz(selected, duration)
        st.rerun()

    if st.session_state.questions and not st.session_state.submitted:
        with st.sidebar:
            st.markdown("### Navigation")
            timer()
            st.progress((st.session_state.current_idx+1)/len(st.session_state.questions))
            answered = sum(1 for q in st.session_state.questions if q["id"] in st.session_state.answers)
            st.caption(f"Beantwortet: {answered}/{len(st.session_state.questions)}")
        q = st.session_state.questions[st.session_state.current_idx]
        render_question(q, st.session_state.current_idx)
        nav_controls()

    if st.session_state.submitted and st.session_state.questions:
        correct, total, percent, df = evaluate()
        st.success(f"Ergebnis: {correct}/{total} richtig ({percent} %) – Zeit: {st.session_state.duration_min} min (geplant)")
        export_csv(df)
        review(df, st.session_state.questions)

    st.markdown("<a name='export'></a>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
