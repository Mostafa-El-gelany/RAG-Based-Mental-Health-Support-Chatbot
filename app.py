from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import streamlit as st

from src.pipeline.chat_engine import ChatEngine


st.set_page_config(
    page_title="MindBridge Chat",
    page_icon="🫶",
    layout="wide",
    initial_sidebar_state="expanded",
)


PROMPT_SUGGESTIONS = [
    "I feel anxious and can't sleep.",
    "I am sad all the time and need support.",
    "How can I calm down during a panic attack?",
    "I need help understanding my feelings.",
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #07111f;
            --bg-2: #0c1a31;
            --bg-3: #eef3fb;
            --card: rgba(13, 22, 41, 0.66);
            --card-light: rgba(255, 255, 255, 0.76);
            --stroke: rgba(255, 255, 255, 0.12);
            --text: #eaf1ff;
            --muted: rgba(234, 241, 255, 0.72);
            --accent: #7cd4ff;
            --accent-2: #8df0c9;
            --accent-3: #a7b7ff;
            --shadow: 0 24px 80px rgba(0, 0, 0, 0.28);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 12%, rgba(125, 212, 255, 0.20), transparent 18%),
                radial-gradient(circle at 90% 6%, rgba(141, 240, 201, 0.18), transparent 16%),
                radial-gradient(circle at 80% 80%, rgba(167, 183, 255, 0.18), transparent 22%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 44%, var(--bg-3) 44%, #f5f7fc 100%);
            color: var(--text);
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 44px 44px;
            mask-image: linear-gradient(to bottom, rgba(0,0,0,0.45), transparent 95%);
            opacity: 0.3;
            z-index: 0;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(14px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes softFloat {
            0%, 100% {
                transform: translate3d(0, 0, 0);
            }
            50% {
                transform: translate3d(0, -10px, 0);
            }
        }

        @keyframes glowPulse {
            0%, 100% {
                opacity: 0.55;
                transform: scale(1);
            }
            50% {
                opacity: 0.9;
                transform: scale(1.06);
            }
        }

        @keyframes borderDrift {
            0% {
                box-shadow: 0 0 0 rgba(124, 212, 255, 0.0), 0 0 0 rgba(141, 240, 201, 0.0);
            }
            50% {
                box-shadow: 0 0 24px rgba(124, 212, 255, 0.10), 0 0 36px rgba(141, 240, 201, 0.08);
            }
            100% {
                box-shadow: 0 0 0 rgba(124, 212, 255, 0.0), 0 0 0 rgba(141, 240, 201, 0.0);
            }
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #091224 0%, #102140 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] *,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] div {
            color: #f4f8ff !important;
        }

        .main-shell {
            position: relative;
            z-index: 1;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border-radius: 32px;
            padding: 1.6rem 1.7rem;
            background: linear-gradient(145deg, rgba(9, 17, 33, 0.88), rgba(18, 31, 58, 0.76));
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: var(--shadow);
            margin: 0.35rem 0 1rem;
            animation: fadeInUp 0.7s ease-out both;
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: -120px auto auto -120px;
            width: 280px;
            height: 280px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(124, 212, 255, 0.22), transparent 68%);
            filter: blur(8px);
            animation: glowPulse 9s ease-in-out infinite;
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 0.85rem;
        }

        .brand-mark {
            width: 52px;
            height: 52px;
            border-radius: 18px;
            display: grid;
            place-items: center;
            font-size: 1.4rem;
            background: linear-gradient(135deg, rgba(124,212,255,0.25), rgba(141,240,201,0.20));
            border: 1px solid rgba(255,255,255,0.14);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
            animation: softFloat 8s ease-in-out infinite;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2.2rem, 5vw, 3.8rem);
            line-height: 0.98;
            letter-spacing: -0.06em;
            color: #f8fbff;
        }

        .hero p {
            margin: 0.9rem 0 0;
            max-width: 760px;
            font-size: 1.02rem;
            line-height: 1.65;
            color: var(--muted);
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 1.15rem;
        }

        .hero-card,
        .sidebar-card,
        .result-box,
        .status-card {
            border-radius: 22px;
            border: 1px solid rgba(255,255,255,0.11);
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(12px);
        }

        .hero-card {
            animation: fadeInUp 0.7s ease-out both;
        }

        .hero-card:nth-child(1) {
            animation-delay: 0.08s;
        }

        .hero-card:nth-child(2) {
            animation-delay: 0.16s;
        }

        .hero-card:nth-child(3) {
            animation-delay: 0.24s;
        }

        .hero-card {
            padding: 0.95rem 1rem;
            animation: fadeInUp 0.7s ease-out both, borderDrift 12s ease-in-out infinite;
        }

        .hero-card-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: rgba(234, 241, 255, 0.62);
            margin-bottom: 0.35rem;
        }

        .hero-card-value {
            font-size: 1.02rem;
            font-weight: 700;
            color: #f8fbff;
        }

        .hero-card-sub {
            margin-top: 0.28rem;
            font-size: 0.86rem;
            line-height: 1.45;
            color: rgba(234, 241, 255, 0.74);
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.48rem 0.78rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.09);
            border: 1px solid rgba(255,255,255,0.12);
            color: #edf4ff;
            font-size: 0.88rem;
            animation: fadeInUp 0.7s ease-out both;
        }

        .pill:nth-child(1) { animation-delay: 0.1s; }
        .pill:nth-child(2) { animation-delay: 0.18s; }
        .pill:nth-child(3) { animation-delay: 0.26s; }
        .pill:nth-child(4) { animation-delay: 0.34s; }

        .content-wrap {
            display: grid;
            grid-template-columns: 1.5fr 0.75fr;
            gap: 1rem;
            align-items: start;
        }

        .panel {
            border-radius: 30px;
            padding: 1rem;
            background: rgba(255,255,255,0.76);
            border: 1px solid rgba(15, 27, 50, 0.08);
            box-shadow: 0 16px 50px rgba(15, 27, 50, 0.08);
            color: #0f172a;
            animation: fadeInUp 0.55s ease-out both;
        }

        .panel h2,
        .panel h3,
        .panel p,
        .panel label,
        .panel span {
            color: #0f172a;
        }

        .chat-area {
            padding: 0.4rem 0.2rem 0.8rem;
        }

        .bubble {
            padding: 1rem 1.05rem;
            border-radius: 22px;
            margin-bottom: 0.8rem;
            box-shadow: 0 10px 26px rgba(13, 25, 46, 0.08);
            line-height: 1.68;
            white-space: pre-wrap;
            animation: fadeInUp 0.42s ease-out both;
        }

        .bubble-user {
            margin-left: 12%;
            background: linear-gradient(135deg, #0f223f, #18345d);
            color: #f8fbff;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .bubble-assistant {
            margin-right: 12%;
            background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
            color: #0f172a;
            border: 1px solid rgba(15, 27, 50, 0.08);
        }

        .bubble-meta {
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
            margin-bottom: 0.75rem;
        }

        .mini-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.37rem 0.68rem;
            border-radius: 999px;
            font-size: 0.8rem;
            background: rgba(15, 27, 50, 0.06);
            color: #0f172a;
            border: 1px solid rgba(15, 27, 50, 0.08);
        }

        .sidebar-card {
            padding: 0.95rem 1rem;
            margin-bottom: 0.8rem;
            background: rgba(255,255,255,0.07);
        }

        .sidebar-title {
            margin: 0 0 0.3rem;
            font-size: 1.03rem;
            font-weight: 700;
        }

        .sidebar-subtitle {
            margin: 0;
            color: rgba(244, 248, 255, 0.74);
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .status-card {
            padding: 0.9rem 1rem;
            background: rgba(255,255,255,0.08);
            margin-bottom: 0.75rem;
        }

        .status-label {
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            color: rgba(234, 241, 255, 0.65);
            margin-bottom: 0.35rem;
        }

        .status-value {
            font-size: 0.96rem;
            font-weight: 700;
            color: #ffffff;
        }

        .prompt-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.55rem;
            margin-top: 0.5rem;
        }

        .prompt-card button {
            width: 100%;
            border-radius: 16px !important;
            border: 1px solid rgba(124, 212, 255, 0.14) !important;
            background: linear-gradient(135deg, rgba(124, 212, 255, 0.16), rgba(167, 183, 255, 0.12)) !important;
            color: #eef6ff !important;
        }

        .result-box {
            padding: 0.9rem 1rem;
            background: rgba(255,255,255,0.82);
            border: 1px solid rgba(15, 27, 50, 0.09);
            color: #0f172a;
            animation: fadeInUp 0.5s ease-out both;
        }

        [data-testid="stChatMessage"] {
            animation: fadeInUp 0.35s ease-out both;
        }

        [data-testid="stChatMessage"] > div {
            transition: transform 180ms ease, box-shadow 180ms ease;
        }

        [data-testid="stChatMessage"]:hover > div {
            transform: translateY(-1px);
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }

        .footer-note {
            margin-top: 0.9rem;
            font-size: 0.84rem;
            color: rgba(234, 241, 255, 0.66);
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_engine() -> ChatEngine:
    return ChatEngine()


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Welcome. I can listen, detect the language you use, look up supporting context when "
                    "needed, and reply in a calm, supportive style."
                ),
            }
        ]
    if "last_meta" not in st.session_state:
        st.session_state.last_meta = None


def transcript_text() -> str:
    lines = []
    for message in st.session_state.messages:
        role = message.get("role", "assistant").title()
        content = message.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def render_header() -> None:
    st.markdown(
        """
        <div class="hero main-shell">
            <div class="brand-row">
                <div class="brand-mark">🫶</div>
                <div>
                    <div class="pill">MindBridge Chat</div>
                </div>
            </div>
            <h1>Beautiful, calm, and focused support chat.</h1>
            <p>
                This interface wraps your project workflow in a polished conversation experience.
                It detects language, translates when necessary, classifies the question, retrieves
                helpful context, and returns a thoughtful answer.
            </p>
            <div class="pill-row">
                <span class="pill">🌐 Language aware</span>
                <span class="pill">🧭 Intent routing</span>
                <span class="pill">📚 Retrieval grounded</span>
                <span class="pill">✨ Clean conversation UI</span>
            </div>
            <div class="hero-grid">
                <div class="hero-card">
                    <div class="hero-card-label">Input flow</div>
                    <div class="hero-card-value">Message → Detect → Translate → Answer</div>
                    <div class="hero-card-sub">A straightforward path with no extra clutter.</div>
                </div>
                <div class="hero-card">
                    <div class="hero-card-label">Response mode</div>
                    <div class="hero-card-value">Supportive and grounded</div>
                    <div class="hero-card-sub">The assistant stays calm, helpful, and concise.</div>
                </div>
                <div class="hero-card">
                    <div class="hero-card-label">UI style</div>
                    <div class="hero-card-value">Glass, gradients, and soft depth</div>
                    <div class="hero-card-sub">A premium look without making the app harder to use.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> int:
    st.sidebar.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-title">Chat controls</div>
            <p class="sidebar-subtitle">Tune retrieval depth and jump back into the conversation with one click.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_k = st.sidebar.slider("Knowledge results", 1, 5, 3)

    st.sidebar.markdown(
        """
        <div class="status-card">
            <div class="status-label">Current pipeline</div>
            <div class="status-value">Language detection → translation → intent → RAG → response</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Quick prompts")
    selected_prompt = None
    for index, prompt in enumerate(PROMPT_SUGGESTIONS, start=1):
        if st.sidebar.button(prompt, key=f"prompt_{index}", use_container_width=True):
            selected_prompt = prompt

    if st.sidebar.button("Clear conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Conversation cleared. Send a new message whenever you are ready."
                ),
            }
        ]
        st.session_state.last_meta = None
        st.rerun()

    st.sidebar.download_button(
        "Download transcript",
        data=transcript_text(),
        file_name=f"mindbridge-transcript-{datetime.now():%Y%m%d-%H%M%S}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.sidebar.markdown(
        """
        <div class="footer-note">
            Best used as a focused support interface. If you are in immediate danger or feel unsafe,
            contact local emergency services or a trusted person right away.
        </div>
        """,
        unsafe_allow_html=True,
    )

    return top_k, selected_prompt


def render_messages() -> None:
    st.markdown('<div class="panel main-shell chat-area">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        avatar = "🧠" if role == "assistant" else "🙂"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message.get("content", ""))
    st.markdown("</div>", unsafe_allow_html=True)


def render_metadata(meta: dict[str, Any] | None) -> None:
    if not meta:
        return

    st.markdown("### Session insight")
    cols = st.columns(4)
    cols[0].metric("Language", meta.get("detected_language", "n/a"))
    cols[1].metric("Intent", meta.get("intent", "n/a"))
    cols[2].metric("RAG hits", len(meta.get("results") or []))
    cols[3].metric("Translation", "enabled" if meta.get("detected_language") != "en" else "not needed")

    with st.expander("See how this response was built", expanded=False):
        st.write(f"Detected language: {meta.get('detected_language', 'n/a')}")
        st.write(f"Intent: {meta.get('intent', 'n/a')}")
        st.write(f"Translated prompt: {meta.get('translated_prompt', 'n/a')}")
        if meta.get("rewritten_query"):
            st.write(f"Rewritten query: {meta['rewritten_query']}")

        results = meta.get("results") or []
        if results:
            st.subheader("Retrieved context")
            for index, item in enumerate(results, start=1):
                payload = getattr(item, "payload", {}) or {}
                st.markdown(
                    f"""
                    <div class="result-box">
                        <strong>Result {index}</strong><br />
                        <strong>Chunk:</strong> {payload.get('chunk', 'N/A')}<br />
                        <strong>Context:</strong> {payload.get('context', 'N/A')}<br />
                        <strong>Response:</strong> {payload.get('response', 'N/A')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def process_message(user_prompt: str, top_k: int) -> None:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="🙂"):
        st.markdown(user_prompt)

    engine = get_engine()
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking..."):
            try:
                result = engine.process_message(user_prompt, top_k=top_k)
                st.markdown(result["assistant_response"])
                st.session_state.messages.append(
                    {"role": "assistant", "content": result["assistant_response"]}
                )
                st.session_state.last_meta = result
            except Exception as exc:
                error_message = (
                    "I could not complete that request right now because a project dependency or model is unavailable. "
                    f"Details: {exc}"
                )
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
                st.session_state.last_meta = None


def main() -> None:
    inject_styles()
    init_state()
    top_k, selected_prompt = render_sidebar()
    render_header()

    st.markdown('<div class="content-wrap main-shell">', unsafe_allow_html=True)
    render_messages()
    st.markdown("</div>", unsafe_allow_html=True)

    if selected_prompt:
        process_message(selected_prompt, top_k)

    user_prompt = st.chat_input("Ask me anything about mental health support...")
    if user_prompt:
        process_message(user_prompt, top_k)

    render_metadata(st.session_state.last_meta)


if __name__ == "__main__":
    main()
