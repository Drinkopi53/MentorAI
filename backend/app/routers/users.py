from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, models, user_service, gamification_service
from ..database import get_db
from ..dependencies import require_active_user, require_premium_user # Impor dependensi otentikasi
from passlib.context import CryptContext
from pydantic import BaseModel # Untuk request body set-subscription

router = APIRouter(
    prefix="/users",
    tags=["Users & Gamification"],
    responses={404: {"description": "Not found"}},
)

# Konteks password (bisa juga di auth_service.py atau user_service.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Endpoint ini tidak memerlukan otentikasi karena untuk membuat pengguna baru
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

# Endpoint ini bisa publik
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

# Endpoint yang memerlukan otentikasi
@router.post("/me/add-xp", response_model=schemas.UserRead, summary="Tambahkan XP ke Pengguna Saat Ini")
def add_xp_to_current_user_endpoint(
    points: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_active_user)
):
    """
    Menambahkan poin XP ke pengguna yang saat ini terotentikasi.
    """
    updated_user = gamification_service.add_xp(db=db, user_id=current_user.id, points=points)
    # add_xp sekarang mengembalikan UserRead, jadi tidak perlu UserRead.from_orm() lagi
    if not updated_user:
        # Ini seharusnya tidak terjadi jika current_user valid, kecuali ada masalah DB
        raise HTTPException(status_code=500, detail="Gagal memperbarui XP pengguna.")
    return updated_user

@router.get("/me/check-badges", response_model=List[schemas.UserBadgeRead], summary="Periksa Lencana untuk Pengguna Saat Ini")
def check_current_user_badges_endpoint(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_active_user)
):
    """
    Memeriksa dan memberikan lencana baru untuk pengguna yang saat ini terotentikasi.
    Mengembalikan daftar lencana yang BARU diberikan dalam panggilan ini.
    """
    # gamification_service.check_and_award_new_badges mengharapkan objek User model
    newly_awarded_user_badges = gamification_service.check_and_award_new_badges(db=db, user=current_user)
    return [schemas.UserBadgeRead.from_orm(ub) for ub in newly_awarded_user_badges]

# Endpoint untuk menginisialisasi lencana (sebaiknya dilindungi oleh peran admin di masa depan)
@router.post("/init-badges", summary="Inisialisasi Lencana Default (Setup)", include_in_schema=False)
def initialize_default_badges_endpoint(db: Session = Depends(get_db)):
    # Di aplikasi nyata, ini harus dilindungi dan hanya bisa diakses oleh admin.
    try:
        gamification_service.initialize_badges(db)
        return {"message": "Proses inisialisasi lencana default telah dijalankan."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menginisialisasi lencana: {str(e)}")

# --- Endpoint untuk Fitur Premium ---
@router.get("/premium-feature", summary="Akses Fitur Premium (Contoh)")
def get_premium_feature_data(current_user: models.User = Depends(require_premium_user)):
    """
    Endpoint contoh yang hanya dapat diakses oleh pengguna dengan status langganan 'premium'.
    """
    return {"message": f"Selamat datang di fitur premium, {current_user.username}! Data rahasia ada di sini.", "user_subscription": current_user.subscription_status}

# --- Endpoint untuk Admin/Pengujian Mengubah Status Langganan ---
class SubscriptionUpdateRequest(BaseModel):
    subscription_status: str # Misal: "free", "premium"

@router.post("/admin/set-subscription/{user_id}", response_model=schemas.UserRead, summary="Set Status Langganan Pengguna (Admin/Pengujian)")
def set_user_subscription_status(
    user_id: int,
    request_body: SubscriptionUpdateRequest,
    db: Session = Depends(get_db),
    # current_admin: models.User = Depends(require_admin_user) # Di aplikasi nyata, ini harus dilindungi admin
    current_user: models.User = Depends(require_active_user) # Untuk sekarang, pengguna aktif bisa mengubah (untuk tes)
):
    """
    **Endpoint Pengujian/Admin:** Mengatur status langganan untuk pengguna tertentu.
    Di aplikasi produksi, endpoint ini harus dilindungi dan hanya dapat diakses oleh admin.
    """
    # Untuk pengujian, kita biarkan pengguna aktif mengubah status pengguna lain.
    # Di produksi, Anda akan memeriksa apakah current_user adalah admin.
    # if not current_user.is_superuser: # Jika Anda punya field is_superuser
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operasi tidak diizinkan.")

    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pengguna dengan ID {user_id} tidak ditemukan.")

    # Validasi status langganan yang masuk (opsional, bisa juga dengan Enum)
    valid_statuses = ["free", "premium", "expired", "premium_plus"] # Contoh
    if request_body.subscription_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Status langganan tidak valid. Pilih dari: {', '.join(valid_statuses)}")

    user_to_update.subscription_status = request_body.subscription_status
    try:
        db.commit()
        db.refresh(user_to_update)
        return schemas.UserRead.from_orm(user_to_update)
    except Exception as e:
        db.rollback()
        print(f"Error saat update status langganan untuk user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Gagal memperbarui status langganan.")

```
Catatan:
*   Saya membuat endpoint `POST /users/` dasar untuk membuat pengguna. Ini **tidak aman untuk produksi** tanpa otentikasi dan manajemen token yang tepat, tetapi diperlukan untuk membuat data pengguna untuk forum dan leaderboard.
*   Endpoint `/leaderboard` menggunakan `user_service.get_users_leaderboard`.
*   Endpoint `/users/{user_id}` mengambil detail pengguna termasuk lencana.
*   Endpoint pengujian `/users/{user_id}/add-xp` dan `/{user_id}/check-badges` ditambahkan untuk memicu logika gamifikasi.
*   Endpoint `/init-badges` ditambahkan untuk memudahkan pengisian tabel `badges` dengan data awal, sebaiknya ini dilindungi atau hanya dijalankan sekali.

Selanjutnya, saya akan membuat `backend/app/routers/forum.py`.
