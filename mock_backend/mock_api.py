"""Stand-in for the BitGuard /validate API (same response shape as the real one).
Returns deterministic demo data derived from the address, so no model/Neo4j needed."""
import hashlib
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Req(BaseModel):
    seed_parameter: str

LOW = [
    ("Long wallet history", "decreases_risk", "This wallet has been active for a long time, which is typical of legitimate use."),
    ("Few links to flagged wallets", "decreases_risk", "Very little of this wallet's activity connects to wallets with a risky history."),
    ("Regular, steady transaction pattern", "decreases_risk", "Transactions follow an ordinary pattern rather than bursts of rapid movement."),
]
HIGH = [
    ("Rapid pass-through of funds", "increases_risk", "Funds arrive and leave quickly, a pattern often seen in laundering."),
    ("Connected to many high-risk wallets", "increases_risk", "This wallet transacts closely with wallets that have a risky history."),
    ("Many new counterparties in a short time", "increases_risk", "A large number of new wallets interacted with this one in a short window."),
]

@app.post("/validate")
async def validate(r: Req):
    a = r.seed_parameter.strip()
    h = int(hashlib.sha256(a.encode()).hexdigest(), 16)
    score = (h % 1000) / 1000 * 0.9 + 0.005
    if score >= 0.6: risk = "very_high"
    elif score >= 0.5: risk = "high"
    elif score >= 0.1: risk = "mixed_signal"
    elif score >= 0.01: risk = "low"
    else: risk = "very_low"
    reasons_src = HIGH if risk in ("high", "very_high") else LOW
    reasons = [{"feature": n, "display_name": n, "shap_explanation": e, "shap_value": 0.1,
                "direction": d, "feature_value": 1.0, "influence_pct": 40 - i * 10}
               for i, (n, d, e) in enumerate(reasons_src)]
    first = 300000 + h % 300000
    return {
        "bitcoin_wallet": a, "top_reasons": reasons,
        "btc_sent": round((h % 5000) / 100, 8), "btc_received": round((h % 5200) / 100 + 0.5, 8),
        "total_txs_analyzed": 20 + h % 400, "total_wallets_analyzed": 10 + h % 200,
        "first_active_block": first, "last_active_block": first + 1000 + h % 200000,
        "risk_probability": risk, "risk_score": score,
    }
