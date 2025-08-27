# PV-Basiswissen Online-Test (Streamlit)

Dieser Online-Test bildet zentrale Inhalte aus *PV-Basiswissen (Sachkunde)* als Multiple-Choice-Quiz ab.
Er ist als eigenständige Streamlit-App implementiert und kann lokal oder auf einer Platform wie Streamlit Community Cloud betrieben werden.

## Funktionen
- Prüfungsmodus (Timer, keine sofortigen Lösungen) und Lernmodus (sofortiges Feedback)
- Zufällige Auswahl und Reihenfolge der Fragen
- Ergebnis-Auswertung mit Punktzahl, Prozent, Zeitstempel
- Review-Seite mit richtigen Antworten und Erklärungen
- Export der Antworten als CSV
- Branding (Logo unter `assets/logo.png`)

## Installation (lokal)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment
- **Streamlit Cloud**: Repo hochladen, als App starten, `app.py` auswählen.
- **Docker** (optional):
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Fragen editieren
Die Fragen liegen in `questions.json`. Struktur pro Eintrag:
```json
{
  "id": "A1-001",
  "question": "Beispielfrage?",
  "choices": ["A", "B", "C", "D"],
  "answer_index": 1,
  "explanation": "Kurzbegründung…",
  "topic": "Grundlagen",
  "difficulty": 1
}
```
- `answer_index` ist der Index (0-basiert) der richtigen Antwort.
- `difficulty`: 1 (leicht) bis 3 (schwer).

## Haftung
Die Inhalte sind als Lern- und Prüfungsunterstützung gedacht. Technische, rechtliche und steuerliche Auskünfte sind ohne Gewähr.
