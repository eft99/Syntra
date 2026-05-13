"""
Backend REST çağrıları — main.py genişledikçe uçlar burada toplanır.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import requests

BASE_URL = os.environ.get("SYNTRA_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_PREFIX = f"{BASE_URL}/api"
DEFAULT_TIMEOUT = 30


class APIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def health() -> dict[str, Any]:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    r.raise_for_status()
    return r.json()


def get_products() -> list[dict[str, Any]]:
    """GET /api/products — liste veya {items:[]} sarmalayıcısı."""
    r = requests.get(f"{API_PREFIX}/products", timeout=DEFAULT_TIMEOUT)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "items" in data:
        return list(data["items"])
    if isinstance(data, dict) and "products" in data:
        return list(data["products"])
    return []


def post_demo_seed() -> dict[str, Any]:
    # Seed endpoint is POST /api/demo/seed
    r = requests.post(f"{API_PREFIX}/demo/seed", timeout=DEFAULT_TIMEOUT)
    if r.status_code not in (200, 201):
        raise APIError(r.text or "Seed başarısız", r.status_code)
    try:
        return r.json()
    except Exception:
        return {"ok": True, "detail": r.text}


def post_demo_reset() -> dict[str, Any]:
    # Reset endpoint is DELETE /api/demo/reset?onayla=evet
    r = requests.delete(f"{API_PREFIX}/demo/reset", params={"onayla": "evet"}, timeout=DEFAULT_TIMEOUT)
    if r.status_code not in (200, 201):
        raise APIError(r.text or "Reset başarısız", r.status_code)
    try:
        return r.json()
    except Exception:
        return {"ok": True}


def post_products_import(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Toplu içe aktarma — Backend'de /api/products (POST) veya /api/upload-products (Excel) var.
    Burada JSON listesi gönderiyoruz, bu yüzden /api/products endpoint'ine döngüyle veya toplu (varsa) atılmalı.
    Şu anki endpoints.py'de toplu JSON importu yok, sadece tekil /api/products POST var.
    Demo için /api/demo/seed kullanılması önerilir.
    """
    # Eğer backend'de toplu import ucu yoksa hata verelim veya tek tek gönderelim.
    # Mevcut endpoints.py'de @router.post("/products") tekil ürün alır.
    errors = []
    for rec in records:
        r = requests.post(f"{API_PREFIX}/products", json=rec, timeout=DEFAULT_TIMEOUT)
        if r.status_code >= 400:
            errors.append(f"{rec.get('sku')}: {r.text}")
    
    if errors:
        raise APIError("Bazı ürünler yüklenemedi: " + "; ".join(errors[:3]))
    
    return {"ok": True}


def get_orders() -> list[dict[str, Any]]:
    r = requests.get(f"{API_PREFIX}/orders", timeout=DEFAULT_TIMEOUT)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "items" in data:
        return list(data["items"])
    return []


def post_ai_chat(messages: list[dict[str, str]], context: Optional[str] = None) -> str:
    """POST /api/ai/chat — {messages, context?}"""
    body: dict[str, Any] = {"messages": messages}
    if context:
        body["context"] = context
    r = requests.post(f"{API_PREFIX}/ai/chat", json=body, timeout=60)
    if r.status_code == 404:
        raise APIError("AI sohbet ucu henüz backend'de yok (/api/ai/chat).", 404)
    if r.status_code >= 400:
        raise APIError(r.text or "AI hatası", r.status_code)
    data = r.json()
    if isinstance(data, dict) and "reply" in data:
        return str(data["reply"])
    if isinstance(data, dict) and "message" in data:
        return str(data["message"])
    return str(data)


def get_stock_alerts() -> list[dict[str, Any]]:
    """GET /api/ai/stock-alerts veya client-side filtre için ürün listesi."""
    r = requests.get(f"{API_PREFIX}/ai/stock-alerts", timeout=60)
    if r.status_code == 404:
        return []
    if r.status_code >= 400:
        raise APIError(r.text or "Uyarılar alınamadı", r.status_code)
    data = r.json()
    if isinstance(data, dict) and "alerts" in data:
        return list(data["alerts"])
    if isinstance(data, list):
        return data
    return []


def post_forgot_password(email: str) -> dict[str, Any]:
    """
    POST /api/auth/forgot-password — gövde: {"email": "..."}
    Dönüş: {"outcome": "sent"|"not_found"|"invalid"|"unavailable"|"error", "detail": ...?}
    """
    try:
        r = requests.post(
            f"{API_PREFIX}/auth/forgot-password",
            json={"email": email},
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException:
        return {"outcome": "unavailable"}

    try:
        data = r.json() if r.content else {}
    except Exception:
        data = {}

    if r.status_code == 404:
        return {"outcome": "unavailable"}

    if r.status_code == 422:
        return {"outcome": "invalid", "detail": data}

    if r.status_code >= 500:
        return {"outcome": "error", "detail": r.text}

    if r.status_code == 200:
        if data.get("sent") is True:
            return {"outcome": "sent"}
        return {"outcome": "not_found"}

    return {"outcome": "error", "detail": r.text}
