from __future__ import annotations

import gradio as gr

print("Importing Chat Engine...")
from src.pipeline.chat_engine import ChatEngine

print("Initializing Chat Engine...")
engine = ChatEngine()

# -----------------------
# Prompt suggestions
# -----------------------
PROMPT_SUGGESTIONS = [
    "I feel anxious and can't sleep.",
    "I am sad all the time and need support.",
    "How can I calm down during a panic attack?",
    "I need help understanding my feelings.",
]

# -----------------------
# MODERN UI CSS
# -----------------------
CUSTOM_CSS = """
.gradio-container {
    background: radial-gradient(circle at top, #0f172a, #070b14) !important;
    font-family: ui-sans-serif, system-ui;
    color: #eaf0ff !important;
    display: flex;
    justify-content: center;
}

.main {
    max-width: 900px !important;
}

/* HERO */
.hero {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 12px;
}

.hero h1 {
    margin: 0;
    font-size: 1.6rem;
}

.hero p {
    margin-top: 6px;
    color: rgba(234,240,255,0.65);
}

/* CHAT BOX */
.chatbot {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 12px;
    height: 520px;
    overflow: auto;
}

/* USER MESSAGE */
.message.user {
    background: linear-gradient(135deg, rgba(110,231,255,0.18), rgba(110,231,255,0.08)) !important;
    border: 1px solid rgba(110,231,255,0.25) !important;
    color: #eaf0ff !important;
    border-radius: 16px !important;
    padding: 10px 14px !important;
    margin-left: auto !important;
    max-width: 75% !important;
}

/* BOT MESSAGE */
.message.bot {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: #eaf0ff !important;
    border-radius: 16px !important;
    padding: 10px 14px !important;
    margin-right: auto !important;
    max-width: 75% !important;
}

/* MESSAGE SPACING */
.message {
    margin: 8px 0 !important;
    line-height: 1.5 !important;
}

/* INPUT */
textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 14px !important;
    color: #eaf0ff !important;
}

/* BUTTONS */
button {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #eaf0ff !important;
    transition: 0.2s ease;
}

button:hover {
    transform: translateY(-1px);
    border-color: rgba(110,231,255,0.35) !important;
}
"""

# -----------------------
# HEADER
# -----------------------
HEADER_HTML = """
<div class="hero">
    <h1>MindBridge Chat</h1>
    <p>Emotion-aware AI assistant with language detection, intent routing, RAG, and emotion analysis.</p>
</div>
"""

# -----------------------
# INITIAL HISTORY
# -----------------------
INITIAL_HISTORY = [
    {
        "role": "assistant",
        "content": "Hello 👋 I’m ready to help you with support, understanding, and guidance.",
    }
]

# -----------------------
# CHAT LOGIC
# -----------------------
def process_message(user_prompt, history, top_k):
    if not user_prompt.strip():
        return "", history, "n/a", "n/a", "0", "not needed", "n/a", ""

    history.append({"role": "user", "content": user_prompt})

    try:
        result = engine.process_message(user_prompt, top_k=int(top_k))

        assistant_response = result["assistant_response"]
        history.append({"role": "assistant", "content": assistant_response})

        lang = result.get("detected_language", "n/a")
        intent = result.get("intent", "n/a")
        emotion = result.get("emotion", "n/a")
        rag_hits = str(len(result.get("results") or []))
        translation = "enabled" if lang != "en" else "not needed"

        debug = f"""
**Detected language:** {lang}

**Intent:** {intent}

**Emotion:** {emotion}

**Translated prompt:** {result.get('translated_prompt', 'n/a')}
"""

        results = result.get("results") or []
        if results:
            debug += "\n### Retrieved Context:\n"
            for i, item in enumerate(results, 1):
                payload = getattr(item, "payload", {}) or {}
                debug += f"""
**Result {i}**
- Chunk: {payload.get('chunk', 'N/A')}
- Context: {payload.get('context', 'N/A')}
- Response: {payload.get('response', 'N/A')}
"""

    except Exception as e:
        history.append({"role": "assistant", "content": f"Error: {e}"})
        return "", history, "error", "error", "0", "error", "error", str(e)

    return "", history, lang, intent, rag_hits, translation, emotion, debug


# -----------------------
# UI
# -----------------------
with gr.Blocks(title="MindBridge Chat") as demo:

    conversation_state = gr.State(INITIAL_HISTORY.copy())

    with gr.Sidebar():
        gr.Markdown("## Controls")

        top_k = gr.Slider(1, 5, value=3, step=1, label="RAG Top-K")

        gr.Markdown("### Quick prompts")
        prompt_buttons = [gr.Button(p, variant="secondary") for p in PROMPT_SUGGESTIONS]

    HEADER_HTML

    chatbot = gr.Chatbot(label="Conversation", height=520)

    chat_input = gr.Textbox(
        placeholder="Type your message...",
        show_label=False,
    )

    # -----------------------
    # METRICS ROW (NOW WITH EMOTION)
    # -----------------------
    with gr.Row():
        metric_lang = gr.Textbox(label="Language", interactive=False)
        metric_intent = gr.Textbox(label="Intent", interactive=False)
        metric_rag = gr.Textbox(label="RAG Hits", interactive=False)
        metric_trans = gr.Textbox(label="Translation", interactive=False)
        metric_emotion = gr.Textbox(label="Emotion", interactive=False)

    debug = gr.Markdown()

    outputs = [
        chat_input,
        chatbot,
        metric_lang,
        metric_intent,
        metric_rag,
        metric_trans,
        metric_emotion,
        debug,
    ]

    chat_input.submit(
        process_message,
        inputs=[chat_input, conversation_state, top_k],
        outputs=outputs,
    )

    for btn in prompt_buttons:
        btn.click(
            process_message,
            inputs=[btn, conversation_state, top_k],
            outputs=outputs,
        )

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    demo.launch(css=CUSTOM_CSS)