from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional

from .. import schemas, models, gamification_service # Menggunakan .. untuk impor dari direktori induk (app)
from ..database import get_db

router = APIRouter(
    prefix="/forum", # Awalan umum untuk semua endpoint forum
    tags=["Forum"],
    responses={404: {"description": "Not found"}},
)

# --- Helper Functions (bisa dipindah ke forum_service.py jika kompleksitas meningkat) ---

def get_post_or_404(db: Session, post_id: int) -> models.ForumPost:
    post = db.query(models.ForumPost).filter(models.ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Postingan dengan ID {post_id} tidak ditemukan.")
    return post

def get_reply_or_404(db: Session, reply_id: int) -> models.ForumReply:
    reply = db.query(models.ForumReply).filter(models.ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Balasan dengan ID {reply_id} tidak ditemukan.")
    return reply

# --- Endpoints untuk Postingan Forum ---

@router.post("/posts", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
def create_forum_post(
    post_in: schemas.PostCreate,
    # Untuk saat ini, kita akan mensimulasikan author_id. Di aplikasi nyata, ini dari token Auth.
    author_id: int = Body(..., example=1, description="ID pengguna yang membuat postingan (simulasi untuk saat ini)."),
    db: Session = Depends(get_db)
):
    """
    Membuat postingan forum baru.
    `author_id` disimulasikan dalam body request untuk pengembangan.
    """
    # Periksa apakah pengguna (author) ada
    author = db.query(models.User).filter(models.User.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pengguna dengan ID {author_id} tidak ditemukan.")

    db_post = models.ForumPost(**post_in.model_dump(), author_id=author_id)
    db.add(db_post)

    # Gamifikasi: Tambah XP untuk membuat postingan dan periksa lencana
    # Poin XP bisa dikonfigurasi
    xp_for_post = 25
    gamification_service.add_xp(db=db, user_id=author_id, points=xp_for_post)
    # check_and_award_new_badges sudah dipanggil di dalam add_xp jika user di-pass,
    # atau kita bisa memanggilnya secara eksplisit di sini jika add_xp tidak menerimanya.
    # Untuk konsistensi, kita pastikan user object diteruskan ke check_and_award_new_badges.
    # gamification_service.check_and_award_new_badges(db=db, user=author) # Jika add_xp tidak melakukannya

    db.commit()
    db.refresh(db_post)
    return schemas.PostRead.from_orm(db_post)


@router.get("/posts", response_model=List[schemas.PostRead])
def read_forum_posts(
    skip: int = 0,
    limit: int = 20,
    # Tambahkan filter lain jika perlu, misal: category: Optional[str] = None
    db: Session = Depends(get_db)
):
    """
    Mengambil daftar postingan forum dengan paginasi.
    Secara default diurutkan berdasarkan tanggal pembuatan terbaru.
    """
    posts = db.query(models.ForumPost)\
              .order_by(models.ForumPost.created_at.desc())\
              .offset(skip)\
              .limit(limit)\
              .all()
    return [schemas.PostRead.from_orm(post) for post in posts]


@router.get("/posts/{post_id}", response_model=schemas.PostReadWithReplies)
def read_single_forum_post(post_id: int, db: Session = Depends(get_db)):
    """
    Mengambil satu postingan forum berdasarkan ID, beserta semua balasannya.
    Balasan di-load menggunakan eager loading.
    """
    # Menggunakan joinedload atau selectinload untuk efisiensi pengambilan relasi
    post = db.query(models.ForumPost)\
             .options(selectinload(models.ForumPost.replies).selectinload(models.ForumReply.author))\
             .options(joinedload(models.ForumPost.author))\
             .filter(models.ForumPost.id == post_id)\
             .first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Postingan dengan ID {post_id} tidak ditemukan.")
    return schemas.PostReadWithReplies.from_orm(post)


@router.put("/posts/{post_id}", response_model=schemas.PostRead)
def update_forum_post(
    post_id: int,
    post_in: schemas.PostUpdate,
    # Di aplikasi nyata, periksa apakah pengguna yang terotentikasi adalah penulis postingan
    # current_user_id: int = Depends(get_current_user_id_placeholder),
    db: Session = Depends(get_db)
):
    """
    Memperbarui postingan forum yang ada.
    Memerlukan otorisasi (pengguna harus menjadi penulis postingan).
    """
    db_post = get_post_or_404(db, post_id)

    # if db_post.author_id != current_user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk mengedit postingan ini.")

    update_data = post_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)
    return schemas.PostRead.from_orm(db_post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forum_post(
    post_id: int,
    # current_user_id: int = Depends(get_current_user_id_placeholder),
    db: Session = Depends(get_db)
):
    """
    Menghapus postingan forum.
    Memerlukan otorisasi (pengguna harus menjadi penulis postingan atau admin).
    """
    db_post = get_post_or_404(db, post_id)

    # if db_post.author_id != current_user_id: # Tambahkan pemeriksaan admin jika perlu
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk menghapus postingan ini.")

    db.delete(db_post)
    db.commit()
    return None # Status 204 No Content


@router.post("/posts/{post_id}/vote", response_model=schemas.PostRead)
def vote_on_post(
    post_id: int,
    vote_value: int = Body(..., embed=True, description="Nilai vote: 1 untuk upvote, -1 untuk downvote (jika diimplementasikan). Saat ini hanya upvote."),
    # user_id: int = Depends(get_current_user_id_placeholder), # Untuk melacak siapa yang vote
    db: Session = Depends(get_db)
):
    """
    Memberikan suara (upvote) pada postingan forum.
    Fitur downvote dan pencegahan double-voting bisa ditambahkan.
    """
    db_post = get_post_or_404(db, post_id)
    if vote_value == 1:
        db_post.upvotes = (db_post.upvotes or 0) + 1
        # Gamifikasi: Penulis postingan mendapatkan XP untuk upvote
        if db_post.author_id:
             gamification_service.add_xp(db=db, user_id=db_post.author_id, points=5) # Misal 5 XP per upvote
    # elif vote_value == -1: # Logika downvote
    #     db_post.downvotes = (db_post.downvotes or 0) + 1
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nilai vote tidak valid. Gunakan 1 untuk upvote.")

    db.commit()
    db.refresh(db_post)
    return schemas.PostRead.from_orm(db_post)


# --- Endpoints untuk Balasan Forum ---

@router.post("/posts/{post_id}/replies", response_model=schemas.ReplyRead, status_code=status.HTTP_201_CREATED)
def create_forum_reply(
    post_id: int,
    reply_in: schemas.ReplyCreate, # ReplyCreate seharusnya tidak butuh post_id lagi karena sudah di path
    author_id: int = Body(..., example=1, description="ID pengguna yang membuat balasan (simulasi)."),
    db: Session = Depends(get_db)
):
    """
    Membuat balasan baru untuk postingan forum.
    `author_id` disimulasikan. `parent_reply_id` opsional untuk balasan berulir.
    """
    # Pastikan postingan ada
    get_post_or_404(db, post_id) # Ini akan raise 404 jika post_id tidak valid

    # Pastikan author ada
    author = db.query(models.User).filter(models.User.id == author_id).first()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pengguna dengan ID {author_id} tidak ditemukan.")

    # Jika ada parent_reply_id, pastikan itu valid dan milik postingan yang sama
    if reply_in.parent_reply_id:
        parent_reply = db.query(models.ForumReply).filter(
            models.ForumReply.id == reply_in.parent_reply_id,
            models.ForumReply.post_id == post_id # Penting: pastikan parent reply ada di post yang sama
        ).first()
        if not parent_reply:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent reply dengan ID {reply_in.parent_reply_id} tidak valid atau bukan milik postingan ini.")

    # Buang post_id dari reply_in jika ada, karena kita dapat dari path
    reply_data = reply_in.model_dump()
    if 'post_id' in reply_data: # Seharusnya tidak ada jika ReplyCreate benar
        del reply_data['post_id']

    db_reply = models.ForumReply(
        **reply_data,
        post_id=post_id,
        author_id=author_id
    )
    db.add(db_reply)

    # Gamifikasi untuk balasan
    gamification_service.add_xp(db=db, user_id=author_id, points=10) # Misal 10 XP per balasan

    db.commit()
    db.refresh(db_reply)
    return schemas.ReplyRead.from_orm(db_reply)


@router.get("/replies/{reply_id}", response_model=schemas.ReplyRead) # Biasanya balasan diambil bersama postingan
def read_single_forum_reply(reply_id: int, db: Session = Depends(get_db)):
    """
    Mengambil satu balasan forum berdasarkan ID.
    (Biasanya balasan diambil sebagai bagian dari postingan).
    """
    reply = get_reply_or_404(db, reply_id)
    return schemas.ReplyRead.from_orm(reply)


@router.put("/replies/{reply_id}", response_model=schemas.ReplyRead)
def update_forum_reply(
    reply_id: int,
    reply_in: schemas.ReplyUpdate,
    # current_user_id: int = Depends(get_current_user_id_placeholder),
    db: Session = Depends(get_db)
):
    """
    Memperbarui balasan forum.
    Memerlukan otorisasi.
    """
    db_reply = get_reply_or_404(db, reply_id)
    # if db_reply.author_id != current_user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk mengedit balasan ini.")

    update_data = reply_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reply, key, value)

    db.commit()
    db.refresh(db_reply)
    return schemas.ReplyRead.from_orm(db_reply)


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forum_reply(
    reply_id: int,
    # current_user_id: int = Depends(get_current_user_id_placeholder),
    db: Session = Depends(get_db)
):
    """
    Menghapus balasan forum.
    Memerlukan otorisasi.
    """
    db_reply = get_reply_or_404(db, reply_id)
    # if db_reply.author_id != current_user_id: # Tambahkan pemeriksaan admin jika perlu
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan untuk menghapus balasan ini.")

    db.delete(db_reply)
    db.commit()
    return None


@router.post("/replies/{reply_id}/vote", response_model=schemas.ReplyRead)
def vote_on_reply(
    reply_id: int,
    vote_value: int = Body(..., embed=True, description="Nilai vote: 1 untuk upvote."),
    # user_id: int = Depends(get_current_user_id_placeholder),
    db: Session = Depends(get_db)
):
    """
    Memberikan suara (upvote) pada balasan forum.
    """
    db_reply = get_reply_or_404(db, reply_id)
    if vote_value == 1:
        db_reply.upvotes = (db_reply.upvotes or 0) + 1
        # Gamifikasi: Penulis balasan mendapatkan XP untuk upvote
        if db_reply.author_id:
             gamification_service.add_xp(db=db, user_id=db_reply.author_id, points=2) # Misal 2 XP per upvote balasan
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nilai vote tidak valid. Gunakan 1 untuk upvote.")

    db.commit()
    db.refresh(db_reply)
    return schemas.ReplyRead.from_orm(db_reply)
```

Catatan penting:
*   **Struktur CRUD**: Menyediakan endpoint dasar untuk membuat, membaca, memperbarui, dan menghapus postingan dan balasan.
*   **Simulasi Author ID**: Untuk `create_forum_post` dan `create_forum_reply`, `author_id` saat ini disimulasikan sebagai bagian dari body request. Dalam aplikasi produksi, ini akan diambil dari token otentikasi pengguna yang login.
*   **Otorisasi**: Komentar placeholder ditambahkan di mana pemeriksaan otorisasi (misalnya, apakah pengguna adalah penulis konten sebelum mengedit/menghapus) harus dilakukan.
*   **Eager Loading**: Saat mengambil satu postingan (`GET /posts/{post_id}`), `selectinload` dan `joinedload` digunakan untuk memuat balasan dan penulis secara efisien.
*   **Voting**: Endpoint dasar untuk upvote pada postingan dan balasan. Fitur seperti mencegah vote ganda atau downvote belum diimplementasikan.
*   **Gamifikasi Terintegrasi**: Panggilan ke `gamification_service.add_xp` ditambahkan saat membuat postingan/balasan dan saat menerima upvote.
*   **Balasan Berulir**: Pembuatan balasan mendukung `parent_reply_id`. Pengambilan balasan berulir secara efisien dalam `GET /posts/{post_id}` mungkin memerlukan query rekursif atau penyesuaian lebih lanjut jika kedalamannya besar, tetapi skema `PostReadWithReplies` dan `SimpleReplyRead` mencoba menyederhanakan ini untuk tampilan awal.

Langkah selanjutnya adalah menyertakan router ini di `main.py`.
