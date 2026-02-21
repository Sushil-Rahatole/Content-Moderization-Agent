# ─── components/dashboard.py ──────────────────────────────────────────────────
# Analytics dashboard — charts and stats from session log

import streamlit as st
from utils.logger import get_log, get_stats
from collections import Counter
import pandas as pd


def _render_verdict_bar(allow_pct, review_pct, block_pct):
    """
    Render verdict distribution using Streamlit columns + native elements.
    Avoids all HTML f-string rendering issues entirely.
    """
    st.markdown("**Verdict Distribution**")

    # Use st.columns proportionally — this is 100% reliable, no HTML needed
    total_pct = allow_pct + review_pct + block_pct

    if total_pct == 0:
        return

    # Build a colored progress-style bar using pure HTML — simple single string
    bar_html = (
        "<div style='"
        "display:flex; height:30px; border-radius:10px; overflow:hidden;"
        "background:#1e1e2e; width:100%;'>"
    )

    if allow_pct > 0:
        bar_html += (
            "<div style='"
            "width:" + str(allow_pct) + "%;"
            "background:#22c55e;"
            "display:flex; align-items:center; justify-content:center;"
            "font-size:0.75rem; font-weight:700; color:#000;'>"
            + (str(allow_pct) + "%" if allow_pct > 10 else "") +
            "</div>"
        )

    if review_pct > 0:
        bar_html += (
            "<div style='"
            "width:" + str(review_pct) + "%;"
            "background:#f59e0b;"
            "display:flex; align-items:center; justify-content:center;"
            "font-size:0.75rem; font-weight:700; color:#000;'>"
            + (str(review_pct) + "%" if review_pct > 10 else "") +
            "</div>"
        )

    if block_pct > 0:
        bar_html += (
            "<div style='"
            "width:" + str(block_pct) + "%;"
            "background:#ef4444;"
            "display:flex; align-items:center; justify-content:center;"
            "font-size:0.75rem; font-weight:700; color:#fff;'>"
            + (str(block_pct) + "%" if block_pct > 10 else "") +
            "</div>"
        )

    bar_html += "</div>"

    st.markdown(bar_html, unsafe_allow_html=True)

    # Legend below — simple columns, no HTML
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f"<div style='color:#22c55e; font-family:monospace; font-size:0.85rem;'>"
        f"🟢 Allow &nbsp; {allow_pct}%</div>",
        unsafe_allow_html=True
    )
    c2.markdown(
        f"<div style='color:#f59e0b; font-family:monospace; font-size:0.85rem;'>"
        f"🟡 Review {review_pct}%</div>",
        unsafe_allow_html=True
    )
    c3.markdown(
        f"<div style='color:#ef4444; font-family:monospace; font-size:0.85rem;'>"
        f"🔴 Block &nbsp; {block_pct}%</div>",
        unsafe_allow_html=True
    )


def render_dashboard():
    """Render the full analytics dashboard tab."""
    log   = get_log()
    stats = get_stats()

    # ── Empty State ──────────────────────────────────────────────────────────
    if not log:
        st.markdown(
            "<div style='text-align:center; padding:3rem; color:#555;'>"
            "<div style='font-size:3rem;'>📊</div>"
            "<div style='font-size:1rem; margin-top:0.5rem;'>"
            "No data yet. Analyze some text to see your dashboard."
            "</div></div>",
            unsafe_allow_html=True
        )
        return

    # ── KPI Metrics ──────────────────────────────────────────────────────────
    st.markdown("### 📊 Session Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📝 Total",     stats["total"])
    c2.metric("✅ Allowed",   stats["allow"])
    c3.metric("⚠️ Reviewed",  stats["review"])
    c4.metric("🚫 Blocked",   stats["block"])
    c5.metric("📈 Avg Score", stats["avg_score"])

    st.markdown("---")

    # ── Verdict Distribution ──────────────────────────────────────────────────
    st.markdown("### 🎯 Verdict Distribution")
    total = stats["total"]
    if total > 0:
        allow_pct  = round((stats["allow"]  / total) * 100)
        review_pct = round((stats["review"] / total) * 100)
        block_pct  = round((stats["block"]  / total) * 100)
        _render_verdict_bar(allow_pct, review_pct, block_pct)

    st.markdown("---")

    # ── Most Flagged Categories ──────────────────────────────────────────────
    st.markdown("### 🚩 Most Flagged Categories")
    all_flagged = []
    for entry in log:
        cats = entry.get("flagged_categories", "")
        if cats:
            all_flagged.extend([c.strip() for c in cats.split(",") if c.strip()])

    if all_flagged:
        counts    = Counter(all_flagged).most_common(8)
        max_count = counts[0][1]
        for cat, count in counts:
            bar_pct = int((count / max_count) * 100)
            # Each bar is built as a plain concatenated string — no f-string nesting
            bar_html = (
                "<div style='margin-bottom:12px;'>"
                "<div style='"
                "display:flex; justify-content:space-between;"
                "font-size:0.82rem; color:#ccc; margin-bottom:4px;"
                "font-family:monospace;'>"
                "<span>🚩 " + cat + "</span>"
                "<span>" + str(count) + "x</span>"
                "</div>"
                "<div style='"
                "background:#1e1e2e; border-radius:50px;"
                "height:8px; overflow:hidden;'>"
                "<div style='"
                "width:" + str(bar_pct) + "%;"
                "height:100%;"
                "background:linear-gradient(90deg,#f72585,#7209b7);"
                "border-radius:50px;'>"
                "</div>"
                "</div>"
                "</div>"
            )
            st.markdown(bar_html, unsafe_allow_html=True)
    else:
        st.success("🎉 No harmful categories flagged in this session!")

    st.markdown("---")

    # ── Full Moderation Log ──────────────────────────────────────────────────
    st.markdown("### 📋 Full Moderation Log")
    df           = pd.DataFrame(log)
    display_cols = ["timestamp", "text", "risk_score", "verdict", "flagged_categories"]
    existing     = [c for c in display_cols if c in df.columns]
    df_display   = df[existing].copy()
    df_display["text"] = df_display["text"].str[:60] + "..."
    st.dataframe(df_display, use_container_width=True, hide_index=True)