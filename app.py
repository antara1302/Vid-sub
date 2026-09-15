import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_meeting_data
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="vid-sub",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg: #111313;
    --surface: #191c1b;
    --surface-2: #202422;
    --surface-3: #262b29;
    --border: #343a37;

    --text: #f1f0e9;
    --muted: #a7aaa3;

    --mint: #a8d5ba;
    --peach: #f0b8a4;
    --yellow: #e8d59b;
    --blue: #a9c7d9;
    --pink: #d9b8c8;

    --success: #a8d5ba;

    --radius-lg: 20px;
    --radius-md: 13px;
    --radius-sm: 9px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.04em;
}

/* Main layout */
.block-container {
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 5rem;
}

/* Brand */
.brand {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    letter-spacing: -0.06em;
    color: var(--text);
}

.brand-dot {
    color: var(--mint);
}

/* Hero */
.hero-wrap {
    text-align: center;
    max-width: 820px;
    margin: 4rem auto 3.5rem auto;
}

.hero-title {
    font-family: 'DM Sans', sans-serif;
    font-size: clamp(3rem, 7vw, 5.8rem);
    font-weight: 700;
    line-height: .94;
    letter-spacing: -0.075em;
    color: var(--text);
    margin: 0;
}

.hero-sub {
    margin: 1.2rem auto 0 auto;
    max-width: 570px;
    color: var(--muted);
    font-size: 1rem;
    line-height: 1.6;
}

/* Top navigation */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .2rem 0;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 1.8rem;
}

.nav-link {
    color: var(--muted);
    font-size: .85rem;
}

/* Input workspace */
.workspace {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.7rem;
    box-shadow: 0 20px 55px rgba(0, 0, 0, .22);
}

.workspace-label {
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: .68rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    margin-bottom: .8rem;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stTextInput > div > div > input {
    min-height: 52px !important;
    font-size: .95rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--mint) !important;
    box-shadow: 0 0 0 1px rgba(168, 213, 186, .18) !important;
}

label {
    color: var(--muted) !important;
}

/* Buttons */
.stButton > button {
    min-height: 50px !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--mint) !important;
    background: var(--mint) !important;
    color: #17201b !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    filter: brightness(1.04);
    box-shadow: 0 10px 25px rgba(168, 213, 186, .12) !important;
}

.stButton > button:active {
    transform: scale(.98) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}

.card:hover {
    transform: translateY(-2px);
    border-color: #4a514d;
    box-shadow: 0 12px 35px rgba(0, 0, 0, .16);
}

.card-title {
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .8rem;
}

.card-content {
    font-size: .9rem;
    line-height: 1.75;
    color: var(--text);
}

/* Pastel badges */
.badge {
    display: inline-block;
    padding: .28rem .65rem;
    border-radius: 999px;
    font-size: .65rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.badge-purple {
    background: rgba(168, 213, 186, .12);
    color: var(--mint);
    border: 1px solid rgba(168, 213, 186, .28);
}

.badge-cyan {
    background: rgba(169, 199, 217, .11);
    color: var(--blue);
    border: 1px solid rgba(169, 199, 217, .26);
}

.badge-green {
    background: rgba(232, 213, 155, .11);
    color: var(--yellow);
    border: 1px solid rgba(232, 213, 155, .25);
}

/* Status */
.status-bar {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: .7rem .85rem;
    background: var(--surface-2);
    border-radius: var(--radius-sm);
    margin: .4rem 0;
    border: 1px solid var(--border);
    font-size: .8rem;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active {
    background: var(--peach);
    box-shadow: 0 0 9px rgba(240, 184, 164, .5);
    animation: pulse 1.5s infinite;
}

.dot-done {
    background: var(--mint);
}

.dot-pending {
    background: #4b514d;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: .4; }
}

/* Chat */
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.chat-msg {
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: .25rem;
}

.chat-label {
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.chat-bubble {
    display: inline-block;
    padding: .7rem 1rem;
    border-radius: 11px;
    font-size: .88rem;
    line-height: 1.6;
    max-width: 90%;
}

.user-label {
    color: var(--peach);
}

.bot-label {
    color: var(--mint);
}

.user-bubble {
    background: rgba(240, 184, 164, .10);
    border: 1px solid rgba(240, 184, 164, .22);
    align-self: flex-end;
}

.bot-bubble {
    background: rgba(168, 213, 186, .08);
    border: 1px solid rgba(168, 213, 186, .20);
    align-self: flex-start;
}

/* Transcript */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 1.2rem;
    font-family: 'DM Sans', sans-serif;
    font-size: .86rem;
    line-height: 1.8;
    max-height: 330px;
    overflow-y: auto;
    color: var(--muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* Streamlit progress/spinner */
.stProgress > div > div > div {
    background: var(--mint) !important;
}

.stSpinner > div {
    border-top-color: var(--mint) !important;
}

[data-testid="stMarkdownContainer"] p {
    color: var(--text);
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.6rem 0 !important;
}

/* Mobile */
@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero-wrap {
        margin-top: 2.5rem;
    }

    .hero-title {
        font-size: 3.5rem;
    }

    .nav-links {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"

def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">🎬 vid-sub</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple">Input</span>', unsafe_allow_html=True)
    source = st.text_input("YouTube URL or File Path", placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4")

    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    run_btn = st.button("⚡  Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("summary",    "📋", "Summarisation"),
            ("title",      "🏷️", "Title Generation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-wrap"><div class="hero-title">Meetings,<br>made useful.</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Turn conversations into clear summaries, decisions, action items, and answers you can actually find.</div></div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — see sidebar for live status…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("title", "active")
            title = generate_title(summary)
            update_step("title", "done")

            update_step("extract", "active")
            meeting_data = extract_meeting_data(transcript)
            update_step("extract", "done")

            action_items = meeting_data.get("action_items", [])
            decisions = meeting_data.get("key_decisions", [])
            questions = meeting_data.get("open_questions", [])

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title banner
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # Top row: summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Second row: action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.2rem;font-weight:700;margin-bottom:1rem">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Paste a YouTube URL or local file path, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:2rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)