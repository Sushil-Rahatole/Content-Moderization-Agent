import streamlit as st
import json, datetime
from config.settings import APP_TITLE, APP_ICON, SAMPLE_PROMPTS, PLATFORM_POLICIES, VERDICTS
from components.sidebar  import render_sidebar
from components.results  import render_result
from components.dashboard import render_dashboard
from agent.moderator     import analyze_text, analyze_appeal, analyze_url_content
from utils.logger        import init_log, add_log_entry, get_log, get_stats
from utils.exporter      import generate_csv, get_export_filename
from utils.url_scanner   import fetch_url_text

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
html, body, [class*="css"] { font-family:'Syne',sans-serif; background:#0a0a0f; color:#e8e8f0; }
.stApp { background:#0a0a0f; }
div[data-testid="stSidebar"] { background:#0d0d18 !important; }
.hero { text-align:center; padding:1rem 0 0.5rem 0; }
.hero h1 { font-size:2.6rem; font-weight:800;
    background:linear-gradient(135deg,#ff4d6d,#f72585,#7209b7);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0; }
.hero p { color:#555; font-family:'Space Mono',monospace; font-size:0.85rem; margin-top:4px; }
.stTextArea textarea { background:#12121c !important; color:#e8e8f0 !important;
    border:1.5px solid #2a2a3e !important; border-radius:10px !important;
    font-family:'Space Mono',monospace !important; }
.stTextInput input { background:#12121c !important; color:#e8e8f0 !important;
    border:1.5px solid #2a2a3e !important; border-radius:10px !important; }
.stButton>button { background:linear-gradient(135deg,#f72585,#7209b7) !important;
    color:#fff !important; border:none !important; border-radius:10px !important;
    font-weight:700 !important; font-family:'Syne',sans-serif !important; }
.stButton>button:hover { opacity:0.85 !important; }
.stTabs [data-baseweb="tab"] { font-family:'Syne',sans-serif !important; font-weight:700 !important; color:#888 !important; }
.stTabs [aria-selected="true"] { color:#f72585 !important; }
.policy-badge { display:inline-block; background:#1a0a2e; border:1px solid #7209b7;
    color:#b07ff7; border-radius:20px; padding:3px 14px; font-size:0.8rem;
    font-family:monospace; margin-bottom:0.5rem; }
.appeal-box { background:#12121c; border:1.5px solid #f59e0b; border-radius:12px; padding:1rem 1.2rem; margin-top:1rem; }
.webhook-box { background:#0d1117; border:1px solid #2a2a3e; border-radius:10px;
    padding:1rem; font-family:'Space Mono',monospace; font-size:0.78rem; color:#7ee787; }
</style>
""", unsafe_allow_html=True)

init_log()
api_key = render_sidebar()

st.markdown("""
<div class="hero">
  <h1>🛡️ ContentGuard AI</h1>
  <p>Real-time Content Moderation Agent · Risk Scoring · Multi-platform · AgentX 2026</p>
</div>
""", unsafe_allow_html=True)

active_policy = st.session_state.get("active_policy", "🌐 General Platform")
st.markdown(f'<div style="text-align:center"><span class="policy-badge">📋 Active Policy: {active_policy}</span></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Analyze Text",
    "🌐 URL Scanner",
    "📦 Batch Mode",
    "📊 Dashboard",
    "⚙️ Policy & API Docs",
])


with tab1:
    st.markdown("### 📝 Analyze Text Content")

    s_cols = st.columns(3)
    for i, (label, sample) in enumerate(SAMPLE_PROMPTS.items()):
        with s_cols[i]:
            st.markdown(f"**{label}**")
            st.caption(sample[:70] + "...")
            if st.button(f"Use sample", key=f"s{i}", use_container_width=True):
                st.session_state["prefill"] = sample

    st.markdown("")
    prefill   = st.session_state.pop("prefill", "")
    user_text = st.text_area("", value=prefill,
                             placeholder="Paste or type any content to moderate...",
                             height=150, key="main_text")
    st.markdown(f"<div style='text-align:right;color:#444;font-size:0.75rem;font-family:monospace'>{len(user_text)} chars</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1: analyze_btn = st.button("🔍 Analyze Content", use_container_width=True)
    with c2:
        if st.button("↺", use_container_width=True):
            st.session_state.pop("t1_result", None)
            st.rerun()

    if analyze_btn:
        if not api_key:
            st.error("⚠️ Enter your Groq API key in the sidebar.")
        elif len(user_text.strip()) < 5:
            st.warning("⚠️ Text too short.")
        else:
            with st.spinner("🤖 Agent analyzing..."):
                try:
                    policy_ctx = PLATFORM_POLICIES.get(active_policy, "")
                    result     = analyze_text(api_key, user_text, policy_ctx)
                    add_log_entry(user_text, result, source="text")
                    st.session_state["t1_result"] = (result, user_text)
                except Exception as e:
                    st.error(f"Agent error: {e}")

    if "t1_result" in st.session_state:
        result, orig = st.session_state["t1_result"]
        render_result(result, orig)

        if result["verdict"] in ("REVIEW", "BLOCK"):
            st.markdown('<div class="appeal-box">', unsafe_allow_html=True)
            st.markdown("#### ⚖️ Appeal This Decision")
            st.caption("Think the verdict is unfair? Provide context and the agent will reconsider.")
            appeal_text = st.text_area("Explain your context / reason for appeal:",
                                        placeholder="e.g. This is a quote from a history textbook discussing past atrocities...",
                                        height=80, key="appeal_input")
            if st.button("📨 Submit Appeal", use_container_width=True):
                if not appeal_text.strip():
                    st.warning("Please provide an appeal reason.")
                else:
                    with st.spinner("🤖 Agent reconsidering..."):
                        try:
                            appeal_result = analyze_appeal(api_key, orig, result, appeal_text)
                            add_log_entry(orig, appeal_result, source="appeal")
                            st.session_state["t1_result"] = (appeal_result, orig)
                            old_score = result["risk_score"]
                            new_score = appeal_result["risk_score"]
                            if new_score < old_score:
                                st.success(f"✅ Appeal partially accepted! Score: {old_score} → {new_score}")
                            else:
                                st.info(f"⚖️ Appeal reviewed. Score maintained at {new_score}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Appeal error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("🔌 Webhook Payload (API Integration Preview)"):
            st.markdown("This is what ContentGuard would POST to your app's endpoint in production:")
            payload = {
                "event":      "content.moderated",
                "timestamp":  datetime.datetime.now().isoformat(),
                "platform":   active_policy,
                "verdict":    result["verdict"],
                "risk_score": result["risk_score"],
                "flagged":    result.get("flagged_categories", []),
                "confidence": result.get("confidence", ""),
                "action":     "block" if result["verdict"] == "BLOCK" else ("queue_review" if result["verdict"] == "REVIEW" else "allow"),
                "text_hash":  hex(hash(orig) & 0xFFFFFFFF),
            }
            st.markdown(f'<div class="webhook-box">{json.dumps(payload, indent=2)}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### 🌐 URL Content Scanner")
    st.markdown("Enter any public URL. The agent fetches the page and moderates its content automatically.")
    st.info("💡 Real-world use: Social platforms use this to moderate links before users click them.")

    url_input = st.text_input("", placeholder="https://example.com/article", key="url_input")

    if st.button("🔍 Scan URL", use_container_width=True):
        if not api_key:
            st.error("⚠️ Enter your Groq API key in the sidebar.")
        elif not url_input.strip():
            st.warning("⚠️ Please enter a URL.")
        else:
            with st.spinner("🌐 Fetching page content..."):
                try:
                    page_text = fetch_url_text(url_input.strip())
                    st.success(f"✅ Fetched {len(page_text)} characters from page.")
                except Exception as e:
                    st.error(f"❌ Could not fetch URL: {e}")
                    page_text = None

            if page_text:
                with st.spinner("🤖 Agent moderating page content..."):
                    try:
                        result = analyze_url_content(api_key, page_text, url_input)
                        add_log_entry(page_text[:500], result, source=f"url:{url_input}")
                        render_result(result, f"[URL] {url_input}\n\n{page_text[:300]}...")
                    except Exception as e:
                        st.error(f"Moderation error: {e}")

with tab3:
    st.markdown("### 📦 Batch Moderation — CSV Upload")
    st.markdown("Upload a CSV with a `text` column. The agent moderates every row automatically.")

    template = "text\nI love this product!\nBuy cheap pills now, click here!\nI hate everyone from that country."
    st.download_button("📄 Download CSV Template", data=template.encode(),
                       file_name="template.csv", mime="text/csv")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        import pandas as pd
        df = pd.read_csv(uploaded)
        if "text" not in df.columns:
            st.error("⚠️ CSV must have a 'text' column.")
        else:
            st.success(f"✅ {len(df)} rows loaded.")
            st.dataframe(df.head(5), use_container_width=True, hide_index=True)
            max_rows = min(len(df), 20)
            st.info(f"Will process up to {max_rows} rows.")

            if st.button("🚀 Run Batch Moderation", use_container_width=True):
                if not api_key:
                    st.error("⚠️ Enter your Groq API key.")
                else:
                    results_list = []
                    prog = st.progress(0, text="Starting...")
                    status = st.empty()
                    policy_ctx = PLATFORM_POLICIES.get(active_policy, "")

                    for i, row in df.head(max_rows).iterrows():
                        text = str(row["text"]).strip()
                        if not text: continue
                        status.markdown(f"🔍 Row {i+1} / {max_rows}...")
                        try:
                            res = analyze_text(api_key, text, policy_ctx)
                            add_log_entry(text, res, source="batch")
                            v = res["verdict"]
                            results_list.append({
                                "text":               text[:80],
                                "risk_score":         res["risk_score"],
                                "verdict":            v,
                                "flagged_categories": ", ".join(res.get("flagged_categories", [])),
                                "reasoning":          res.get("reasoning", ""),
                            })
                        except Exception as e:
                            results_list.append({"text": text[:80], "verdict": "ERROR", "error": str(e)})
                        prog.progress((i+1)/max_rows, text=f"Processed {i+1}/{max_rows}")

                    status.empty(); prog.empty()
                    st.success(f"✅ Batch complete — {len(results_list)} items moderated!")
                    rdf = pd.DataFrame(results_list)
                    st.dataframe(rdf, use_container_width=True, hide_index=True)

                    # Color summary
                    c1,c2,c3 = st.columns(3)
                    c1.metric("✅ Allowed",  sum(1 for r in results_list if r.get("verdict")=="ALLOW"))
                    c2.metric("⚠️ Review",   sum(1 for r in results_list if r.get("verdict")=="REVIEW"))
                    c3.metric("🚫 Blocked",  sum(1 for r in results_list if r.get("verdict")=="BLOCK"))

                    st.download_button("📥 Download Results CSV",
                                       data=rdf.to_csv(index=False).encode(),
                                       file_name="batch_results.csv", mime="text/csv",
                                       use_container_width=True)

with tab4:
    render_dashboard()

with tab5:
    st.markdown("### ⚙️ Platform Policy Builder")
    st.markdown("Select the policy that matches your platform. The agent adjusts its strictness automatically.")

    selected = st.selectbox("Choose Platform Policy", list(PLATFORM_POLICIES.keys()),
                             index=list(PLATFORM_POLICIES.keys()).index(active_policy))
    st.session_state["active_policy"] = selected
    st.info(f"**Policy Rule:** {PLATFORM_POLICIES[selected]}")

    if st.button("✅ Apply Policy", use_container_width=True):
        st.success(f"Policy set to: {selected}")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📖 API Integration Docs")
    st.markdown("How to integrate ContentGuard into your own app:")

    st.code("""# Python Integration Example
import requests

response = requests.post("https://your-app.com/moderate", json={
    "text": "User submitted content here",
    "platform": "kids_app",
    "api_key": "your_contentguard_key"
})

result = response.json()
# result = {
#   "verdict": "BLOCK",
#   "risk_score": 87,
#   "flagged_categories": ["Hate Speech"],
#   "action": "block",
#   "reasoning": "..."
# }

if result["verdict"] == "BLOCK":
    hide_content()
elif result["verdict"] == "REVIEW":
    send_to_human_review()
else:
    publish_content()
""", language="python")

    st.markdown("### 🔌 Supported Integrations")
    col1, col2, col3 = st.columns(3)
    col1.success("✅ REST API")
    col2.success("✅ Webhook POST")
    col3.success("✅ CSV Batch")
    col1.success("✅ Multi-language")
    col2.success("✅ Appeal System")
    col3.success("✅ Policy Builder")