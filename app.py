import json
import time
import tempfile
import os
import streamlit as st
import google.generativeai as genai

TEXT_EXTS = {"txt", "eml", "md"}
BINARY_EXTS = {"pdf", "png", "jpg", "jpeg"}

# ── Page setup ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Relay — Agent Trace Summarizer",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme / CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #0B1220;
    --panel: #131B2E;
    --panel-raised: #182238;
    --line: #26324A;
    --text: #E8ECF3;
    --text-dim: #8C97AF;
    --amber: #E8A33D;
    --teal: #4FD1C5;
    --red: #F2555A;
}

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

.stApp { background: var(--ink); }

/* Hide default streamlit chrome for a cleaner product feel */
#MainMenu, footer, header { visibility: hidden; }

/* Header block */
.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--amber);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}
.eyebrow .dot {
    width: 6px; height: 6px;
    background: var(--amber);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--amber);
    display: inline-block;
}
.hero-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 38px;
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.01em;
    margin: 0 0 12px 0;
    color: var(--text);
}
.hero-title span { color: var(--text-dim); font-weight: 500; }
.hero-sub {
    color: var(--text-dim);
    font-size: 15px;
    line-height: 1.6;
    max-width: 640px;
    margin-bottom: 8px;
}

/* Panel label */
.panel-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 4px;
    display: block;
}

/* Containers with border act as our "panels" */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--panel);
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background: var(--panel-raised) !important;
    border: 1px solid var(--line) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 1px var(--amber) !important;
}
label { color: var(--text-dim) !important; font-size: 12.5px !important; font-weight: 500 !important; }

/* Radio pills (source type) */
div[role="radiogroup"] { gap: 6px; }
div[role="radiogroup"] label {
    background: var(--panel-raised);
    border: 1px solid var(--line);
    border-radius: 7px;
    padding: 6px 14px !important;
}

/* Buttons */
.stButton > button {
    background: var(--amber) !important;
    color: #1A1305 !important;
    border: none !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    width: 100%;
    transition: box-shadow 0.15s;
}
.stButton > button:hover { box-shadow: 0 0 0 3px rgba(232,163,61,0.25) !important; color: #1A1305 !important; }

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background: var(--panel-raised) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 6px !important;
}

/* Status widget (agent trace) */
[data-testid="stStatusWidget"], div[data-testid="stExpander"] {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Output cards */
.summary-card {
    font-size: 14.5px;
    line-height: 1.7;
    color: var(--text);
}
.action-item {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 14px;
    align-items: start;
    background: var(--panel-raised);
    border: 1px solid var(--line);
    border-left: 3px solid var(--amber);
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.action-item .task { font-size: 13.5px; line-height: 1.5; color: var(--text); }
.action-item .meta { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-dim); white-space: nowrap; text-align: right; }
.action-item .owner { color: var(--teal); font-weight: 600; }
.badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 3px 9px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
    height: fit-content;
}
.badge.high { background: rgba(242,85,90,0.15); color: #FF8B8F; }
.badge.medium { background: rgba(232,163,61,0.15); color: var(--amber); }
.badge.low { background: rgba(79,209,197,0.15); color: var(--teal); }

.decision-row {
    font-size: 13.5px;
    line-height: 1.6;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    color: var(--text);
}
.decision-row:last-child { border-bottom: none; }
.decision-row::before { content: '— '; color: var(--text-dim); }

.empty-note { color: var(--text-dim); font-size: 13px; font-style: italic; }

.footnote {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    color: #4A5670;
    line-height: 1.7;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="eyebrow"><span class="dot"></span>Agent online</div>
<div class="hero-title">Relay <span>— thread &amp; transcript triage agent</span></div>
<div class="hero-sub">Drop in an email thread or a meeting transcript. The agent parses it, pulls out who owns what,
and hands back a clean summary — no more re-reading a 40-message thread to find the one commitment that mattered.</div>
""", unsafe_allow_html=True)

st.write("")

# ── Config panel ─────────────────────────────────────────────────────────
with st.container(border=True):
    st.markdown('<span class="panel-label">01 — Configure</span>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        api_key = st.text_input("Gemini API key", type="password", placeholder="AIza...",
                                 help="Used only for this session's requests — never stored or logged.")
    with c2:
        model_name = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"])
    st.caption("Your key stays in this browser session. It's sent straight to Google's API and nowhere else.")

st.write("")

# ── Source panel ─────────────────────────────────────────────────────────
with st.container(border=True):
    st.markdown('<span class="panel-label">02 — Source</span>', unsafe_allow_html=True)
    source_type = st.radio("Source type", ["Email thread", "Meeting transcript"],
                            horizontal=True, label_visibility="collapsed")

    placeholder = ("Paste the full email thread here — include sender names and timestamps if you have them. "
                    "The agent reads the whole thing, not just the latest reply.") if source_type == "Email thread" \
        else "Paste the meeting transcript here — speaker labels help, but plain text works too."

    pasted_text = st.text_area("Content", height=240, placeholder=placeholder, label_visibility="collapsed")

    uploaded = st.file_uploader(
        "or drop in a file — .txt, .eml, .md, .pdf, or a screenshot (.png / .jpg)",
        type=["txt", "eml", "md", "pdf", "png", "jpg", "jpeg"],
    )

    uploaded_gemini_file = None  # holds a Gemini-hosted file handle for PDFs/screenshots

    if uploaded is not None:
        ext = uploaded.name.rsplit(".", 1)[-1].lower()
        if ext in TEXT_EXTS:
            pasted_text = uploaded.read().decode("utf-8", errors="ignore")
            st.caption(f"Loaded text from **{uploaded.name}**.")
        elif ext in BINARY_EXTS:
            st.caption(f"**{uploaded.name}** will be read directly by Gemini (PDF/image understanding) — no paste needed.")
            # stash the raw bytes + suffix; actual upload to Gemini happens on Run,
            # since it needs the configured API key first
            st.session_state["_pending_upload"] = {
                "bytes": uploaded.getvalue(),
                "suffix": f".{ext}",
                "mime": {
                    "pdf": "application/pdf",
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                }[ext],
                "name": uploaded.name,
            }
    else:
        st.session_state.pop("_pending_upload", None)

    run_clicked = st.button("Run agent")

st.write("")

# ── Prompt builder ───────────────────────────────────────────────────────
def build_prompt(kind: str, text: str = None, has_attachment: bool = False) -> str:
    label = "email thread" if kind == "Email thread" else "meeting transcript"
    instructions = f"""You are an operations agent that reads {label}s and extracts what matters.

Read the {"attached file (it may be a PDF document or a screenshot — read any visible text and layout) containing the " + label if has_attachment else "following " + label} and respond with ONLY a JSON object (no markdown fences, no preamble) matching this exact shape:

{{
  "summary": "a tight 3-5 sentence summary of what was discussed and decided",
  "action_items": [
    {{ "task": "specific task description", "owner": "person responsible, or 'Unassigned' if unclear", "due_date": "date or timeframe if mentioned, else 'Not specified'", "priority": "high" | "medium" | "low" }}
  ],
  "key_decisions": ["decision 1", "decision 2"]
}}

If there are no clear action items or decisions, return empty arrays for those fields — do not invent content that isn't in the source."""

    if has_attachment:
        return instructions
    return f"""{instructions}

SOURCE:
\"\"\"
{text}
\"\"\""""

STAGES = {
    "Email thread": [
        "Ingesting thread",
        "Resolving participants",
        "Tracing reply chain",
        "Extracting commitments",
        "Structuring output",
    ],
    "Meeting transcript": [
        "Ingesting transcript",
        "Identifying speakers",
        "Segmenting discussion",
        "Extracting commitments",
        "Structuring output",
    ],
}

# ── Run ──────────────────────────────────────────────────────────────────
pending_upload = st.session_state.get("_pending_upload")
has_text = bool(pasted_text and pasted_text.strip())
has_attachment = pending_upload is not None

if run_clicked:
    if not api_key:
        st.error("Add your Gemini API key first.")
    elif not has_text and not has_attachment:
        st.error("Paste an email thread or transcript, or upload a file, first.")
    else:
        stages = STAGES[source_type]
        if has_attachment:
            stages = [f"Reading {pending_upload['name']}"] + stages[1:]

        result = None
        error_msg = None

        with st.status("Running agent…", expanded=True) as status:
            for stage in stages[:-1]:
                st.write(f"◆ {stage}")
                time.sleep(0.35)
            st.write(f"◆ {stages[-1]}")

            tmp_path = None
            try:
                genai.configure(api_key=api_key)
                gmodel = genai.GenerativeModel(model_name)

                if has_attachment:
                    # write to a temp file so genai can upload it
                    with tempfile.NamedTemporaryFile(delete=False, suffix=pending_upload["suffix"]) as tmp:
                        tmp.write(pending_upload["bytes"])
                        tmp_path = tmp.name
                    gemini_file = genai.upload_file(tmp_path, mime_type=pending_upload["mime"])
                    contents = [gemini_file, build_prompt(source_type, has_attachment=True)]
                else:
                    contents = build_prompt(source_type, text=pasted_text)

                response = gmodel.generate_content(
                    contents,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.2},
                )
                raw = response.text.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)
                status.update(label="Agent finished", state="complete", expanded=False)
            except Exception as e:
                error_msg = str(e)
                status.update(label="Agent failed", state="error", expanded=True)
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)

        if error_msg:
            st.error(f"Something went wrong: {error_msg}")
        elif result:
            with st.container(border=True):
                st.markdown('<span class="panel-label">Summary</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary-card">{result.get("summary", "No summary returned.")}</div>',
                            unsafe_allow_html=True)

            st.write("")
            with st.container(border=True):
                st.markdown('<span class="panel-label">Action items</span>', unsafe_allow_html=True)
                items = result.get("action_items", [])
                if items:
                    for it in items:
                        priority = (it.get("priority") or "medium").lower()
                        st.markdown(f"""
                        <div class="action-item">
                            <div class="task">{it.get('task', '')}</div>
                            <div class="meta"><span class="owner">{it.get('owner', 'Unassigned')}</span><br>{it.get('due_date', 'Not specified')}</div>
                            <div class="badge {priority}">{priority}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-note">No action items detected.</div>', unsafe_allow_html=True)

            st.write("")
            with st.container(border=True):
                st.markdown('<span class="panel-label">Key decisions</span>', unsafe_allow_html=True)
                decisions = result.get("key_decisions", [])
                if decisions:
                    for d in decisions:
                        st.markdown(f'<div class="decision-row">{d}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-note">No explicit decisions detected.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footnote">
Relay v0.1 · calls the Gemini API directly from this app<br>
Want live Gmail / Calendar ingestion instead of paste? That needs a Google OAuth client ID registered on your own
Google Cloud project — wire it in whenever you're ready.
</div>
""", unsafe_allow_html=True)
