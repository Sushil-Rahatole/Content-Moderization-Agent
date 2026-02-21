# ─── utils/database.py ────────────────────────────────────────────────────────
# MongoDB Atlas integration for persistent moderation log storage

import streamlit as st
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


# ── Connection ────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_db_client():
    """
    Create a cached MongoDB client using Streamlit secrets.
    Returns None if connection fails (graceful degradation).
    """
    try:
        uri    = st.secrets.get("MONGO_URI", "")
        if not uri:
            return None
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")   # verify connection
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
        return None


def get_collection():
    """Return the moderation_logs collection or None."""
    client = get_db_client()
    if client is None:
        return None
    try:
        db  = client["contentguard"]
        col = db["moderation_logs"]
        # Create indexes for fast querying
        col.create_index([("timestamp", DESCENDING)])
        col.create_index([("verdict",   1)])
        return col
    except Exception:
        return None


def is_db_connected() -> bool:
    """Check if MongoDB is available."""
    return get_collection() is not None


# ── Write ─────────────────────────────────────────────────────────────────────

def save_log_entry(text: str, result: dict, source: str = "text") -> bool:
    """
    Save a moderation result to MongoDB.
    Returns True on success, False on failure.
    """
    col = get_collection()
    if col is None:
        return False
    try:
        doc = {
            "timestamp":          datetime.utcnow(),
            "timestamp_str":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source":             source,
            "text":               text,
            "risk_score":         result.get("risk_score", 0),
            "verdict":            result.get("verdict", ""),
            "flagged_categories": result.get("flagged_categories", []),
            "safe_categories":    result.get("safe_categories", []),
            "reasoning":          result.get("reasoning", ""),
            "suggestions":        result.get("suggestions", ""),
            "confidence":         result.get("confidence", ""),
            "is_appeal":          result.get("is_appeal", False),
        }
        col.insert_one(doc)
        return True
    except Exception:
        return False


# ── Read ──────────────────────────────────────────────────────────────────────

def fetch_all_logs(limit: int = 200) -> list:
    """
    Fetch recent moderation logs from MongoDB.
    Returns list of dicts compatible with session log format.
    """
    col = get_collection()
    if col is None:
        return []
    try:
        docs = col.find(
            {},
            {"_id": 0}
        ).sort("timestamp", DESCENDING).limit(limit)

        results = []
        for doc in docs:
            results.append({
                "timestamp":          doc.get("timestamp_str", ""),
                "source":             doc.get("source", "text"),
                "text":               doc.get("text", ""),
                "risk_score":         doc.get("risk_score", 0),
                "verdict":            doc.get("verdict", ""),
                "flagged_categories": ", ".join(doc.get("flagged_categories", [])),
                "safe_categories":    ", ".join(doc.get("safe_categories", [])),
                "reasoning":          doc.get("reasoning", ""),
                "suggestions":        doc.get("suggestions", ""),
                "confidence":         doc.get("confidence", ""),
                "is_appeal":          doc.get("is_appeal", False),
            })
        return results
    except Exception:
        return []


def fetch_stats_from_db() -> dict:
    """
    Compute aggregate stats directly from MongoDB.
    Much faster than loading all docs for large datasets.
    """
    col = get_collection()
    if col is None:
        return {"total": 0, "allow": 0, "review": 0, "block": 0, "avg_score": 0, "appeals": 0}
    try:
        total   = col.count_documents({})
        allow   = col.count_documents({"verdict": "ALLOW"})
        review  = col.count_documents({"verdict": "REVIEW"})
        block   = col.count_documents({"verdict": "BLOCK"})
        appeals = col.count_documents({"is_appeal": True})

        # Avg score via aggregation pipeline
        pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$risk_score"}}}]
        avg_result = list(col.aggregate(pipeline))
        avg_score  = round(avg_result[0]["avg"], 1) if avg_result else 0

        return {
            "total":     total,
            "allow":     allow,
            "review":    review,
            "block":     block,
            "avg_score": avg_score,
            "appeals":   appeals,
        }
    except Exception:
        return {"total": 0, "allow": 0, "review": 0, "block": 0, "avg_score": 0, "appeals": 0}


def fetch_flagged_categories(limit: int = 500) -> list:
    """Fetch all flagged categories for analytics."""
    col = get_collection()
    if col is None:
        return []
    try:
        docs = col.find(
            {"flagged_categories": {"$ne": []}},
            {"_id": 0, "flagged_categories": 1}
        ).limit(limit)
        all_cats = []
        for doc in docs:
            all_cats.extend(doc.get("flagged_categories", []))
        return all_cats
    except Exception:
        return []


def clear_all_logs() -> bool:
    """Delete all moderation logs from MongoDB."""
    col = get_collection()
    if col is None:
        return False
    try:
        col.delete_many({})
        return True
    except Exception:
        return False


def get_total_count() -> int:
    """Fast count of total documents."""
    col = get_collection()
    if col is None:
        return 0
    try:
        return col.count_documents({})
    except Exception:
        return 0
