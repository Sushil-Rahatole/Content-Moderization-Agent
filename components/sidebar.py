import streamlit as st
from utils.logger import get_log, get_stats, clear_log
from utils.exporter import generate_csv, get_export_filename
from config.settings import HARMFUL_CATEGORIES, APP_VERSION


def get_api_key() -> str:
    """
    Auto-detect API key from Streamlit Cloud secrets.
    Falls back to manual input if not found.
    """
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key and key != "gsk_your_key_here":
            return key
    except Exception:
        pass
    return None


def render_sidebar() -> str:
    """Render sidebar and return the active API key."""
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:0.5rem 0 1rem 0;'>
            <div style='font-size:2.2rem;'>🛡️</div>
            <div style='font-weight:800; font-size:1.15rem; color:#e8e8f0;'>ContentGuard AI</div>
            <div style='font-size:0.7rem; color:#555; font-family:monospace;'>v{APP_VERSION} · AgentX 2026</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🔑 API Configuration")
        secret_key = get_api_key()

        if secret_key:
            st.success("✅ API Key loaded from cloud secrets")
            api_key = secret_key
        else:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Get your free key at console.groq.com"
            )
            if not api_key:
                st.warning("⚠️ Enter your free Groq API key above")
                st.markdown("[🔗 Get free key →](https://console.groq.com)", unsafe_allow_html=False)

        st.markdown("---")

        st.markdown("### 📊 Risk Thresholds")
        st.markdown("🟢 **ALLOW** &nbsp;&nbsp; Score 0 – 39")
        st.markdown("🟡 **REVIEW** &nbsp; Score 40 – 69")
        st.markdown("🔴 **BLOCK** &nbsp;&nbsp; Score 70 – 100")
        st.markdown("---")

        stats = get_stats()
        st.markdown("### 📈 Session Stats")
        c1, c2 = st.columns(2)
        c1.metric("Analyzed",   stats["total"])
        c2.metric("Avg Score",  stats["avg_score"])
        c1.metric("✅ Allow",   stats["allow"])
        c2.metric("⚠️ Review",  stats["review"])
        st.metric("🚫 Blocked", stats["block"])
        if stats.get("appeals", 0):
            st.metric("⚖️ Appeals", stats["appeals"])
        st.markdown("---")

        st.markdown("### 🔍 Categories")
        for cat in HARMFUL_CATEGORIES:
            st.markdown(f"• {cat}")
        st.markdown("---")

        log = get_log()
        if log:
            st.download_button(
                "📥 Download Report (CSV)",
                data=generate_csv(log),
                file_name=get_export_filename(),
                mime="text/csv",
                use_container_width=True
            )
            if st.button("🗑️ Clear Session", use_container_width=True):
                clear_log()
                st.rerun()

        if log:
            st.markdown("---")
            st.markdown("### 📜 Recent")
            for entry in reversed(log[-5:]):
                v = entry["verdict"]
                color = "#22c55e" if v=="ALLOW" else ("#f59e0b" if v=="REVIEW" else "#ef4444")
                emoji = "🟢" if v=="ALLOW" else ("🟡" if v=="REVIEW" else "🔴")
                short = entry["text"][:40]+"..." if len(entry["text"])>40 else entry["text"]
                src   = f" [{entry.get('source','text')}]" if entry.get('source') != 'text' else ''
                st.markdown(f"""
                <div style='background:#12121c; border-left:3px solid {color};
                     border-radius:6px; padding:5px 10px; margin-bottom:5px;
                     font-size:0.72rem; font-family:monospace; color:#ccc;'>
                    {emoji}{src} {short}<br>
                    <b style='color:{color};'>{entry["risk_score"]} · {v}</b>
                </div>
                """, unsafe_allow_html=True)

    return api_key