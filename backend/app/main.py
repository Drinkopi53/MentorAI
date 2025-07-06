from fastapi import FastAPI, HTTPException, Body
from .schemas import Curriculum, CurriculumGoalRequest # Mengimpor model Pydantic
from .ai_services import generate_curriculum_from_goal # Mengimpor layanan AI

# Aplikasi FastAPI utama. Jika menggunakan --root-path /api di docker-compose,
# semua rute yang didefinisikan di sini akan secara otomatis diawali dengan /api.
# Jadi, endpoint "/" akan menjadi "/api/" dan "/curriculum" akan menjadi "/api/curriculum".
app = FastAPI(
    title="MentorAI Backend",
    version="0.1.0",
    description="Backend API untuk MentorAI, menyediakan generasi kurikulum dan fitur lainnya."
)

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

# Anda dapat menambahkan router lain di sini jika aplikasi berkembang
# from .routers import users, content_sources
# app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(content_sources.router, prefix="/content", tags=["Content Sources"])


if __name__ == "__main__":
    import uvicorn
    # Perintah ini untuk menjalankan aplikasi secara langsung dengan `python -m app.main` (jika di root backend)
    # atau `python main.py` (jika di direktori app).
    # Konfigurasi uvicorn di docker-compose.yml (`app.main:app --reload --host 0.0.0.0 --port 8000 --root-path /api`)
    # adalah yang akan digunakan saat menjalankan dengan Docker.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Menambahkan reload=True untuk konsistensi
