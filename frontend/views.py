"""Sekme içerikleri — app.py'den ayrı modül."""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

import api_client
from api_client import APIError
from data_loader import parse_excel_products, records_to_preview_df
from i18n import t


def _products_df(products: list[dict[str, Any]]) -> pd.DataFrame:
    if not products:
        return pd.DataFrame(
            columns=["id", "sku", "name", "stock_quantity", "critical_limit", "supplier_email"]
        )
    return pd.DataFrame(products)


def _critical_alerts_from_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in products:
        try:
            stock = int(p.get("stock_quantity", 0))
            limit = int(p.get("critical_limit", 0))
        except (TypeError, ValueError):
            continue
        if stock <= limit:
            out.append(
                {
                    "product": p.get("name") or p.get("sku"),
                    "sku": p.get("sku"),
                    "current_stock": stock,
                    "critical_limit": limit,
                }
            )
    return out


def render_tab_operations(lang: str) -> None:
    st.subheader(t(lang, "tab_ops"))
    try:
        products = api_client.get_products()
        orders = api_client.get_orders()
    except Exception as e:
        st.warning(f"{t(lang, 'backend_fail')}: {e}")
        products, orders = [], []

    n_orders = len(orders)
    n_skus = len(products)
    crit = len(_critical_alerts_from_products(products))

    m1, m2, m3 = st.columns(3)
    m1.metric(t(lang, "metrics_orders"), n_orders)
    m2.metric(t(lang, "metrics_products"), n_skus)
    m3.metric(t(lang, "metrics_critical"), crit, delta_color="inverse")

    st.divider()
    st.caption(t(lang, "chart_stock_title"))
    df = _products_df(products)
    if df.empty or "name" not in df.columns or "stock_quantity" not in df.columns:
        st.info("—")
    else:
        chart_df = df.nlargest(8, "stock_quantity")[["name", "stock_quantity"]].set_index("name")
        st.bar_chart(chart_df)


def render_tab_inventory(lang: str, role: str) -> None:
    st.subheader(t(lang, "tab_inv"))
    is_admin = role == "admin"

    c_seed, c_reset, c_ref = st.columns([1, 1, 2], vertical_alignment="center")
    with c_seed:
        if st.button(t(lang, "seed"), disabled=not is_admin, use_container_width=True):
            try:
                api_client.post_demo_seed()
                st.success("OK")
                st.rerun()
            except APIError as e:
                st.error(str(e))
            except Exception as e:
                st.error(str(e))
    with c_reset:
        if st.button(t(lang, "reset"), disabled=not is_admin, use_container_width=True):
            try:
                api_client.post_demo_reset()
                st.success("OK")
                st.rerun()
            except APIError as e:
                st.error(str(e))
            except Exception as e:
                st.error(str(e))
    with c_ref:
        if st.button(t(lang, "refresh"), use_container_width=True):
            st.rerun()

    try:
        products = api_client.get_products()
    except Exception as e:
        st.error(f"{t(lang, 'backend_fail')}: {e}")
        products = []

    st.markdown(f"**{t(lang, 'inv_list')}**")
    st.dataframe(_products_df(products), use_container_width=True, hide_index=True)

    st.markdown(f"**{t(lang, 'inv_upload')}**")
    if not is_admin:
        st.info(t(lang, "admin_only_upload"))
        return

    up = st.file_uploader("Excel", type=["xlsx", "xlsm"], label_visibility="collapsed")
    if "parsed_records" not in st.session_state:
        st.session_state.parsed_records = None
        st.session_state.parse_warnings = []

    if up is not None:
        raw = up.getvalue()
        if st.button(t(lang, "inv_parse"), type="secondary"):
            try:
                recs, warns = parse_excel_products(raw, up.name)
                st.session_state.parsed_records = recs
                st.session_state.parse_warnings = warns
            except ValueError as e:
                st.error(str(e))
                st.session_state.parsed_records = None

    if st.session_state.parsed_records:
        for w in st.session_state.parse_warnings:
            st.warning(w)
        st.dataframe(records_to_preview_df(st.session_state.parsed_records), use_container_width=True)
        if st.button(t(lang, "inv_send"), type="primary"):
            try:
                api_client.post_products_import(st.session_state.parsed_records)
                st.success("OK")
                st.session_state.parsed_records = None
                st.session_state.parse_warnings = []
                st.rerun()
            except APIError as e:
                st.error(str(e))
            except Exception as e:
                st.error(str(e))


def render_tab_ai(lang: str) -> None:
    st.subheader(t(lang, "tab_ai"))
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    if not st.session_state.ai_messages:
        st.caption(t(lang, "ai_empty"))

    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(t(lang, "ai_placeholder"))
    if prompt:
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        try:
            reply = api_client.post_ai_chat(st.session_state.ai_messages)
            st.session_state.ai_messages.append({"role": "assistant", "content": reply})
        except APIError as e:
            st.session_state.ai_messages.append(
                {"role": "assistant", "content": f"*{e}*"}
            )
        except Exception as e:
            st.session_state.ai_messages.append(
                {"role": "assistant", "content": f"*Hata: {e}*"}
            )
        st.rerun()


def render_tab_notifications(lang: str) -> None:
    st.subheader(t(lang, "tab_notif"))
    try:
        products = api_client.get_products()
    except Exception as e:
        st.error(f"{t(lang, 'backend_fail')}: {e}")
        products = []

    alerts: Optional[list] = None
    try:
        alerts = api_client.get_stock_alerts()
    except APIError:
        alerts = None
    except Exception:
        alerts = None

    if alerts is None or len(alerts) == 0:
        alerts = _critical_alerts_from_products(products)

    if not alerts:
        st.success(t(lang, "notif_none"))
        return

    for a in alerts:
        title = a.get("product") or a.get("name") or a.get("sku") or "—"
        stock = a.get("current_stock", a.get("stock_quantity", "—"))
        with st.expander(f"⚠ {title} — stock: {stock}", expanded=False):
            if "ai_suggestion" in a:
                st.markdown(a["ai_suggestion"])
            else:
                st.json(a)
