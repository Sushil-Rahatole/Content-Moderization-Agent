
import streamlit as st
from config.settings import VERDICTS


def render_result(result: dict, original_text: str):
    """Display the full moderation result in a structured UI."""

    verdict  = result["verdict"]
    score    = result["risk_score"]
    flagged  = result.get("flagged_categories", [])
    safe     = result.get("safe_categories", [])
    reason   = result.get("reasoning", "")
    suggest  = result.get("suggestions", "")
    conf     = result.get("confidence", "")

    v        = VERDICTS[verdict]
    emoji    = v["emoji"]
    color    = v["color"]
    bg       = v["bg"]
    border   = v["border"]

    # ── Main Verdict Card ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:{bg}; border:1.5px solid {border}; border-radius:14px;
         padding:1.5rem 2rem; margin-top:1.2rem;'>
        <div style='font-size:1.8rem; font-weight:800; color:{color};
             font-family:monospace; letter-spacing:2px;'>
            {emoji} {verdict}
        </div>
        <div style='color:#aaa; font-size:0.85rem; margin-top:6px;'>
            Risk Score: <b style='color:#fff; font-size:1.1rem;'>{score}</b> / 100
            &nbsp;&nbsp;|&nbsp;&nbsp; Confidence: <b style='color:#fff;'>{conf}</b>
        </div>
        <div style='background:#1e1e2e; border-radius:50px; height:12px;
             margin-top:10px; overflow:hidden;'>
            <div style='width:{score}%; height:100%; background:{color};
                 border-radius:50px;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🚩 Flagged Categories")
        if flagged:
            for cat in flagged:
                st.markdown(f"""
                <span style='display:inline-block; background:#2e0d0d;
                     border:1px solid #ef4444; color:#ef4444; border-radius:20px;
                     padding:3px 12px; margin:3px; font-size:0.8rem;
                     font-family:monospace;'>🚩 {cat}</span>
                """, unsafe_allow_html=True)
        else:
            st.success("No harmful categories detected")

    with col2:
        st.markdown("#### ✅ Clean Categories")
        if safe:
            for cat in safe:
                st.markdown(f"""
                <span style='display:inline-block; background:#0d2e1a;
                     border:1px solid #22c55e; color:#22c55e; border-radius:20px;
                     padding:3px 12px; margin:3px; font-size:0.8rem;
                     font-family:monospace;'>✓ {cat}</span>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 🧠 Agent Reasoning")
        st.info(reason)
    with col4:
        st.markdown("#### 💡 Improvement Suggestion")
        st.success(suggest)

    with st.expander("📄 View Analyzed Text"):
        st.markdown(f"""
        <div style='background:#12121c; border-radius:8px; padding:1rem;
             font-family:monospace; font-size:0.85rem; color:#ccc; line-height:1.6;'>
            {original_text}
        </div>
        """, unsafe_allow_html=True)
