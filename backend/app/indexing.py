from sqlalchemy.orm import Session
from typing import List, Optional

from .data_ingestion import chunk_text # Fungsi dari langkah 2.2 (seharusnya dari data_ingestion.py)
from .ai_services import get_embedding
from .models import LearningContent, ContentType # Impor model DB dan Enum
from .database import get_db # Untuk penggunaan di masa depan jika ini menjadi endpoint

def index_content(
    db: Session,
    source_url: str,
    title: str,
    text_content: str,
    content_type: ContentType
) -> List[LearningContent]:
    """
    Memproses teks konten, memecahnya menjadi potongan, menghasilkan embedding,
    dan menyimpan setiap potongan beserta embeddingnya ke database.

    Args:
        db: Sesi database SQLAlchemy.
        source_url: URL sumber konten.
        title: Judul umum konten (misalnya, judul artikel atau video).
        text_content: Teks konten mentah yang akan diindeks.
        content_type: Jenis konten (dari enum ContentType).

    Returns:
        Daftar objek LearningContent yang telah disimpan ke database.
        Mengembalikan daftar kosong jika teks konten kosong atau terjadi error embedding.
    """
    if not text_content or not text_content.strip():
        print(f"Peringatan: Konten teks untuk '{title}' ({source_url}) kosong. Tidak ada yang diindeks.")
        return []

    # Langkah 1: Potong teks menggunakan fungsi dari data_ingestion.py
    # Parameter chunk_size dan chunk_overlap default akan digunakan (1000, 150)
    text_chunks = chunk_text(text_content)

    if not text_chunks:
        print(f"Peringatan: Tidak ada potongan teks yang dihasilkan untuk '{title}' ({source_url}).")
        return []

    indexed_contents: List[LearningContent] = []
    for i, chunk in enumerate(text_chunks):
        # Langkah 2: Hasilkan embedding untuk setiap potongan
        embedding_vector = get_embedding(chunk)

        if embedding_vector is None:
            print(f"Peringatan: Gagal menghasilkan embedding untuk potongan {i+1} dari '{title}'. Potongan dilewati.")
            continue # Lewati potongan ini jika embedding gagal

        # Langkah 3: Simpan potongan dan embeddingnya ke tabel learning_content
        db_content = LearningContent(
            title=title,
            source_url=source_url,
            content_type=content_type,
            text_chunk=chunk,
            embedding=embedding_vector
            # Anda bisa menambahkan chunk_sequence=i jika kolom itu ada di model
        )
        db.add(db_content)
        indexed_contents.append(db_content)
        print(f"Potongan {i+1} dari '{title}' disiapkan untuk diindeks.")

    try:
        db.commit()
        for content in indexed_contents:
            db.refresh(content) # Refresh untuk mendapatkan ID yang dihasilkan DB, dll.
        print(f"Berhasil mengindeks {len(indexed_contents)} potongan untuk '{title}' ({source_url}).")
    except Exception as e:
        db.rollback()
        print(f"Error saat melakukan commit ke database untuk '{title}': {e}")
        # Mengembalikan daftar kosong karena tidak ada yang berhasil disimpan
        return []

    return indexed_contents

# Contoh penggunaan dasar (untuk pengujian atau pemanggilan dari skrip lain):
# if __name__ == "__main__":
#     from .database import SessionLocal, create_db_and_tables
#     from .data_ingestion import scrape_article_content # Contoh

#     # Pastikan tabel sudah dibuat
#     create_db_and_tables()

#     db = SessionLocal()

#     # Contoh 1: Indeks artikel
#     article_url = "https://www.example.com/my-cool-article" # Ganti dengan URL valid
#     # article_text = scrape_article_content(article_url) # Perlu akses internet
#     article_text = "Ini adalah konten artikel contoh yang sangat panjang. " * 50 + \
#                    "Artikel ini membahas berbagai topik menarik. " * 50 + \
#                    "Semoga proses chunking dan embedding berjalan lancar." * 50
#     article_title = "Artikel Contoh Keren"

#     if article_text:
#         print(f"\nMengindeks artikel: {article_title}")
#         indexed_articles = index_content(
#             db=db,
#             source_url=article_url,
#             title=article_title,
#             text_content=article_text,
#             content_type=ContentType.ARTICLE
#         )
#         if indexed_articles:
#             print(f"Berhasil mengindeks {len(indexed_articles)} potongan dari artikel.")
#             # print(f"ID potongan pertama: {indexed_articles[0].id}")
#         else:
#             print(f"Gagal mengindeks artikel atau tidak ada konten yang valid.")
#     else:
#         print(f"Tidak dapat mengambil konten untuk artikel: {article_url}")

    # Anda dapat menambahkan contoh lain untuk video transcript, dll.

#     db.close()
```

Beberapa poin penting:
*   Fungsi `index_content` menerima sesi database (`db: Session`) sebagai argumen. Ini memungkinkan manajemen transaksi yang lebih baik jika dipanggil dari dalam sebuah request FastAPI.
*   Menggunakan `chunk_text` dari `data_ingestion.py` dan `get_embedding` dari `ai_services.py`.
*   Membuat instance `LearningContent` untuk setiap potongan dan menambahkannya ke sesi database.
*   Melakukan `db.commit()` setelah memproses semua potongan untuk satu konten. Jika terjadi error, `db.rollback()` akan dipanggil.
*   Mengembalikan daftar objek `LearningContent` yang telah diindeks dan di-refresh (untuk mendapatkan ID dari database).
*   Saya telah menyertakan blok `if __name__ == "__main__":` yang dikomentari sebagai contoh bagaimana fungsi ini dapat diuji atau digunakan secara mandiri, tetapi ini memerlukan penyiapan database dan pengambilan konten yang sebenarnya.
*   Penting untuk memastikan bahwa `ContentType` yang diteruskan ke fungsi ini adalah anggota dari enum `ContentType` yang valid.

Langkah selanjutnya adalah membuat endpoint pencarian di `main.py`.
