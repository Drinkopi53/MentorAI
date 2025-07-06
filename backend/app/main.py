import os # Ditambahkan untuk pemeriksaan getenv di startup
from fastapi import FastAPI, HTTPException, Body, Depends, Query as FastAPIQuery
from typing import List, Optional
from sqlalchemy.orm import Session

from .schemas import ( # Mengimpor model Pydantic
    Curriculum, CurriculumGoalRequest,
    SearchResponse, SearchResultItem
)
from .ai_services import generate_curriculum_from_goal, get_embedding # Mengimpor layanan AI
from .database import create_db_and_tables, get_db # Untuk DB setup dan session
from .models import LearningContent, ContentType as ContentTypeEnum # Model database dan Enum
from pydantic import HttpUrl # Untuk validasi URL di IndexUrlRequest
import requests # Untuk mengambil judul di endpoint indeks
from bs4 import BeautifulSoup # Untuk parsing HTML judul di endpoint indeks


# Panggil create_db_and_tables() di sini atau gunakan event handler startup.
# Menggunakan event handler lebih disarankan untuk aplikasi FastAPI.

from .routers import users as usersRouter
from .routers import forum as forumRouter
from .routers import auth as authRouter # Impor router otentikasi

# Aplikasi FastAPI utama. Jika menggunakan --root-path /api di docker-compose,
# semua rute yang didefinisikan di sini akan secara otomatis diawali dengan /api.
# Jadi, endpoint "/" akan menjadi "/api/" dan "/curriculum" akan menjadi "/api/curriculum".
app = FastAPI(
    title="MentorAI Backend",
    version="0.1.0",
    description="Backend API untuk MentorAI, menyediakan generasi kurikulum dan fitur lainnya."
)

# Event handler untuk startup aplikasi
@app.on_event("startup")
def on_startup():
    """
    Fungsi yang akan dijalankan saat aplikasi FastAPI dimulai.
    Ini akan membuat tabel database jika belum ada.
    """
    print("Aplikasi FastAPI memulai...")
    create_db_and_tables()
    print("Pemeriksaan/pembuatan tabel database selesai.")
    # Anda bisa menambahkan inisialisasi lain di sini jika perlu
    # Misalnya, memastikan model embedding dimuat (meskipun ai_services.py sudah melakukannya saat impor)
    if get_embedding("test") is None and os.getenv("GEMINI_API_KEY"): # Cek sederhana jika embedding service bermasalah
        print("PERINGATAN PENTING: Fungsi get_embedding mungkin tidak berfungsi dengan benar.")


@app.get("/", tags=["General"])
async def root():
    """
    Endpoint root untuk API backend MentorAI.
    Menyediakan pesan status sederhana yang menunjukkan bahwa backend berjalan.
    Jika Uvicorn dijalankan dengan `--root-path /api`, endpoint ini akan dapat diakses di `/api/`.
    """
    return {"message": "MentorAI Backend is running"}

@app.post("/curriculum", response_model=Curriculum, tags=["Curriculum Generation"])
async def create_curriculum_endpoint(
    request_body: CurriculumGoalRequest = Body(..., description="Tujuan pembelajaran pengguna untuk menghasilkan kurikulum.")
):
    """
    Membuat dan mengembalikan kurikulum pembelajaran yang dipersonalisasi berdasarkan tujuan (goal) yang diberikan pengguna.

    Endpoint ini menggunakan model AI generatif (Google Gemini) untuk:
    1.  Memecah tujuan pengguna menjadi modul-modul pembelajaran tingkat tinggi.
    2.  Untuk setiap modul, menghasilkan detail seperti tujuan pembelajaran, topik, deskripsi, dan kata kunci.

    Outputnya adalah objek Kurikulum terstruktur yang siap digunakan oleh frontend atau layanan lain.
    """
    try:
        print(f"Menerima permintaan kurikulum untuk tujuan: {request_body.goal}")
        curriculum_result = await generate_curriculum_from_goal(request_body.goal)
        if not curriculum_result.modules:
            # Ini bisa terjadi jika AI tidak dapat menghasilkan modul yang valid atau terjadi error parsial
            # Pertimbangkan apakah akan mengembalikan 200 dengan modul kosong atau error tertentu.
            # Untuk saat ini, kita kembalikan apa yang dihasilkan, bahkan jika modul kosong.
            print(f"PERINGATAN: Kurikulum yang dihasilkan untuk '{request_body.goal}' tidak memiliki modul.")
        return curriculum_result
    except ValueError as ve:
        # Error yang diketahui, seperti GEMINI_API_KEY tidak ada atau parsing JSON gagal
        print(f"ValueError saat membuat kurikulum: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        # Error runtime umum dari layanan AI
        print(f"RuntimeError saat membuat kurikulum: {re}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan pada layanan AI: {re}")
    except Exception as e:
        # Menangkap error tak terduga lainnya
        print(f"Error tak terduga saat membuat kurikulum: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal server yang tidak terduga: {e}")


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_learning_content(
    query: str = FastAPIQuery(..., min_length=3, max_length=200, description="Kueri pencarian pengguna."),
    top_k: int = FastAPIQuery(10, ge=1, le=50, description="Jumlah hasil teratas yang akan dikembalikan."),
    db: Session = Depends(get_db)
):
    """
    Mencari konten pembelajaran yang relevan berdasarkan kueri pengguna menggunakan pencarian semantik.

    Endpoint ini akan:
    1. Menghasilkan embedding vektor untuk kueri pencarian pengguna.
    2. Mencari di database untuk potongan konten yang memiliki embedding paling mirip
       (menggunakan kesamaan kosinus) dengan embedding kueri.
    3. Mengembalikan daftar potongan konten yang paling relevan.
    """
    print(f"Menerima permintaan pencarian untuk kueri: '{query}' dengan top_k={top_k}")

    query_embedding = get_embedding(query)
    if query_embedding is None:
        print(f"Gagal menghasilkan embedding untuk kueri: '{query}'")
        raise HTTPException(status_code=500, detail="Gagal memproses kueri pencarian (embedding error).")

    try:
        # Melakukan pencarian kesamaan kosinus.
        # Operator <=> menghitung jarak kosinus. Semakin kecil jaraknya, semakin mirip.
        # Untuk kesamaan kosinus (di mana nilai yang lebih tinggi lebih baik), Anda mungkin perlu 1 - jarak,
        # atau menggunakan operator lain jika pgvector mendukungnya secara langsung (misalnya, inner product #>).
        # pgvector: L2 distance (<->), inner product (<#>), cosine distance (<=>).
        # Cosine distance = 1 - cosine similarity. Jadi, order by ASC pada cosine distance adalah benar.

        # Opsi 1: Menggunakan cosine_distance (jarak, lebih kecil lebih baik)
        # results = db.query(LearningContent).order_by(LearningContent.embedding.cosine_distance(query_embedding)).limit(top_k).all()

        # Opsi 2: Menggunakan max_inner_product (produk dalam, lebih besar lebih baik untuk vektor ternormalisasi)
        # Jika embedding Anda ternormalisasi, produk dalam negatif setara dengan jarak kosinus.
        # results = db.query(LearningContent).order_by(LearningContent.embedding.max_inner_product(query_embedding).desc()).limit(top_k).all()

        # Kita akan tetap menggunakan cosine_distance karena lebih intuitif (jarak lebih kecil = lebih mirip)
        # dan umum digunakan.

        similar_contents = db.query(LearningContent)\
                             .order_by(LearningContent.embedding.cosine_distance(query_embedding))\
                             .limit(top_k)\
                             .all()

        # Jika Anda ingin skor kesamaan (0 hingga 1, di mana 1 adalah kesamaan sempurna):
        # from sqlalchemy import func, literal_column
        # similar_contents_with_score = db.query(
        #     LearningContent,
        #     (1 - LearningContent.embedding.cosine_distance(query_embedding)).label("similarity_score")
        # ).order_by(literal_column("similarity_score").desc()).limit(top_k).all()
        # Kemudian Anda perlu menyesuaikan SearchResultItem untuk menyertakan similarity_score
        # dan memproses tuple (LearningContent, score)

        print(f"Ditemukan {len(similar_contents)} hasil pencarian untuk kueri '{query}'.")

        # Konversi hasil SQLAlchemy ke model Pydantic SearchResultItem
        # Perhatikan bahwa LearningContent.content_type adalah enum, perlu dikonversi ke str jika belum.
        # Model Pydantic dengan orm_mode=True akan mencoba menangani ini.
        search_results = [
            SearchResultItem.from_orm(content) for content in similar_contents
        ]

        return SearchResponse(query=query, results=search_results)

    except Exception as e:
        print(f"Error saat melakukan pencarian di database: {e}")
        # Log error lebih detail di sini di produksi
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat melakukan pencarian: {e}")

# --- Endpoint Pengindeksan untuk Pengujian ---
from .data_ingestion import scrape_article_content # Untuk mengambil konten artikel
from .indexing import index_content # Fungsi pengindeksan utama
from .models import ContentType # Enum untuk tipe konten
from pydantic import BaseModel, HttpUrl

class IndexUrlRequest(BaseModel):
    url: HttpUrl
    title: Optional[str] = None # Judul bisa opsional, mungkin diambil dari artikel
    content_type: ContentType = ContentType.ARTICLE # Default ke artikel

@app.post("/index-content", tags=["Indexing (Testing)"], summary="Indeks konten dari URL")
async def index_content_from_url_endpoint(
    request: IndexUrlRequest,
    db: Session = Depends(get_db)
):
    """
    **Endpoint Pengujian:** Mengambil konten dari URL yang diberikan,
    memprosesnya, dan mengindeksnya ke dalam database untuk pencarian semantik.

    - Menggunakan `scrape_article_content` untuk mengambil teks dari URL.
    - Memanggil `index_content` untuk memotong teks, membuat embedding, dan menyimpan ke DB.
    """
    print(f"Menerima permintaan pengindeksan untuk URL: {request.url} dengan tipe: {request.content_type}")

    scraped_text = None
    article_title = request.title

    if request.content_type == ContentType.ARTICLE:
        scraped_text = scrape_article_content(str(request.url))
        if not scraped_text:
            raise HTTPException(status_code=400, detail=f"Gagal mengambil atau memproses konten artikel dari URL: {request.url}")
        if not article_title: # Coba ambil judul dari tag <title> jika tidak disediakan
            try:
                response = requests.get(str(request.url), timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                if soup.title and soup.title.string:
                    article_title = soup.title.string.strip()
            except Exception:
                pass # Biarkan kosong jika gagal
            if not article_title: # Jika masih kosong
                 article_title = "Artikel Tidak Berjudul" # Default
    # Tambahkan logika lain di sini jika ada tipe konten lain yang perlu di-scrape berbeda
    # Misalnya, untuk YOUTUBE_TRANSCRIPT, Anda perlu mengambil transkrip, bukan meng-scrape halaman.
    else:
        raise HTTPException(status_code=400, detail=f"Tipe konten '{request.content_type}' saat ini tidak didukung untuk pengindeksan otomatis dari URL.")

    if not scraped_text: # Seharusnya sudah ditangani, tapi sebagai penjaga
        raise HTTPException(status_code=500, detail="Gagal mendapatkan konten teks untuk diindeks.")

    try:
        indexed_items = index_content(
            db=db,
            source_url=str(request.url),
            title=article_title if article_title else "Konten Tidak Berjudul",
            text_content=scraped_text,
            content_type=request.content_type
        )
        if not indexed_items:
            return {"message": "Konten berhasil diproses tetapi tidak ada potongan yang diindeks (mungkin teks kosong atau error embedding).", "url": str(request.url), "title": article_title, "indexed_chunks": 0}

        return {
            "message": "Konten berhasil diindeks.",
            "url": str(request.url),
            "title": article_title,
            "indexed_chunks": len(indexed_items),
            "first_chunk_id": indexed_items[0].id if indexed_items else None
        }
    except Exception as e:
        print(f"Error selama proses pengindeksan untuk URL {request.url}: {e}")
        db.rollback() # Pastikan rollback jika terjadi error di sini
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat pengindeksan konten: {str(e)}")


# Anda dapat menambahkan router lain di sini jika aplikasi berkembang
# from .routers import users, content_sources
# app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(content_sources.router, prefix="/content", tags=["Content Sources"])

# Sertakan router untuk pengguna dan forum
# Prefix /api akan ditangani oleh Uvicorn jika --root-path /api digunakan.
# Jadi, kita tidak perlu menambahkan /api lagi di sini.
# Router itu sendiri sudah memiliki prefix (misal, /users, /forum, /auth).
app.include_router(authRouter.router)
app.include_router(usersRouter.router)
app.include_router(forumRouter.router)


if __name__ == "__main__":
    import uvicorn
    # Perintah ini untuk menjalankan aplikasi secara langsung dengan `python -m app.main` (jika di root backend)
    # atau `python main.py` (jika di direktori app).
    # Konfigurasi uvicorn di docker-compose.yml (`app.main:app --reload --host 0.0.0.0 --port 8000 --root-path /api`)
    # adalah yang akan digunakan saat menjalankan dengan Docker.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Menambahkan reload=True untuk konsistensi

# --- Endpoint Chatbot RAG ---
from fastapi.responses import StreamingResponse
from .chatbot import stream_chatbot_response # Fungsi streaming dari chatbot.py
from langchain_core.runnables import RunnableConfig # Untuk config di stream

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Pertanyaan pengguna untuk chatbot.")
    # Anda bisa menambahkan session_id atau user_id di sini jika diperlukan untuk histori chat
    # session_id: Optional[str] = None

@app.post("/chat", tags=["Chatbot (RAG)"], summary="Berinteraksi dengan Tutor AI")
async def chat_with_rag_bot(
    request: ChatRequest
):
    """
    Menerima pertanyaan pengguna dan mengalirkan (streams) jawaban yang dihasilkan oleh
    Tutor AI berbasis RAG (Retrieval Augmented Generation).

    Tutor AI akan menggunakan basis pengetahuan yang telah diindeks (konten pembelajaran)
    untuk menemukan informasi yang relevan dan kemudian menggunakan model bahasa (Gemini)
    untuk menghasilkan jawaban berdasarkan informasi tersebut.
    """
    print(f"Menerima permintaan chat: '{request.question}'")

    try:
        # Di sini Anda bisa membuat config jika perlu, misalnya untuk callbacks
        # config = RunnableConfig(callbacks=[YourCallbackHandler()])
        config = None # Untuk saat ini tidak ada config khusus

        # Pastikan stream_chatbot_response adalah async generator
        return StreamingResponse(
            stream_chatbot_response(request.question, config=config),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"Error pada endpoint /chat: {e}")
        # Ini adalah fallback, idealnya stream_chatbot_response menangani error internalnya sendiri
        # dan menghasilkan pesan error sebagai bagian dari stream.
        async def error_stream():
            yield f"Error: Terjadi kesalahan internal saat memproses permintaan chat Anda: {str(e)}"
        return StreamingResponse(error_stream(), media_type="text/event-stream", status_code=500)
