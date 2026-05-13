"""Sayfa akışında üst header; position: fixed yok."""

import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
<style>
  /* Genel tipografi */
  html, body, [class*="css"]  {
    font-feature-settings: "kern" 1, "liga" 1;
  }
  .syntra-header-slot {
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.35rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0f172a 100%);
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.35);
  }
  .syntra-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    min-width: 0;
  }
  .syntra-logo {
    font-size: 1.75rem;
    line-height: 1;
  }
  .syntra-titles {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.1rem;
    min-width: 0;
  }
  .syntra-title {
    color: #f8fafc;
    font-weight: 700;
    font-size: 1.2rem;
    letter-spacing: 0.02em;
    margin: 0;
    line-height: 1.2;
  }
  .syntra-sub {
    color: #94a3b8;
    font-size: 0.78rem;
    margin: 0;
    line-height: 1.2;
  }
  div[data-testid="stTabs"] button {
    font-weight: 600;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


