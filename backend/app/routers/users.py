from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, models, user_service, gamification_service # Menggunakan .. untuk impor dari direktori induk (app)
from ..database import get_db
from passlib.context import CryptContext # Untuk hashing password

router = APIRouter(
    prefix="/users",
    tags=["Users & Gamification"], # Menggabungkan tag untuk kesederhanaan saat ini
    responses={404: {"description": "Not found"}},
)

# Pindahkan ini ke file auth_service.py atau user_service.py yang lebih lengkap di masa depan
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Membuat pengguna baru.
    **Catatan:** Ini adalah implementasi dasar tanpa otentikasi atau manajemen sesi penuh.
    """
    db_user_by_email = user_service.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
    db_user_by_username = user_service.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username sudah digunakan.")

    hashed_password = get_password_hash(user.password)
    # Buat objek User model, bukan langsung dari Pydantic untuk hashing
    new_db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        profile_picture_url=user.profile_picture_url,
        xp_points=0, # Default XP saat pembuatan
        streak_days=0 # Default streak
    )
    db.add(new_db_user)
    db.commit()
    db.refresh(new_db_user)
    return schemas.UserRead.from_orm(new_db_user)

@router.get("/leaderboard", response_model=List[schemas.UserPublic])
def get_leaderboard_endpoint(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Mengambil leaderboard pengguna berdasarkan poin XP.
    """
    leaderboard = user_service.get_users_leaderboard(db, skip=skip, limit=limit)
    return leaderboard

@router.get("/{user_id}", response_model=schemas.UserReadWithBadges) # Menggunakan UserReadWithBadges
def read_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Mengambil detail pengguna tertentu beserta lencana yang dimiliki.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    # user_service.get_user(db, user_id=user_id) # Ini mengembalikan UserRead, bukan User model
    if db_user is None:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan.")
    return schemas.UserReadWithBadges.from_orm(db_user) # Pastikan UserReadWithBadges bisa handle relasi badges


@router.post("/{user_id}/add-xp", response_model=schemas.UserRead)
def add_xp_to_user_endpoint(user_id: int, points: int = 10, db: Session = Depends(get_db)):
    """
    **Endpoint Pengujian:** Menambahkan poin XP ke pengguna tertentu.
    """
    updated_user = gamification_service.add_xp(db=db, user_id=user_id, points=points)
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"Pengguna dengan ID {user_id} tidak ditemukan atau gagal update XP.")
    return updated_user

@router.get("/{user_id}/check-badges", response_model=List[schemas.UserBadgeRead])
def check_user_badges_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    **Endpoint Pengujian:** Memeriksa dan memberikan lencana baru untuk pengguna tertentu.
    Mengembalikan daftar lencana yang BARU diberikan dalam panggilan ini.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Pengguna dengan ID {user_id} tidak ditemukan.")

    newly_awarded_user_badges = gamification_service.check_and_award_new_badges(db=db, user=user)
    # Skema UserBadgeRead mengharapkan objek UserBadge, bukan hanya BadgeRead
    # jadi kita perlu memastikan ini dikonversi dengan benar jika diperlukan
    # atau UserBadgeRead.from_orm(user_badge_model_instance)
    return [schemas.UserBadgeRead.from_orm(ub) for ub in newly_awarded_user_badges]


# Endpoint untuk menginisialisasi lencana (hanya untuk admin atau setup awal)
@router.post("/init-badges", summary="Inisialisasi Lencana Default (Admin/Setup)", include_in_schema=False) # Sembunyikan dari docs publik
def initialize_default_badges_endpoint(db: Session = Depends(get_db)):
    # Di aplikasi nyata, ini harus dilindungi dan hanya bisa diakses oleh admin.
    try:
        gamification_service.initialize_badges(db)
        return {"message": "Proses inisialisasi lencana default telah dijalankan."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menginisialisasi lencana: {str(e)}")

```
Catatan:
*   Saya membuat endpoint `POST /users/` dasar untuk membuat pengguna. Ini **tidak aman untuk produksi** tanpa otentikasi dan manajemen token yang tepat, tetapi diperlukan untuk membuat data pengguna untuk forum dan leaderboard.
*   Endpoint `/leaderboard` menggunakan `user_service.get_users_leaderboard`.
*   Endpoint `/users/{user_id}` mengambil detail pengguna termasuk lencana.
*   Endpoint pengujian `/users/{user_id}/add-xp` dan `/{user_id}/check-badges` ditambahkan untuk memicu logika gamifikasi.
*   Endpoint `/init-badges` ditambahkan untuk memudahkan pengisian tabel `badges` dengan data awal, sebaiknya ini dilindungi atau hanya dijalankan sekali.

Selanjutnya, saya akan membuat `backend/app/routers/forum.py`.
