import streamlit as st
import requests
import pandas as pd

# Backend Adresimiz
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# 1. SAYFA AYARLARI VE MARKA KİMLİĞİ
st.set_page_config(
    page_title="Syntra OS | Operasyonel Zeka",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. YAN MENÜ (SIDEBAR) & JÜRİ DEMO MODU
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=50) # Temsili Logo
    st.title("SYNTRA OS")
    st.caption("KOBİ'ler İçin AI İşletim Sistemi")
    st.divider()
    
    # SENİN MAIN.PY'A EKLEDİĞİN HARİKA ÖZELLİK: DEMO SEED
    st.subheader("⚡ Jüri Demo Modu")
    st.write("Sistemi test verileriyle doldurun.")
    if st.button("Veritabanını Doldur (Seed)", type="primary", use_container_width=True):
        with st.spinner("Syntra örnek verilerle besleniyor..."):
            try:
                # Demo endpoint'ine istek atıyoruz
                resp = requests.post(f"{API_URL}/demo/seed")
                if resp.status_code in [200, 201]:
                    st.success("✅ Demo verileri başarıyla yüklendi!")
                    st.balloons()
                else:
                    st.error("Demo verisi yüklenemedi. Backend hatası.")
            except Exception as e:
                st.error("Backend'e ulaşılamıyor. Uvicorn çalışıyor mu?")
                
    st.divider()
    
    # System Health Check (Senin main.py'daki /health endpoint'i)
    if st.button("🔌 Sistem Durumu Kontrolü", use_container_width=True):
        try:
            health = requests.get(f"{BASE_URL}/health").json()
            st.success(f"Durum: {health['durum']} | Versiyon: {health['versiyon']}")
        except:
            st.error("Sistem Çevrimdışı!")

# 3. ANA EKRAN VE SEKMELER
st.header("Syntra Yönetim Paneli")

# Senin main.py'da belirlediğin tags_metadata'ya göre sekmeleri kurduk:
tab_operasyon, tab_envanter, tab_ai, tab_bildirim = st.tabs([
    "📊 Operasyon Özeti", 
    "📦 Envanter & Excel", 
    "🧠 AI Asistan", 
    "📱 Bildirimler"
])

# --- SEKME 1: OPERASYON ÖZETİ ---
with tab_operasyon:
    st.subheader("Anlık Operasyon Durumu")
    st.write("Stok ve sipariş durumunuzun tek bakışta özeti.")
    
    # Jüriye hoş görünmesi için temsili KPI kartları (Görsel amaçlı)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Toplam Sipariş", value="124", delta="+12 Bugün")
    col2.metric(label="Aktif Ürün Çeşidi", value="45", delta="-3 Kritik Stok", delta_color="inverse")
    col3.metric(label="Sistem Sağlığı", value="%100", delta="Senkronize")

# --- SEKME 2: ENVANTER & EXCEL ---
with tab_envanter:
    st.subheader("Toplu Ürün Yönetimi")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Adım 1: Syntra'ya veri yüklemek için standart şablonu indirin.")
        if st.button("⬇️ Şablon İndir", use_container_width=True):
            try:
                # Not: Endpoint adın farklıysa burayı güncelleyebilirsin (Örn: /excel/download)
                response = requests.get(f"{API_URL}/download-template")
                if response.status_code == 200:
                    st.download_button(
                        label="📥 Excel'i Kaydet",
                        data=response.content,
                        file_name="syntra_sablon.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except:
                st.error("Bağlantı hatası.")

    with col2:
        st.info("Adım 2: Doldurduğunuz şablonu yükleyerek stoklarınızı güncelleyin.")
        uploaded_file = st.file_uploader("Excel Dosyası Seçin", type=["xlsx", "xls"], label_visibility="collapsed")
        
        if st.button("🚀 Sisteme Yükle", type="primary", use_container_width=True):
            if uploaded_file:
                with st.spinner("Syntra verileri okuyor..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    try:
                        resp = requests.post(f"{API_URL}/upload-products", files=files)
                        if resp.status_code == 200:
                            st.success("Veriler başarıyla senkronize edildi.")
                        else:
                            st.error(f"Hata: {resp.status_code}")
                    except:
                        st.error("Backend'e ulaşılamıyor.")
            else:
                st.warning("Önce dosya seçmelisiniz.")

# --- SEKME 3: YAPAY ZEKA ---
with tab_ai:
    st.subheader("Kritik Stok Analizi ve İletişim")
    st.write("Syntra, stoğu azalan ürünleri tespit eder ve tedarikçiniz için e-posta taslağı üretir.")
    
    if st.button("🔍 AI Stok Analizini Başlat", type="primary"):
        with st.spinner("Gemini Flash veritabanını tarıyor..."):
            try:
                resp = requests.get(f"{API_URL}/ai/stock-alerts")
                if resp.status_code == 200:
                    alerts = resp.json().get("alerts", [])
                    if not alerts:
                        st.success("Tüm stoklar güvenli seviyede.")
                    else:
                        st.warning(f"{len(alerts)} ürün kritik seviyede!")
                        for alert in alerts:
                            with st.expander(f"📉 {alert['product']} (Kalan: {alert['current_stock']})"):
                                st.write("**Yapay Zeka E-Posta Taslağı:**")
                                st.code(alert['ai_suggestion'], language="markdown")
            except:
                st.error("AI servisine bağlanılamadı.")

# --- SEKME 4: BİLDİRİMLER (Main.py'daki yeni etiket için) ---
with tab_bildirim:
    st.subheader("Çok Kanallı Bildirim Yönetimi")
    st.write("Sipariş ve stok durumlarını ilgili kanallara otomatik iletin.")
    
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        st.button("📧 E-Posta Gönder", disabled=True, use_container_width=True)
    with b_col2:
        st.button("💬 WhatsApp Mesajı Tetikle", disabled=True, use_container_width=True)
    with b_col3:
        st.button("✈️ Telegram Bildirimi At", disabled=True, use_container_width=True)
    
    st.caption("Not: Bu modül Syntra'nın Faz-2 planlamasında aktif edilecektir.")
