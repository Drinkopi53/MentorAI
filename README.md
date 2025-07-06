# MentorAI

## Gambaran Umum Proyek

MentorAI adalah platform bertenaga AI yang dirancang untuk memberikan panduan dan dukungan yang dipersonalisasi kepada pengguna di berbagai domain. Ini memanfaatkan kekuatan model bahasa besar (LLM) melalui Gemini API dari Google untuk menawarkan pengalaman bimbingan interaktif dan adaptif. Platform ini memungkinkan pengguna untuk mengimpor konten dari berbagai sumber seperti video YouTube, PDF, dan halaman web, lalu menggunakan konten ini untuk membuat basis pengetahuan yang dapat ditanyakan oleh pengguna.

Arsitektur proyek terdiri dari:

*   **Frontend:** Aplikasi React yang menyediakan antarmuka pengguna untuk berinteraksi dengan platform.
*   **Backend:** API FastAPI yang menangani logika bisnis, interaksi database, dan integrasi dengan layanan eksternal seperti Gemini API dan YouTube.
*   **Database:** PostgreSQL dengan ekstensi `pgvector` untuk menyimpan data pengguna, konten yang diproses, dan embedding vektor untuk pencarian semantik.

## Prasyarat

Pastikan Anda telah menginstal perangkat lunak berikut di sistem Anda:

*   [Node.js](https://nodejs.org/) (versi LTS direkomendasikan)
*   [Python](https://www.python.org/) (versi 3.8 atau lebih tinggi)
*   [Docker](https://www.docker.com/) dan [Docker Compose](https://docs.docker.com/compose/)

## Struktur Monorepo

Proyek ini diatur sebagai monorepo dengan direktori utama berikut:

*   `/frontend`: Berisi kode sumber untuk aplikasi React.
*   `/backend`: Berisi kode sumber untuk aplikasi FastAPI.

## Penyiapan Lingkungan Pengembangan

Ikuti langkah-langkah ini untuk menyiapkan lingkungan pengembangan lokal.

### 1. Kloning Repositori

```bash
git clone <URL_REPOSITORI_ANDA>
cd MentorAI
```

### 2. Konfigurasi Variabel Lingkungan

Anda perlu membuat file `.env` di direktori `/frontend` dan `/backend` untuk menyimpan variabel lingkungan.

**Frontend (`/frontend/.env`):**

Buat file bernama `.env` di direktori `/frontend` dan tambahkan variabel berikut:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

Ganti nilai jika backend Anda berjalan di URL atau port yang berbeda.

**Backend (`/backend/.env`):**

Buat file bernama `.env` di direktori `/backend` dan tambahkan variabel berikut:

```env
DATABASE_URL=postgresql://user:password@db:5432/mentorai_db
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
YOUTUBE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
JWT_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Ganti nilai placeholder dengan kredensial dan kunci API Anda yang sebenarnya:
*   `DATABASE_URL`: URL koneksi untuk database PostgreSQL Anda. Jika menggunakan Docker Compose seperti yang disediakan, `user`, `password`, dan `mentorai_db` harus cocok dengan yang dikonfigurasi di `docker-compose.yml`.
*   `GEMINI_API_KEY`: Kunci API Gemini Anda dari Google AI Studio atau Google Cloud.
*   `YOUTUBE_API_KEY`: Kunci API Google Cloud Anda yang diaktifkan untuk YouTube Data API v3.
*   `JWT_SECRET_KEY`: Kunci rahasia yang kuat untuk menandatangani token JWT. Anda dapat membuatnya menggunakan `openssl rand -hex 32`.

### 3. Penyiapan Backend

Buka terminal baru dan navigasikan ke direktori backend:

```bash
cd backend
```

Buat dan aktifkan lingkungan virtual (disarankan):

```bash
python -m venv venv
# Di Windows
# venv\Scripts\activate
# Di macOS/Linux
# source venv/bin/activate
```

Instal dependensi Python:

```bash
pip install -r requirements.txt
```

### 4. Penyiapan Frontend

Buka terminal baru dan navigasikan ke direktori frontend:

```bash
cd frontend
```

Instal dependensi Node.js:

```bash
npm install
```

## Menjalankan Server Pengembangan

Anda dapat menjalankan server pengembangan untuk frontend dan backend secara bersamaan.

**Menggunakan Docker Compose (Cara yang Direkomendasikan):**

Cara termudah untuk menjalankan semua layanan (frontend, backend, dan database) adalah dengan menggunakan Docker Compose. Dari direktori root proyek:

```bash
docker-compose up --build
```

*   Frontend akan dapat diakses di `http://localhost:3000`.
*   Backend akan dapat diakses di `http://localhost:8000`.
*   Database PostgreSQL akan berjalan di port `5432` (diekspos ke host jika diperlukan, tetapi terutama diakses oleh layanan backend melalui jaringan Docker).

**Menjalankan Secara Manual:**

Jika Anda lebih suka menjalankan layanan secara manual tanpa Docker:

**Menjalankan Backend (FastAPI):**

Di terminal dengan direktori `/backend` dan lingkungan virtual diaktifkan:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di `http://localhost:8000`.

**Menjalankan Frontend (React):**

Di terminal dengan direktori `/frontend`:

```bash
npm start
```

Aplikasi React akan terbuka secara otomatis di browser Anda, biasanya di `http://localhost:3000`.

Setelah menjalankan kedua server secara manual, frontend akan dapat berkomunikasi dengan backend jika `REACT_APP_API_BASE_URL` di `/frontend/.env` dikonfigurasi dengan benar untuk menunjuk ke server backend (misalnya, `http://localhost:8000/api`).
Pastikan database PostgreSQL Anda berjalan secara terpisah dan `DATABASE_URL` di `/backend/.env` menunjuk ke sana dengan benar.

---

Dengan mengikuti instruksi ini, Anda seharusnya dapat menyiapkan dan menjalankan proyek MentorAI di lingkungan pengembangan lokal Anda.