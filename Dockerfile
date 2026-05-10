# 1. Adım: Temel Malzeme
# Projemizi çalıştırmak için hafif ve güvenli bir Python 3.12 imajı seçiyoruz.
FROM python:3.12-slim

# 2. Adım: Çalışma Alanı
# Konteynerin (sanal kutunun) içinde kodlarımızın duracağı bir 'code' klasörü oluşturuyoruz.
WORKDIR /code

# 3. Adım: Gerekli Aletleri Kurma
# Kütüphanelerimizin (özellikle veritabanı sürücüsü 'asyncpg') sorunsuz kurulabilmesi için
# gereken bazı sistem araçlarını Linux'un içine kuruyoruz.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Adım: Alışveriş Listesini Kopyalama ve Kurma
# Önce sadece 'requirements.txt' dosyasını kopyalayıp kuruyoruz.
# Docker bu adımı hafızasına alır ve kütüphaneler değişmediği sürece tekrar kurmaz, hız kazanırız.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Adım: Asıl Kodları Kopyalama
# Şimdi kendi yazdığımız 'app' klasörünü konteynerin içine kopyalıyoruz.
COPY ./app /code/app

# 6. Adım: Sağlık Kontrolü
# Docker'a, her 30 saniyede bir uygulamamızın 'yaşıyor' olup olmadığını kontrol etmesini söylüyoruz.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 7. Adım: Motoru Çalıştırma
# Konteyner başladığında, FastAPI sunucusunu başlatacak olan komutu buraya yazıyoruz.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]