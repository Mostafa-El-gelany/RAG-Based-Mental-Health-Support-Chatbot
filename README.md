# MindBridge Chat

A simple Streamlit chatbot that wraps the project workflow:

- detects the input language
- translates to English when needed
- classifies intent
- runs retrieval for mental-health questions
- generates an answer and translates it back if needed

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

You can also start it with:

```bash
python main.py
```

## Required environment variables

- `LLM_API_KEY`
- `QDRANT_CLUSTER_ENDPOINT`
- `QDRANT_API_KEY`

## Notes

- The language detector expects the model file at `src/Language_Detection/models/language_detector.pkl`.
- The app keeps the chatbot state in memory for the current session.
