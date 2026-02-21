
APP_TITLE   = "ContentGuard AI — Moderation Agent"
APP_ICON    = "🛡️"
APP_VERSION = "2.0.0"

GROQ_MODEL       = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.1
GROQ_MAX_TOKENS  = 800

THRESHOLD_ALLOW  = 40
THRESHOLD_REVIEW = 70

HARMFUL_CATEGORIES = [
    "Hate Speech", "Violence", "Sexual Content", "Self-Harm",
    "Harassment", "Misinformation", "Illegal Activity", "Spam / Scam",
]

PLATFORM_POLICIES = {
    "🌐 General Platform":    "Standard moderation. Flag obvious hate speech, violence, illegal content.",
    "👶 Kids / Family App":   "Very strict. Block any adult themes, mild violence, suggestive language.",
    "🎮 Gaming Community":    "Moderate. Allow competitive trash-talk but block slurs and threats.",
    "📰 News / Discussion":   "Lenient. Allow political debate and strong opinions. Block incitement only.",
    "🏥 Healthcare Platform": "Strict on self-harm. Allow medical discussions but flag dangerous advice.",
    "🛒 E-commerce":          "Block spam, scam, fake reviews. Allow product criticism.",
}

VERDICTS = {
    "ALLOW":  {"emoji": "✅", "color": "#22c55e", "bg": "#0d2e1a", "border": "#22c55e"},
    "REVIEW": {"emoji": "⚠️", "color": "#f59e0b", "bg": "#2e2200", "border": "#f59e0b"},
    "BLOCK":  {"emoji": "🚫", "color": "#ef4444", "bg": "#2e0d0d", "border": "#ef4444"},
}

SAMPLE_PROMPTS = {
    "🟢 Safe":       "I love coding and building AI projects with my friends. Today was so productive!",
    "🟡 Borderline": "This politician is completely corrupt and should face serious consequences for their actions.",
    "🔴 Harmful":    "I hate people from that group. They are subhuman and do not deserve to live among us.",
}

EXPORT_COLUMNS = ["timestamp", "text", "risk_score", "verdict", "flagged_categories", "reasoning"]