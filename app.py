import time
import streamlit as st
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
# Palette: soft slate background, muted sage + periwinkle accents, low-glare text.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:          #131a21;
    --bg-2:        #18212a;
    --surface:     rgba(255,255,255,0.025);
    --surface-2:   rgba(255,255,255,0.045);
    --border:      rgba(255,255,255,0.07);
    --border-soft: rgba(143,185,168,0.20);
    --text:        #e4e8ee;
    --text-2:      #a7b0bc;
    --muted:       #6e7987;
    --sage:        #8fb9a8;
    --sage-soft:   rgba(143,185,168,0.12);
    --peri:        #a5abd8;
    --done:        #86b896;
    --done-soft:   rgba(134,184,150,0.10);
    --green:       #4ade80;
    --red:         #e57373;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
}
/* Force light text everywhere so it works regardless of Streamlit's theme */
.stApp, [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] strong {
    color: var(--text);
}
[data-testid="stMarkdownContainer"] a { color: var(--sage); }
[data-testid="stMarkdownContainer"] code {
    background: var(--surface-2);
    color: var(--peri);
}
.stApp {
    background:
        radial-gradient(1100px 520px at 12% -8%, rgba(143,185,168,0.07), transparent 60%),
        radial-gradient(900px 480px at 100% 105%, rgba(165,171,216,0.06), transparent 60%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 3rem 3rem; max-width: 1180px; }

/* ── Hero ── */
.hero { text-align: center; padding: 3rem 0 1.5rem; }
.hero-eyebrow {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--sage);
    background: var(--sage-soft);
    border: 1px solid var(--border-soft);
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    margin-bottom: 1.3rem;
}
.hero h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.6rem, 5.5vw, 4.4rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    color: var(--text);
    margin: 0 0 1rem;
}
.hero h1 span {
    background: linear-gradient(120deg, var(--sage) 10%, var(--peri) 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    display: block;
    font-size: 1.02rem;
    font-weight: 300;
    color: var(--text-2) !important;
    max-width: 560px;
    margin: 0 auto 1.6rem !important;
    text-align: center !important;
    text-wrap: balance;
    line-height: 1.7;
}
.hero, .hero * { text-align: center; }
.hero-pills { justify-content: center !important; }
.hero-pills { display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; }
.hero-pill {
    font-size: 0.78rem;
    color: var(--text-2);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.4rem 0.95rem;
}
.hero-pill b { color: var(--sage); font-weight: 500; margin-right: 0.3rem; }

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(143,185,168,0.22), transparent);
    margin: 2.2rem 0;
}

/* ── Cards (keyed Streamlit containers) ── */
.st-key-input_card, .st-key-pipeline_card, .st-key-report_card, .st-key-critic_card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.8rem 2rem;
    box-shadow: 0 12px 40px rgba(0,0,0,0.18);
}
.st-key-report_card { border-color: var(--border-soft); }
.st-key-critic_card { border-color: rgba(134,184,150,0.20); }

.card-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--sage);
    margin-bottom: 0.2rem;
}
.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 1rem;
}
.hint {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 1.2rem 0 0.5rem;
}
.footnote { font-size: 0.78rem; color: var(--muted); margin-top: 1rem; line-height: 1.6; }

/* ── Text input ── */
.stTextInput label p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--text-2) !important;
}
.stTextInput div[data-baseweb="input"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    transition: border-color .2s ease, box-shadow .2s ease;
}
.stTextInput div[data-baseweb="input"]:focus-within {
    border-color: var(--sage) !important;
    box-shadow: 0 0 0 4px rgba(143,185,168,0.12) !important;
}
.stTextInput div[data-baseweb="base-input"] { background: transparent !important; }
.stTextInput input::placeholder { color: var(--muted) !important; }
.stTextInput input {
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: 0.85rem 1rem !important;
    background: transparent !important;
}

/* ── Primary button (Run) ── */
.stButton button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(120deg, #7fab99 0%, #9298c9 100%) !important;
    color: #10161c !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 8px 24px rgba(143,185,168,0.18) !important;
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease !important;
}
.stButton button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-1px);
    filter: brightness(1.05);
    box-shadow: 0 12px 30px rgba(143,185,168,0.25) !important;
}

/* ── Secondary buttons (example chips) ── */
.stButton button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background: var(--surface-2) !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-size: 0.8rem !important;
    padding: 0.45rem 0.8rem !important;
    min-height: 0 !important;
    line-height: 1.35 !important;
    transition: all .15s ease !important;
}
.stButton button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    color: var(--text) !important;
    border-color: var(--border-soft) !important;
    background: var(--sage-soft) !important;
}

/* ── Pipeline steps ── */
.step {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.95rem 1.1rem;
    margin-bottom: 0.7rem;
    border-radius: 14px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    transition: all .25s ease;
}
.step.running { border-color: rgba(143,185,168,0.40); background: var(--sage-soft); }
.step.done    { border-color: rgba(134,184,150,0.25); background: var(--done-soft); }

.step-index {
    flex: 0 0 38px;
    height: 38px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.03);
}
.step.running .step-index { color: var(--sage); border-color: var(--sage); }
.step.done .step-index    { color: #10161c; background: var(--done); border-color: var(--done); }

.step-body { flex: 1; min-width: 0; }
.step-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
}
.step-desc { font-size: 0.8rem; color: var(--muted); margin-top: 0.1rem; }
.step-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.12em;
    white-space: nowrap;
    color: var(--muted);
}
.step.running .step-status { color: var(--sage); }
.step.done .step-status    { color: var(--green); }
.step.failed               { border-color: rgba(229,115,115,0.35); background: rgba(229,115,115,0.07); }
.step.failed .step-index   { color: #10161c; background: var(--red); border-color: var(--red); }
.step.failed .step-status  { color: var(--red); }
.step.done                 { border-color: rgba(74,222,128,0.30); background: rgba(74,222,128,0.06); }
.step.done .step-index     { background: var(--green); border-color: var(--green); }

/* ── Status light ── */
.step-status { display: flex; align-items: center; gap: 0.5rem; }
.light {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #3a4450;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
    flex: 0 0 10px;
}
.light.running {
    background: #e8c170;
    box-shadow: 0 0 0 0 rgba(232,193,112,0.6);
    animation: ping 1.4s ease-out infinite;
}
.light.done {
    background: var(--green);
    box-shadow: 0 0 6px 2px rgba(74,222,128,0.55), 0 0 14px 4px rgba(74,222,128,0.25);
}
.light.failed {
    background: var(--red);
    box-shadow: 0 0 6px 2px rgba(229,115,115,0.5);
}
@keyframes ping {
    0%   { box-shadow: 0 0 0 0 rgba(232,193,112,0.55); }
    70%  { box-shadow: 0 0 0 8px rgba(232,193,112,0); }
    100% { box-shadow: 0 0 0 0 rgba(232,193,112,0); }
}

/* ── Progress bar ── */
[data-testid="stProgress"] [role="progressbar"] > div {
    background-color: rgba(255,255,255,0.06) !important;
}
[data-testid="stProgress"] [role="progressbar"] > div > div {
    background: linear-gradient(90deg, var(--sage), var(--peri)) !important;
}
[data-testid="stProgress"] p { color: var(--text-2) !important; font-size: 0.8rem !important; }

/* ── Section heading ── */
.section-heading {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 1rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    color: var(--muted);
    padding: 0.6rem 1rem;
}
.stTabs [aria-selected="true"] { color: var(--text) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--sage) !important; }

/* ── Alerts (warning / error / info) ── */
[data-testid="stAlert"] > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] p { color: var(--text) !important; }

/* ── Report typography ── */
.st-key-report_card h1, .st-key-report_card h2, .st-key-report_card h3,
.st-key-critic_card h1, .st-key-critic_card h2, .st-key-critic_card h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text);
}
.st-key-report_card p, .st-key-report_card li,
.st-key-critic_card p, .st-key-critic_card li {
    color: #ccd3dc;
    line-height: 1.8;
}

/* ── Expander ── */
[data-testid="stExpander"] details {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
}
[data-testid="stExpander"] summary p { color: var(--text-2); font-size: 0.9rem; }

/* ── Download button ── */
.stDownloadButton button {
    background: transparent !important;
    color: var(--sage) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
}
.stDownloadButton button:hover { background: var(--sage-soft) !important; }

/* ── Footer ── */
.notice {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    text-align: center;
    margin-top: 3.5rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Pipeline definition ───────────────────────────────────────────────────────
STEPS = [
    ("search", "01", "Search Agent", "Gathers recent web information"),
    ("reader", "02", "Reader Agent", "Scrapes & extracts deep content"),
    ("writer", "03", "Writer Chain", "Drafts the full research report"),
    ("critic", "04", "Critic Chain", "Reviews & scores the report"),
]
STATUS_LABEL = {"waiting": "WAITING", "running": "RUNNING",
                "done": "DONE", "failed": "FAILED"}


def step_html(num: str, title: str, desc: str, state: str) -> str:
    index = {"done": "✓", "failed": "✕"}.get(state, num)
    return f"""
    <div class="step {state}">
        <div class="step-index">{index}</div>
        <div class="step-body">
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        <div class="step-status"><span class="light {state}"></span>{STATUS_LABEL[state]}</div>
    </div>
    """


def step_state(key: str, results: dict, current: str | None = None,
               failed: str | None = None) -> str:
    if key in results:
        return "done"
    if key == failed:
        return "failed"
    if key == current:
        return "running"
    return "waiting"


# ── Session state ─────────────────────────────────────────────────────────────
st.session_state.setdefault("results", {})
st.session_state.setdefault("running", False)
st.session_state.setdefault("done", False)
st.session_state.setdefault("topic_input", "")


def use_example(text: str):
    st.session_state.topic_input = text


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research <span>Agent</span></h1>
    <div class="hero-sub">
        Four specialized AI agents collaborate — searching, reading, writing
        and critiquing — to deliver a polished research report on any topic.
    </div>
    <div class="hero-pills">
        <span class="hero-pill"><b>4</b>Specialized agents</span>
        <span class="hero-pill"><b>◎</b>Live web research</span>
        <span class="hero-pill"><b>✓</b>Self-reviewed output</span>
    </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_pipeline = st.columns([1.1, 1], gap="large")

with col_input:
    with st.container(key="input_card"):
        st.markdown(
            '<div class="card-label">Start here</div>'
            '<div class="card-title">What should we research?</div>',
            unsafe_allow_html=True,
        )

        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Roadmap for AGI development in next 5 years",
            key="topic_input",
        )

        run_btn = st.button(
            "Run Research Pipeline  →",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running,
        )

        st.markdown('<div class="hint">Try an example</div>',
                    unsafe_allow_html=True)

        examples = [
            "Future of LLMs in the tech industry",
            "Latest AI agents in 2026",
            "Roadmap for AGI in the next 5 years",
        ]
        chip_cols = st.columns(len(examples))
        for col, ex in zip(chip_cols, examples):
            col.button(ex, key=f"ex_{ex}", on_click=use_example, args=(ex,),
                       use_container_width=True)

        st.markdown(
            '<div class="footnote">A full run typically takes a minute or two. '
            'The final report can be downloaded as Markdown.</div>',
            unsafe_allow_html=True,
        )

with col_pipeline:
    with st.container(key="pipeline_card"):
        st.markdown(
            '<div class="card-label">Live status</div>'
            '<div class="card-title">Agent Pipeline</div>',
            unsafe_allow_html=True,
        )

        placeholders = {}
        r = st.session_state.results
        failed_step = st.session_state.get("failed_step")
        for key, num, title, desc in STEPS:
            placeholders[key] = st.empty()
            placeholders[key].markdown(
                step_html(num, title, desc, step_state(
                    key, r, failed=failed_step)),
                unsafe_allow_html=True,
            )

        progress_ph = st.empty()
        completed = sum(k in r for k, *_ in STEPS)
        if completed:
            progress_ph.progress(completed / len(STEPS),
                                 text=f"{completed} of {len(STEPS)} steps complete")


# ── Run trigger ───────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.failed_step = None
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()


# ── Run pipeline (updates the pipeline cards live) ───────────────────────────
if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input.strip()

    current = None

    def refresh(label: str, failed: str | None = None):
        for key, num, title, desc in STEPS:
            placeholders[key].markdown(
                step_html(num, title, desc,
                          step_state(key, results, current, failed)),
                unsafe_allow_html=True,
            )
        progress_ph.progress(len(results) / len(STEPS), text=label)

    try:
        # Step 1: Search
        current = "search"
        refresh("Search Agent is gathering sources…")
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user",
                          f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        refresh("Search Agent complete ✓")          # green light now

        # Step 2: Reader
        current = "reader"
        refresh("Reader Agent is scraping top resources…")
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        refresh("Reader Agent complete ✓")

        # Step 3: Writer
        current = "writer"
        refresh("Writer is drafting the report…")
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined,
        })
        refresh("Writer complete ✓")

        # Step 4: Critic
        current = "critic"
        refresh("Critic is reviewing the report…")
        results["critic"] = critic_chain.invoke({"report": results["writer"]})
        current = None
        refresh("All agents complete ✓")
        time.sleep(0.8)  # let the final green light show before results load

    except Exception as e:
        failed = current
        current = None
        refresh("Pipeline stopped", failed=failed)
        st.session_state.results = results
        st.session_state.failed_step = failed
        st.session_state.running = False
        st.error(f"The pipeline stopped unexpectedly: {e}")
        st.stop()

    st.session_state.results = results
    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r and not st.session_state.running:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>',
                unsafe_allow_html=True)

    tab_report, tab_critic, tab_sources = st.tabs(
        ["📝  Research Report", "🧐  Critic Review", "🔍  Sources"]
    )

    with tab_report:
        if "writer" in r:
            with st.container(key="report_card"):
                st.markdown(r["writer"])
            st.download_button(
                label="⬇  Download Report (.md)",
                data=r["writer"],
                file_name=f"research_report_{int(time.time())}.md",
                mime="text/markdown",
            )
        else:
            st.info("The report wasn't generated in this run.")

    with tab_critic:
        if "critic" in r:
            with st.container(key="critic_card"):
                st.markdown(r["critic"])
        else:
            st.info("The critic review wasn't generated in this run.")

    with tab_sources:
        if "search" in r:
            with st.expander("Search Agent output", expanded=False):
                st.markdown(r["search"])
        if "reader" in r:
            with st.expander("Reader Agent output (scraped content)", expanded=False):
                st.markdown(r["reader"])


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    Research Agent · LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)
