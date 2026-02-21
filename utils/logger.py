# ─── utils/logger.py ──────────────────────────────────────────────────────────
# Dual-mode logger: MongoDB (persistent) + Session State (fallback)

import streamlit as st
from datetime import datetime
from utils.database import (
    is_db_connected, save_log_entry,
    fetch_all_logs, fetch_stats_from_db, clear_all_logs
)


def init_log():
    """Initialize session state variables."""
    if "moderation_log" not in st.session_state:
        st.session_state.moderation_log = []
    if "total_analyzed" not in st.session_state:
        st.session_state.total_analyzed = 0
    if "active_policy"  not in st.session_state:
        st.session_state.active_policy  = "🌐 General Platform"
    if "last_result"    not in st.session_state:
        st.session_state.last_result    = None
    if "db_synced"      not in st.session_state:
        st.session_state.db_synced      = False


def sync_from_db():
    """Pull existing MongoDB logs into session on first page load."""
    if not st.session_state.get("db_synced", False) and is_db_connected():
        logs = fetch_all_logs(limit=200)
        st.session_state.moderation_log = logs
        st.session_state.total_analyzed = len(logs)
        st.session_state.db_synced      = True


def add_log_entry(text: str, result: dict, source: str = "text"):
    """Save to MongoDB (persistent) + session state (real-time UI)."""
    entry = {
        "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source":             source,
        "text":               text,
        "risk_score":         result.get("risk_score", 0),
        "verdict":            result.get("verdict", ""),
        "flagged_categories": ", ".join(result.get("flagged_categories", [])),
        "safe_categories":    ", ".join(result.get("safe_categories", [])),
        "reasoning":          result.get("reasoning", ""),
        "suggestions":        result.get("suggestions", ""),
        "confidence":         result.get("confidence", ""),
        "is_appeal":          result.get("is_appeal", False),
    }
    if is_db_connected():
        save_log_entry(text, result, source)
    st.session_state.moderation_log.insert(0, entry)
    st.session_state.total_analyzed += 1


def get_log() -> list:
    return st.session_state.get("moderation_log", [])


def get_stats() -> dict:
    if is_db_connected():
        return fetch_stats_from_db()
    log = get_log()
    if not log:
        return {"total": 0, "allow": 0, "review": 0, "block": 0, "avg_score": 0, "appeals": 0}
    verdicts = [e["verdict"] for e in log]
    scores   = [e["risk_score"] for e in log]
    return {
        "total":     len(log),
        "allow":     verdicts.count("ALLOW"),
        "review":    verdicts.count("REVIEW"),
        "block":     verdicts.count("BLOCK"),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "appeals":   sum(1 for e in log if e.get("is_appeal")),
    }


def clear_log():
    if is_db_connected():
        clear_all_logs()
    st.session_state.moderation_log = []
    st.session_state.total_analyzed = 0
    st.session_state.db_synced      = False