# Syntra — takım kurulumu

Bu dosya repoyu GitHub’dan indiren herkesin **aynı adımlarla** API ve arayüzü çalıştırması içindir.

## Gereksinimler

| Araç | Sürüm / not |
|------|----------------|
| Python | **3.10+** (Docker imajı 3.12 kullanır) |
| Git | Son sürüm |
| Docker (isteğe bağlı) | Docker Compose v2 |

---

## 1. Repoyu alın

```bash
git clone https://github.com/eft99/Syntra.git
cd Syntra
```

---

## 2. Ortam dosyası (`.env`)

`.env` repoda **yoktur** (gizli anahtarlar için). Şablonu kopyalayın:

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

Sonra `.env` içinde özellikle düzenleyin:

- **`GEMINI_API_KEY`** — AI özellikleri için (yerelde boş bırakılabilir; AI çağrıları hata verebilir).
- **`DATABASE_URL`** — Docker Compose ile çalışıyorsanız örnekteki varsayılan genelde yeterlidir.

---

## 3A. Yerel çalıştırma (Python ile)

### Sanal ortam

**Windows**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### API (FastAPI)

**Windows:** proje kökünde `run_api.ps1` ( `--reload-dir app` ile OneDrive/izin sorunları azaltılır )

```powershell
.\run_api.ps1
```

**Linux / macOS:**

```bash
bash run_api.sh
```

İsteğe bağlı port: `PORT=8080 bash run_api.sh`

Veya doğrudan:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir app
```

- Sağlık kontrolü: <http://127.0.0.1:8000/health>
- Swagger: <http://127.0.0.1:8000/docs>

**Windows `WinError 10013`:** 8000 doluysa başka süreci kapatın veya `--port 8080` kullanın; Streamlit için:

```powershell
$env:SYNTRA_API_BASE_URL = "http://127.0.0.1:8080"
```

### Arayüz (Streamlit)

Yeni bir terminalde, sanal ortam açıkken:

```bash
cd Syntra   # repo kökü
streamlit run frontend/app.py
```

Tarayıcı: **<http://localhost:8501>**

API farklı makine/portta ise ortam değişkeni:

```powershell
# Windows PowerShell
$env:SYNTRA_API_BASE_URL = "http://127.0.0.1:8000"
streamlit run frontend/app.py
```

```bash
# Linux / macOS
export SYNTRA_API_BASE_URL=http://127.0.0.1:8000
streamlit run frontend/app.py
```

---

## 3B. Docker Compose (API + PostgreSQL + UI)

```bash
cp .env.example .env   # ve GEMINI_API_KEY vb. doldurun
docker compose up --build
```

- API: **<http://localhost:8000>**
- Streamlit: **<http://localhost:8501>**  
  Compose içinde UI, API’ye **`http://api:8000`** ile gider (`docker-compose.yml` içinde tanımlı).

Durdurmak: `Ctrl+C`, veriyi silmeden: `docker compose down`  
Volume ile veriyi de silmek: `docker compose down -v`

---

## Demo giriş (Streamlit)

| Rol | Kullanıcı adı | Şifre |
|-----|----------------|-------|
| Yönetici (tüm sekmeler) | `admin` | `admin123` |
| Müşteri (kısıtlı) | `user` | `user123` |

Şifre sıfırlama (demo e-postalar): `admin@syntra.app`, `musteri@syntra.app`

---

## Proje yapısı (özet)

```text
Syntra/
  app/                 # FastAPI backend
  frontend/            # Streamlit (app.py, api_client, views, …)
  requirements.txt     # Backend + ortak araçlar
  requirements-frontend.txt  # Sadece UI Docker imajı
  docker-compose.yml
  .env.example
  run_api.ps1 / run_api.sh
```

---

## Git dalı önerisi

`main` — stabil; özellikler için `feature/...` dalları kullanın.

---

## Sorun giderme

| Sorun | Öneri |
|--------|--------|
| `API'ye ulaşılamıyor` (Streamlit) | Önce uvicorn’un çalıştığını `GET /health` ile doğrulayın. |
| `WinError 10013` (Windows) | Port çakışması veya `--reload`; `run_api.ps1` veya `--reload-dir app` kullanın. |
| AI hata veriyor | `.env` içinde geçerli `GEMINI_API_KEY` tanımlayın. |
| Postgres bağlantı hatası | Docker’da `db` servisinin healthy olduğunu bekleyin; `DATABASE_URL` ile uyumlu kullanıcı/şifre kullanın. |
