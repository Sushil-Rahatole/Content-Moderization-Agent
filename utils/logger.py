import streamlit as st
from datetime import datetime


def init_log():
    if "moderation_log"  not in st.session_state: st.session_state.moderation_log  = []
    if "total_analyzed"  not in st.session_state: st.session_state.total_analyzed  = 0
    if "active_policy"   not in st.session_state: st.session_state.active_policy   = "🌐 General Platform"
    if "last_result"     not in st.session_state: st.session_state.last_result     = None


def add_log_entry(text: str, result: dict, source: str = "text"):
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
    st.session_state.moderation_log.append(entry)
    st.session_state.total_analyzed += 1


def get_log() -> list:
    return st.session_state.get("moderation_log", [])


def clear_log():
    st.session_state.moderation_log = []
    st.session_state.total_analyzed = 0


def get_stats() -> dict:
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
        "avg_score": round(sum(scores) / len(scores), 1),
        "appeals":   sum(1 for e in log if e.get("is_appeal")),
    }