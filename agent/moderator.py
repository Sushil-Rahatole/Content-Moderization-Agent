import json
from groq import Groq
from config.settings import GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS, HARMFUL_CATEGORIES, THRESHOLD_ALLOW, THRESHOLD_REVIEW


def get_verdict(risk_score: int) -> str:
    if risk_score < THRESHOLD_ALLOW:
        return "ALLOW"
    elif risk_score < THRESHOLD_REVIEW:
        return "REVIEW"
    return "BLOCK"


def _parse_response(raw: str) -> dict:
    """Strip markdown fences and parse JSON."""
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _build_system_prompt(policy_context: str = "") -> str:
    policy_line = f"\nPLATFORM POLICY: {policy_context}" if policy_context else ""
    return f"""You are an AI Content Moderation Agent for a real-world platform.{policy_line}

Respond ONLY in this exact JSON format — no extra text, no markdown:
{{
  "risk_score": <integer 0-100>,
  "flagged_categories": ["<violated categories only>"],
  "safe_categories": ["<clean categories>"],
  "reasoning": "<2-3 sentence professional explanation>",
  "suggestions": "<one actionable rewrite suggestion or 'Content is acceptable as-is.'>",
  "confidence": "<HIGH or MEDIUM or LOW>",
  "appeal_hint": "<one sentence on what context might reduce the risk score if appealed>"
}}

Risk Score: 0-10 completely safe | 11-39 mostly safe | 40-69 borderline | 70-89 harmful | 90-100 extremely harmful
Categories: {', '.join(HARMFUL_CATEGORIES)}
Be fair. Normal text scores 0-20. Political opinions and criticism are NOT automatically harmful."""


def analyze_text(api_key: str, text: str, policy_context: str = "") -> dict:
    """Analyze a single piece of text."""
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": _build_system_prompt(policy_context)},
            {"role": "user",   "content": f"Moderate this text:\n\n{text}"}
        ],
        temperature=GROQ_TEMPERATURE,
        max_tokens=GROQ_MAX_TOKENS,
    )
    result = _parse_response(response.choices[0].message.content)
    result["verdict"] = get_verdict(result["risk_score"])
    return result


def analyze_appeal(api_key: str, text: str, original_result: dict, appeal_reason: str) -> dict:
    """Re-analyze text with user-provided appeal context."""
    client = Groq(api_key=api_key)
    context = f"""Original verdict: {original_result['verdict']} (score: {original_result['risk_score']})
Original reasoning: {original_result['reasoning']}
User appeal reason: {appeal_reason}

Re-evaluate fairly considering the appeal context. If the appeal is valid, lower the score."""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user",   "content": f"APPEAL REQUEST:\n{context}\n\nOriginal text:\n{text}"}
        ],
        temperature=0.2,
        max_tokens=GROQ_MAX_TOKENS,
    )
    result = _parse_response(response.choices[0].message.content)
    result["verdict"] = get_verdict(result["risk_score"])
    result["is_appeal"] = True
    return result


def analyze_url_content(api_key: str, url_text: str, url: str) -> dict:
    """Moderate scraped content from a URL."""
    client = Groq(api_key=api_key)
    truncated = url_text[:3000]
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user",   "content": f"Moderate this webpage content from {url}:\n\n{truncated}"}
        ],
        temperature=GROQ_TEMPERATURE,
        max_tokens=GROQ_MAX_TOKENS,
    )
    result = _parse_response(response.choices[0].message.content)
    result["verdict"] = get_verdict(result["risk_score"])
    result["source_url"] = url
    return result