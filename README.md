# 🚀 Syntra

> **Operations, Synchronized by AI.**

AI destekli modern operasyon yönetim platformu.  
Syntra; KOBİ’lerin stok, sipariş, operasyon, tedarik ve müşteri süreçlerini merkezi, ölçeklenebilir ve akıllı bir sistem altında birleştirmek için geliştirilmiştir.

**Takım / GitHub:** Repoyu klonladıktan sonra kurulum, `.env`, Docker ve demo giriş bilgileri için **[SETUP.md](SETUP.md)** dosyasına bakın.

---

# 📌 Proje Hakkında

Küçük ve orta ölçekli işletmeler günlük operasyonlarını çoğunlukla:

- Excel tabloları
- WhatsApp mesajları
- Telefon görüşmeleri
- Manuel stok kontrolleri
- Dağınık sipariş süreçleri

üzerinden yönetmektedir.

Bu yapı:

- operasyonel verimsizlik,
- insan kaynaklı hata,
- stok kayıpları,
- geciken sipariş süreçleri,
- müşteri memnuniyetsizliği,
- ölçeklenme problemleri

oluşturmaktadır.

Syntra, bu manuel operasyon süreçlerini yapay zeka destekli otomasyon sistemleri ile dijitalleştirerek:

- operasyonel görünürlük,
- süreç otomasyonu,
- karar destek mekanizmaları,
- AI tabanlı aksiyon üretimi

sağlamayı hedeflemektedir.

---

# 🧠 Syntra İsmi Nereden Geliyor?

**Syntra** ismi:

- **Synchronization**
- **System**
- **Infrastructure**

kavramlarından ilham alınarak oluşturulmuştur.

Dağınık operasyon süreçlerini tek merkezde senkronize eden modern bir AI operasyon altyapısını temsil eder.

---

# 🎯 Temel Amaç

Platformun temel amacı:

```text
Excel → Veri İşleme → Yapay Zeka Analizi → Operasyon Yönetimi
```

akışını tek sistem altında birleştirmektir.

Sistem:

- stok seviyelerini analiz eder,
- operasyonel riskleri tespit eder,
- sipariş süreçlerini takip eder,
- kritik durumları yorumlar,
- yapay zeka destekli operasyon çıktıları üretir.

---

# ✨ Temel Özellikler

## 📦 Akıllı Stok Yönetimi

- Kritik stok tespiti
- Düşük stok analizi
- AI destekli stok yorumlama
- Yeniden sipariş önerileri
- Tedarikçi mail taslakları

---

## 🛒 Sipariş ve Operasyon Takibi

- Sipariş görüntüleme
- Operasyon paneli
- Günlük operasyon özeti
- Bekleyen süreç analizi
- Süreç durum yönetimi

---

## 📊 Excel Tabanlı Veri Yönetimi

- Excel template indirme
- Toplu ürün yükleme
- Pandas tabanlı veri işleme
- Bulk upload desteği
- Büyük veri işleme altyapısı

---

## 🤖 AI Destekli Operasyon Asistanı

AI sistemi:

- operasyonel riskleri yorumlar,
- kritik stokları analiz eder,
- bağlama uygun içerik üretir,
- tedarikçi iletişimi oluşturur,
- yöneticiyi kritik durumlarda bilgilendirir.

---

## ⚡ Action Layer

Syntra yalnızca analiz yapan bir sistem değildir.

Platform:

- operasyonel bildirim oluşturabilir,
- task üretebilir,
- tedarikçi iletişimi hazırlayabilir,
- aksiyon akışlarını tetikleyebilir.

Planned Integrations:

- WhatsApp Notifications
- Telegram Bot Integration
- Supplier Order Draft API
- Cargo Tracking APIs
- Automated Customer Updates

---

# 🧠 AI Decision Engine

Syntra içerisinde bulunan AI Decision Engine katmanı:

- operasyonel riskleri analiz eder,
- kritik eşikleri değerlendirir,
- aksiyon gerekliliğini belirler,
- otomatik operasyon çıktıları üretir.

Örnek karar akışı:

```text
Stock Below Threshold
        ↓
Risk Analysis
        ↓
AI Decision
        ↓
Notification + Supplier Draft + Task Creation
```

Bu yapı sayesinde sistem yalnızca öneri sunmaz; operasyonel süreçlere aktif şekilde katılır.

---

# ⚡ Event-Driven Trigger Architecture

Syntra event-driven operasyon mantığına uygun şekilde tasarlanmıştır.

Sistem içerisinde:

- `stock_below_threshold`
- `order_created`
- `shipment_delayed`

gibi olaylar trigger mekanizması olarak çalışabilir.

Örnek:

```python
if stock < critical_limit:
    trigger_ai_agent()
```

Bu yaklaşım sistemin:

- daha ölçeklenebilir,
- daha modüler,
- daha otomasyon odaklı

çalışmasını sağlar.

---

# 📈 Operational Intelligence Layer

Platform operasyonel içgörü üretmek için veri analiz katmanına sahiptir.

Planned Features:

- trend analysis
- anomaly detection
- predictive stock analysis
- sales forecasting
- risk scoring
- operational KPI dashboard

Örnek çıktılar:

- “Bu hafta tükenmesi beklenen ürünler”
- “Riskli operasyon süreçleri”
- “En yüksek satış trendine sahip ürünler”

---

# 🏗️ Sistem Mimarisi

## Backend

- FastAPI
- Async Architecture
- RESTful API
- Dependency Injection
- Pydantic Validation

---

## Database

- PostgreSQL
- SQLAlchemy 2.0
- Async ORM
- Relational Schema Design

---

## AI Layer

- Gemini API
- Prompt-driven Operational Analysis
- AI Generated Outputs
- AI Decision Engine
- Trigger-based Operations

---

## Frontend

- Streamlit Dashboard
- Dashboard-based UX
- Operational Visualization

---

## Containerization

- Docker
- Docker Compose
- Isolated Service Architecture

---

# 🧰 Teknoloji Yığını

| Teknoloji | Kullanım Amacı |
|---|---|
| FastAPI | Backend API |
| Python 3.12 | Ana programlama dili |
| PostgreSQL | Veritabanı |
| SQLAlchemy 2.0 | ORM |
| AsyncPG | Async PostgreSQL Driver |
| Streamlit | Frontend |
| Pandas | Veri işleme |
| OpenPyXL | Excel işlemleri |
| Gemini 2.5 Flash | Yapay zeka modeli |
| Docker | Containerization |
| Docker Compose | Servis yönetimi |

---

# 📂 Proje Yapısı

```bash
project-root/
│
├── app/
│   ├── api/
│   │   └── endpoints.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── adapter.py
│   │   ├── decision_engine.py
│   │   ├── event_bus.py
│   │   └── notification_service.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── frontend/
│   └── app.py
│
├── Dockerfile
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

# 🔄 Sistem Akışı

## 1️⃣ Veri Girişi

Kullanıcı Excel dosyası yükler.

## 2️⃣ Veri İşleme

Pandas ile veriler parse edilir ve doğrulanır.

## 3️⃣ Veritabanı Kaydı

Ürünler PostgreSQL veritabanına aktarılır.

## 4️⃣ Event Trigger

Sistem kritik olayları tespit eder.

Örnek:

- stock_below_threshold
- order_created
- shipment_delayed

---

## 5️⃣ AI Analizi

AI sistemi:

- operasyonel riskleri yorumlar,
- stok seviyelerini analiz eder,
- aksiyon gerekliliğini belirler.

---

## 6️⃣ Action Layer

Sistem:

- bildirim üretir,
- task oluşturur,
- tedarikçi mail taslağı hazırlar,
- operasyonel öneriler sunar.

---

## 7️⃣ Dashboard Görselleştirme

Tüm süreç operasyon panelinde görüntülenir.

---

# 🌐 API Endpointleri

## Health Check

```http
GET /health
```

---

## Excel Template İndir

```http
GET /api/download-template
```

---

## Ürün Yükleme

```http
POST /api/upload-products
```

---

## AI Stok Analizi

```http
GET /api/ai/stock-alerts
```

---

## Supplier Draft Generation

```http
POST /api/supplier/draft
```

---

## Notification Trigger

```http
POST /api/notifications/send
```

---

# 🗄️ Veritabanı Yapısı

## Product

Ürün bilgilerini saklar.

### Alanlar

- SKU
- Ürün adı
- Stok miktarı
- Kritik limit
- Tedarikçi mail adresi

---

## Order

Sipariş verilerini tutar.

### Alanlar

- Sipariş numarası
- Müşteri bilgisi
- Sipariş durumu
- Oluşturulma tarihi

---

## OrderItem

Sipariş ve ürün ilişkisini yönetir.

---

# 🧠 AI Operasyon Katmanı

AI sistemi:

- düşük stok ürünlerini analiz eder,
- bağlama uygun içerik üretir,
- operasyonel riskleri yorumlar,
- karar destek çıktıları oluşturur.

## Örnek Çıktı

```text
“Domates stoğu kritik seviyenin altında.
Tedarikçiden yeni ürün talep edilmesi önerilir.”
```

---

# 🖥️ Frontend

Frontend katmanı Streamlit ile geliştirilmiştir.

## Özellikler

- Excel yükleme ekranı
- Dashboard görünümü
- AI analiz ekranı
- Operasyon paneli
- Bildirim sistemi
- Kritik stok görünümü
- Operasyonel özet paneli

---

# 🐳 Docker & Deployment

Tüm sistem Docker Compose ile ayağa kaldırılmaktadır.

## Servisler

- PostgreSQL Database
- FastAPI Backend
- Streamlit Frontend
- Gemini AI Integration Layer

## Avantajlar

- İzole geliştirme ortamı
- Tek komutla kurulum
- Kolay deployment
- Tutarlı çalışma ortamı
- Containerized architecture

---

# ⚙️ Kurulum

## 1. Repository Clone

```bash
git clone <repo-url>
cd syntra
```

---

## 2. Environment Variables

Root dizininde `.env` dosyası oluşturun:

```env
DATABASE_URL=postgresql+asyncpg://admin:password@db:5432/kobi_os
GEMINI_API_KEY=your_api_key
PROJECT_NAME=Syntra
DEBUG=True
```

---

## 3. Docker Servislerini Build Et

```bash
docker compose build
```

---

## 4. Sistemi Başlat

```bash
docker compose up
```

---

# ▶️ Uygulama Erişim Noktaları

| Servis | URL |
|---|---|
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Streamlit Dashboard | http://localhost:8501 |

---

# 🎬 Demo Senaryosu

1. Kullanıcı ürün Excel dosyasını yükler.
2. Sistem ürünleri veritabanına aktarır.
3. Kritik stok event’i tetiklenir.
4. AI sistemi operasyonel analiz gerçekleştirir.
5. Supplier draft oluşturulur.
6. Bildirim sistemi çalışır.
7. Sonuçlar dashboard üzerinden görüntülenir.

Bu süreç boyunca insan müdahalesi minimum seviyede tutulur.

---

# 🚀 Gelecek Geliştirmeler

- WhatsApp entegrasyonu
- Kargo API entegrasyonları
- AI destekli tahminleme
- Gerçek zamanlı bildirim sistemi
- Görev yönetimi
- Satış analitiği
- Mobil uygulama desteği
- Çoklu kullanıcı sistemi
- Yetkilendirme mekanizması
- RAG tabanlı veri erişimi
- Autonomous AI workflows
- Multi-agent operations
- Predictive supply management

---

# 🏆 Hackathon Kriterleri ile Uyumluluk

## Problem Tanımı & Değer Önerisi

Syntra, KOBİ’lerin manuel operasyon süreçlerinden kaynaklanan:

- operasyonel verimsizlik,
- insan kaynaklı hata,
- stok kayıpları,
- müşteri memnuniyetsizliği,
- ölçeklenme problemleri

gibi temel sorunlarına çözüm üretmek amacıyla geliştirilmiştir.

---

## Yapay Zeka Kullanımının Doğruluğu

AI sistemi yalnızca sohbet amacıyla değil:

- operasyonel analiz,
- risk tespiti,
- karar destek mekanizması,
- tedarikçi iletişimi,
- aksiyon üretimi

amacıyla kullanılmaktadır.

Kullanılan model:

- Gemini 2.5 Flash

---

## Teknik Uygulama & Mimari

Sistem:

- async backend mimarisi,
- AI decision engine,
- event-driven triggers,
- containerized deployment,
- modüler servis mimarisi

ile geliştirilmiştir.

---

## Ürünleşme & Kullanıcı Deneyimi

Platform gerçek kullanım senaryolarına uygun şekilde tasarlanmıştır.

Kullanıcı akışı:

```text
Excel Upload → AI Analysis → Operational Action → Dashboard Output
```

---

## Yenilikçilik

Sistem yalnızca veri görüntüleyen bir panel değil:

- operasyonel yorumlama yapan,
- AI destekli aksiyon üreten,
- süreç yönetimine katkı sağlayan

bir operasyon platformudur.

---

## Çalışabilirlik

Tüm servisler Docker Compose ile ayağa kaldırılabilmektedir.

Temel operasyon akışı uçtan uca çalışmaktadır.

---

## Sunum & Demo Yetkinliği

Platform gerçek KOBİ senaryoları üzerinden canlı demo yapılabilecek şekilde tasarlanmıştır.

---

## Dokümantasyon & Kod Organizasyonu

Kod yapısı:

- modüler mimari,
- servis bazlı ayrıştırma,
- environment-based configuration,
- containerized deployment

yaklaşımlarıyla organize edilmiştir.

---

# 📌 Sonuç

Syntra;

- yapay zeka destekli,
- operasyon odaklı,
- ölçeklenebilir,
- modern mimarili

bir KOBİ operasyon yönetim platformudur.

Amaç yalnızca veri göstermek değil;

işletmelerin operasyonel yükünü azaltan, süreçleri optimize eden ve karar destek mekanizmaları sunan akıllı bir sistem oluşturmaktır.
