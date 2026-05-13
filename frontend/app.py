"""
Syntra — Streamlit kurumsal paneli.
Backend şemaları: ProductRead (sku, name, stock_quantity, critical_limit, supplier_email), OrderRead.
"""
from __future__ import annotations

import streamlit as st

import api_client
from i18n import t
from styles import inject_global_styles
from views import (
    render_tab_ai,
    render_tab_inventory,
    render_tab_notifications,
    render_tab_operations,
)


def _init_session() -> None:
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("role", None)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("lang", "tr")
    st.session_state.setdefault("show_forgot_pw", False)


def _logout() -> None:
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = ""
    st.session_state.ai_messages = []
    st.session_state.parsed_records = None
    st.session_state.parse_warnings = []
    st.session_state.show_forgot_pw = False


def _toggle_lang_button(*, key: str) -> None:
    """Tek tıkla TR ↔ EN; combobox kullanılmaz."""
    lang = st.session_state.lang
    label = t(lang, "lang_btn_to_en") if lang == "tr" else t(lang, "lang_btn_to_tr")
    hint = t(lang, "lang_toggle_hint")
    if st.button(label, key=key, help=hint, use_container_width=True):
        st.session_state.lang = "en" if lang == "tr" else "tr"
        st.rerun()


@st.dialog("Syntra")
def forgot_password_dialog() -> None:
    """E-posta ile şifre sıfırlama — POST /api/auth/forgot-password."""
    lang = st.session_state.lang
    h1, h2 = st.columns([4, 1], vertical_alignment="center")
    with h1:
        st.markdown(f"### {t(lang, 'forgot_title')}")
    with h2:
        if st.button(t(lang, "forgot_close"), key="dlg_forgot_close", use_container_width=True):
            st.session_state.show_forgot_pw = False
            st.rerun()

    st.caption(t(lang, "forgot_caption"))
    st.caption(t(lang, "forgot_demo_hint"))

    with st.form("forgot_pw_dialog_form"):
        email = st.text_input(t(lang, "forgot_email"), autocomplete="email")
        submitted = st.form_submit_button(t(lang, "forgot_submit"), type="primary", use_container_width=True)

    if submitted:
        if not (email or "").strip():
            st.warning(t(lang, "forgot_invalid"))
        else:
            res = api_client.post_forgot_password(email.strip())
            oc = res.get("outcome")
            if oc == "sent":
                st.success(t(lang, "forgot_success_sent"))
            elif oc == "not_found":
                st.warning(t(lang, "forgot_not_found"))
            elif oc == "invalid":
                st.warning(t(lang, "forgot_invalid"))
            elif oc == "unavailable":
                st.error(t(lang, "forgot_unavailable"))
            else:
                st.error(t(lang, "forgot_error"))


def _try_login(username: str, password: str, role_choice: str) -> tuple[bool, str]:
    u = username.strip().lower()
    p = password.strip()
    if role_choice == t(st.session_state.lang, "role_admin"):
        if u == "admin" and p == "admin123":
            return True, "admin"
    if role_choice == t(st.session_state.lang, "role_customer"):
        if u == "user" and p == "user123":
            return True, "customer"
    return False, ""


def _render_login() -> None:
    lang = st.session_state.lang
    top_l, top_r = st.columns([3, 1.2], vertical_alignment="center")
    with top_l:
        st.markdown(f"### ⚡ {t(lang, 'app_title')}")
    with top_r:
        _toggle_lang_button(key="login_lang_btn")

    lang = st.session_state.lang
    submitted = False
    user, pwd, role_label = "", "", t(lang, "role_admin")
    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        with st.container(border=True):
            st.markdown(f"### {t(lang, 'login_title')}")
            st.info(t(lang, "login_demo_hint"))
            with st.form("corp_login", clear_on_submit=False):
                user = st.text_input(t(lang, "username"))
                pwd = st.text_input(t(lang, "password"), type="password")
                role_label = st.radio(
                    t(lang, "role"),
                    [t(lang, "role_admin"), t(lang, "role_customer")],
                    horizontal=True,
                )
                submitted = st.form_submit_button(
                    t(lang, "login_btn"), type="primary", use_container_width=True
                )
        if st.button(
            t(lang, "forgot_password_link"),
            key="btn_forgot_pw_open",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.show_forgot_pw = True
            st.rerun()

    if st.session_state.get("show_forgot_pw"):
        forgot_password_dialog()

    if submitted:
        ok, role = _try_login(user, pwd, role_label)
        if ok:
            st.session_state.authenticated = True
            st.session_state.role = role
            st.session_state.username = user.strip()
            st.rerun()
        else:
            st.error(t(lang, "login_error"))


def _render_header() -> None:
    lang = st.session_state.lang
    with st.container():
        left, mid, right = st.columns([4.2, 1.15, 1.15], vertical_alignment="center")
        with left:
            st.markdown(
                f"""
<div class="syntra-header-slot">
  <div class="syntra-brand">
    <div class="syntra-logo" aria-hidden="true">⚡</div>
    <div class="syntra-titles">
      <p class="syntra-title">{t(lang, "app_title")}</p>
      <p class="syntra-sub">{t(lang, "header_tagline")}</p>
    </div>
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )
        with mid:
            _toggle_lang_button(key="hdr_lang_btn")
        with right:
            if st.button(t(lang, "logout"), key="hdr_logout", use_container_width=True):
                _logout()
                st.rerun()


def _render_main_tabs() -> None:
    lang = st.session_state.lang
    role = st.session_state.role

    if role == "admin":
        tab_ops, tab_inv, tab_ai, tab_notif = st.tabs(
            [
                t(lang, "tab_ops"),
                t(lang, "tab_inv"),
                t(lang, "tab_ai"),
                t(lang, "tab_notif"),
            ]
        )
        with tab_ops:
            render_tab_operations(lang)
        with tab_inv:
            render_tab_inventory(lang, role)
        with tab_ai:
            render_tab_ai(lang)
        with tab_notif:
            render_tab_notifications(lang)
    else:
        tab_ops, tab_ai, tab_notif = st.tabs(
            [
                t(lang, "tab_ops"),
                t(lang, "tab_ai"),
                t(lang, "tab_notif"),
            ]
        )
        with tab_ops:
            render_tab_operations(lang)
        with tab_ai:
            render_tab_ai(lang)
        with tab_notif:
            render_tab_notifications(lang)


def main() -> None:
    st.set_page_config(
        page_title="Syntra OS",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    _init_session()
    inject_global_styles()

    if not st.session_state.authenticated:
        _render_login()
        return

    _render_header()

    lang = st.session_state.lang
    role_key = "role_admin" if st.session_state.role == "admin" else "role_customer"
    try:
        h = api_client.health()
        status = h.get("status", h.get("durum", "—"))
        api_line = f"{t(lang, 'api_status')}: {status}"
    except Exception:
        api_line = t(lang, "backend_fail")

    st.caption(f"{st.session_state.username} · {t(lang, role_key)} · {api_line}")

    _render_main_tabs()


if __name__ == "__main__":
    main()
