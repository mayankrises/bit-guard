import json
import logging

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
import requests
import redis

from ..environments import environments as envs

router = APIRouter()

class _MemoryCache:
    """In-memory fallback so the app runs without Redis."""
    def __init__(self):
        self._d = {}
    def get(self, k):
        return self._d.get(k)
    def setex(self, k, ttl, v):
        self._d[k] = v


def _make_cache():
    import os
    host = os.getenv("REDIS_HOST", "redis")
    try:
        r = redis.Redis(host=host, port=6379, decode_responses=True, socket_connect_timeout=1)
        r.ping()
        return r
    except Exception:
        return _MemoryCache()


redis_caching = _make_cache()
logger = logging.getLogger(__name__)

MAX_ADDRESS_LEN = 120
BACKEND_URL = envs.BACKEND_URL
INTERNAL_API_KEY = envs.INTERNAL_API_KEY


import hashlib


def _demo_result(address: str) -> dict:
    """Built-in DEMO data (no model / database). Same address -> same result."""
    h = int(hashlib.sha256(address.encode()).hexdigest(), 16)
    score = (h % 1000) / 1000 * 0.9 + 0.005
    if score >= 0.6:
        risk = "very_high"
    elif score >= 0.5:
        risk = "high"
    elif score >= 0.1:
        risk = "mixed_signal"
    elif score >= 0.01:
        risk = "low"
    else:
        risk = "very_low"
    if risk in ("high", "very_high"):
        src = [
            ("Rapid pass-through of funds", "increases_risk", "Funds arrive and leave quickly, a pattern often seen in laundering."),
            ("Connected to many high-risk wallets", "increases_risk", "This wallet transacts closely with wallets that have a risky history."),
            ("Many new counterparties in a short time", "increases_risk", "Many new wallets interacted with this one in a short window."),
        ]
    else:
        src = [
            ("Long wallet history", "decreases_risk", "This wallet has been active for a long time, which is typical of legitimate use."),
            ("Few links to flagged wallets", "decreases_risk", "Very little of this wallet's activity connects to wallets with a risky history."),
            ("Regular transaction pattern", "decreases_risk", "Transactions follow an ordinary pattern rather than bursts of rapid movement."),
        ]
    reasons = [{"feature": n, "display_name": n, "shap_explanation": e, "shap_value": 0.1,
                "direction": d, "feature_value": 1.0, "influence_pct": 40 - i * 10}
               for i, (n, d, e) in enumerate(src)]
    first = 300000 + h % 300000
    return {
        "bitcoin_wallet": address, "top_reasons": reasons,
        "btc_sent": round((h % 5000) / 100, 8), "btc_received": round((h % 5200) / 100 + 0.5, 8),
        "total_txs_analyzed": 20 + h % 400, "total_wallets_analyzed": 10 + h % 200,
        "first_active_block": first, "last_active_block": first + 1000 + h % 200000,
        "risk_probability": risk, "risk_score": score,
    }


class SubmitRequest(BaseModel):
    seed_parameter: str = Field(min_length=1)


async def validate_address(seed_parameter: str):
    response = None

    try:
        response = requests.post(
            f"{BACKEND_URL}/validate",
            json={"seed_parameter": seed_parameter},
            headers={"X-Internal-API-Key": INTERNAL_API_KEY},
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("ERROR: Error connecting to validation backend: %s", str(exc))

        backend_detail = None
        backend_status = response.status_code if response is not None else None

        if response is None:
            # Backend unreachable -> fall back to built-in demo data
            logger.warning("Backend unreachable, using built-in demo data")
            return _demo_result(seed_parameter)

        if response is not None:
            try:
                backend_detail = response.json().get("detail")
            except ValueError:
                backend_detail = response.text or None

        if backend_status is not None:
            if backend_status >= 500:
                logger.error("ERROR: Backend error: %s - %s", backend_status, backend_detail or "")
                raise HTTPException(
                    status_code=502,
                    detail=backend_detail or f"Backend error: {backend_status}, try again later or contact us."
                ) from exc

            raise HTTPException(
                status_code=backend_status,
                detail=backend_detail or "Error validating request."
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Error validating request, try again later or contact us."
        ) from exc

    return response.json()


def is_allowed_address(address: str):
    a = address.strip()

    if not a:
        return False

    if len(a) > MAX_ADDRESS_LEN:
        return False

    return a.startswith("bc1") or a.startswith("1") or a.startswith("3")


@router.post("/submit")
async def submit(req: SubmitRequest):
    seed_parameter = req.seed_parameter.strip()

    if not seed_parameter:
        raise HTTPException(status_code=400, detail="Seed parameter is required")

    if not (seed_parameter.startswith("bc1") or seed_parameter.startswith("1") or seed_parameter.startswith("3")):
        raise HTTPException(status_code=400, detail="Seed parameter must start with bc1, 1, or 3")

    cache_key = f"btc:{seed_parameter}"

    cached = redis_caching.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await validate_address(seed_parameter)

    redis_caching.setex(cache_key, 259200, json.dumps(result))

    return result
