"""
Excel → ürün satırları (app.schemas.ProductCreate / models.Product ile uyumlu sütunlar).
"""
from __future__ import annotations

import io
from typing import Any

import pandas as pd

# Şablon ve dosyada kabul edilen sütun adları (TR / EN varyantları)
COLUMN_ALIASES: dict[str, list[str]] = {
    "sku": ["sku", "SKU", "ürün kodu", "urun kodu", "stok kodu"],
    "name": ["name", "ad", "ürün adı", "urun adi", "product_name", "ürün"],
    "stock_quantity": ["stock_quantity", "stok", "stok miktarı", "miktar", "qty", "quantity"],
    "critical_limit": ["critical_limit", "kritik limit", "kritik", "min stok", "minimum"],
    "supplier_email": ["supplier_email", "tedarikçi", "tedarikci", "email", "e-posta", "eposta"],
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    rename: dict[str, str] = {}
    lower_map = {str(c).strip().lower(): c for c in out.columns}

    for canonical, variants in COLUMN_ALIASES.items():
        for v in variants:
            key = str(v).strip().lower()
            if key in lower_map:
                rename[lower_map[key]] = canonical
                break

    return out.rename(columns=rename)


def parse_excel_products(file_bytes: bytes, filename: str) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Excel içeriğini okuyup API'ye gönderilecek dict listesine çevirir.

    Returns:
        (records, warnings): records ProductCreate uyumlu; warnings boş değilse kullanıcıya göster.
    """
    warnings: list[str] = []
    bio = io.BytesIO(file_bytes)
    try:
        if not filename.lower().endswith((".xlsx", ".xlsm", ".xls")):
            raise ValueError("Yalnızca .xlsx / .xlsm / .xls desteklenir (tercihen .xlsx).")
        df = pd.read_excel(bio, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Excel okunamadı: {e}") from e

    if df.empty:
        raise ValueError("Dosya boş veya veri satırı yok.")

    df = _normalize_columns(df)

    required = {"sku", "name", "stock_quantity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            "Zorunlu sütunlar eksik: "
            + ", ".join(sorted(missing))
            + ". Beklenen: sku, name, stock_quantity; isteğe bağlı: critical_limit, supplier_email"
        )

    if "critical_limit" not in df.columns:
        df["critical_limit"] = 10
    if "supplier_email" not in df.columns:
        df["supplier_email"] = None

    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)
    df["critical_limit"] = pd.to_numeric(df["critical_limit"], errors="coerce").fillna(10).astype(int)

    df["sku"] = df["sku"].astype(str).str.strip()
    df["name"] = df["name"].astype(str).str.strip()
    df["supplier_email"] = df["supplier_email"].apply(
        lambda x: None if pd.isna(x) or str(x).strip() == "" else str(x).strip()
    )

    dup = df["sku"].duplicated()
    if dup.any():
        warnings.append(f"{int(dup.sum())} tekrarlayan SKU satırı atlandı (ilk kayıt tutuldu).")
        df = df.drop_duplicates(subset=["sku"], keep="first")

    records: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        if not row["sku"] or not row["name"]:
            continue
        rec = {
            "sku": row["sku"],
            "name": row["name"],
            "stock_quantity": max(0, int(row["stock_quantity"])),
            "critical_limit": max(0, int(row["critical_limit"])),
            "supplier_email": row["supplier_email"],
        }
        records.append(rec)

    if not records:
        raise ValueError("Geçerli ürün satırı üretilemedi.")

    return records, warnings


def records_to_preview_df(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Streamlit dataframe önizlemesi için."""
    return pd.DataFrame(records)
