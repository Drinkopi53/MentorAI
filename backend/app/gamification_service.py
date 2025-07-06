from sqlalchemy.orm import Session
from typing import List, Optional

from .models import User, Badge, UserBadge # Impor model database
from .schemas import UserRead, BadgeRead, UserBadgeRead # Impor skema Pydantic jika perlu return type

# --- Definisi Lencana (Contoh) ---
# Dalam aplikasi nyata, ini mungkin disimpan di database dan dikelola oleh admin.
# Atau bisa juga dikonfigurasi dalam file konfigurasi.
# Untuk contoh ini, kita akan hardcode beberapa definisi lencana.
# Kita akan mengasumsikan ada tabel 'badges' yang sudah diisi dengan lencana ini.

# Contoh ID Lencana (sesuaikan dengan ID aktual di tabel 'badges' Anda setelah dibuat)
BADGE_ID_FIRST_XP = 1
BADGE_ID_XP_100 = 2
BADGE_ID_FIRST_POST = 3
# ... dan seterusnya

def add_xp(db: Session, user_id: int, points: int) -> Optional[UserRead]:
    """
    Menambahkan poin XP ke pengguna tertentu dan memeriksa apakah ada lencana baru yang diperoleh.

    Args:
        db: Sesi database SQLAlchemy.
        user_id: ID pengguna yang akan menerima XP.
        points: Jumlah poin XP yang akan ditambahkan.

    Returns:
        Objek User (via UserRead schema) jika pengguna ditemukan dan XP berhasil ditambahkan,
        atau None jika pengguna tidak ditemukan.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"Error: Pengguna dengan ID {user_id} tidak ditemukan saat mencoba menambahkan XP.")
        return None

    user.xp_points = (user.xp_points or 0) + points
    print(f"Menambahkan {points} XP ke pengguna {user.username}. Total XP baru: {user.xp_points}.")

    # Setelah menambahkan XP, periksa apakah ada lencana baru yang diperoleh
    # new_badges_awarded = check_and_award_new_badges(db=db, user_id=user_id, current_xp=user.xp_points)
    # Jika Anda ingin mengembalikan informasi lencana yang baru diberikan, Anda bisa melakukannya di sini.

    try:
        db.commit()
        db.refresh(user)
        # Panggil check_and_award_new_badges setelah commit XP berhasil
        check_and_award_new_badges(db=db, user=user)
        return UserRead.from_orm(user) # Kembalikan data pengguna yang diperbarui
    except Exception as e:
        db.rollback()
        print(f"Error saat commit penambahan XP untuk user_id {user_id}: {e}")
        return None


def award_badge_if_not_exists(db: Session, user: User, badge_id: int) -> Optional[UserBadge]:
    """
    Memberikan lencana kepada pengguna jika mereka belum memilikinya.

    Args:
        db: Sesi database SQLAlchemy.
        user: Objek User SQLAlchemy.
        badge_id: ID lencana yang akan diberikan.

    Returns:
        Objek UserBadge jika lencana berhasil diberikan,
        None jika pengguna sudah memiliki lencana tersebut atau lencana tidak ditemukan.
    """
    # Periksa apakah pengguna sudah memiliki lencana ini
    existing_user_badge = db.query(UserBadge).filter(
        UserBadge.user_id == user.id,
        UserBadge.badge_id == badge_id
    ).first()

    if existing_user_badge:
        # print(f"Pengguna {user.username} sudah memiliki lencana ID {badge_id}.")
        return None # Pengguna sudah memiliki lencana ini

    # Periksa apakah lencana dengan ID tersebut ada
    badge_to_award = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge_to_award:
        print(f"Peringatan: Lencana dengan ID {badge_id} tidak ditemukan di database. Tidak dapat memberikan kepada pengguna {user.username}.")
        return None

    new_user_badge = UserBadge(user_id=user.id, badge_id=badge_id)
    db.add(new_user_badge)
    # Commit akan dilakukan oleh fungsi pemanggil atau di akhir check_and_award_new_badges

    print(f"Lencana '{badge_to_award.name}' (ID: {badge_id}) diberikan kepada pengguna {user.username}!")
    return new_user_badge


def check_and_award_new_badges(db: Session, user: User) -> List[UserBadge]:
    """
    Memeriksa dan memberikan lencana baru kepada pengguna berdasarkan kriteria tertentu
    (misalnya, total XP, jumlah postingan, dll.).
    Fungsi ini dipanggil setelah suatu aksi yang mungkin memicu perolehan lencana (misalnya, add_xp, create_post).

    Args:
        db: Sesi database SQLAlchemy.
        user: Objek User SQLAlchemy yang diperiksa.

    Returns:
        Daftar objek UserBadge yang baru diberikan.
    """
    if not user:
        return []

    awarded_badges_in_this_check: List[UserBadge] = []

    # Kriteria 1: Lencana untuk XP pertama (misalnya, jika XP > 0)
    if user.xp_points > 0:
        badge = award_badge_if_not_exists(db, user, BADGE_ID_FIRST_XP)
        if badge: awarded_badges_in_this_check.append(badge)

    # Kriteria 2: Lencana untuk mencapai 100 XP
    if user.xp_points >= 100:
        badge = award_badge_if_not_exists(db, user, BADGE_ID_XP_100)
        if badge: awarded_badges_in_this_check.append(badge)

    # Kriteria 3: Lencana untuk postingan forum pertama
    # Ini memerlukan query ke tabel ForumPost. Kita asumsikan ada cara untuk mengeceknya.
    # Misalnya, jika user.posts adalah relationship yang valid dan sudah di-load atau bisa di-query:
    # if user.posts and len(user.posts) >= 1: # Ini asumsi, mungkin perlu query eksplisit
    # Atau, Anda bisa meneruskan argumen tambahan seperti `post_count` jika relevan.
    # Untuk saat ini, kita akan fokus pada XP.
    # Jika Anda ingin mengimplementasikan ini, Anda perlu memastikan `user.posts` terisi atau melakukan query:
    # post_count = db.query(ForumPost).filter(ForumPost.author_id == user.id).count()
    # if post_count >= 1:
    #     badge = award_badge_if_not_exists(db, user, BADGE_ID_FIRST_POST)
    #     if badge: awarded_badges_in_this_check.append(badge)


    # Tambahkan kriteria lencana lainnya di sini...
    # Misalnya, untuk streak:
    # if user.streak_days >= 7:
    #     badge = award_badge_if_not_exists(db, user, BADGE_ID_STREAK_7_DAYS)
    #     if badge: awarded_badges_in_this_check.append(badge)

    if awarded_badges_in_this_check:
        try:
            db.commit()
            for ub in awarded_badges_in_this_check:
                db.refresh(ub) # Refresh untuk mendapatkan ID dll.
            print(f"Total {len(awarded_badges_in_this_check)} lencana baru berhasil di-commit untuk pengguna {user.username}.")
        except Exception as e:
            db.rollback()
            print(f"Error saat commit lencana baru untuk pengguna {user.username}: {e}")
            return [] # Kembalikan list kosong jika commit gagal

    return awarded_badges_in_this_check


def initialize_badges(db: Session):
    """
    Menginisialisasi tabel 'badges' dengan beberapa lencana default jika belum ada.
    Ini bisa dipanggil sekali saat startup aplikasi atau melalui skrip setup.
    """
    default_badges = [
        {"id": BADGE_ID_FIRST_XP, "name": "Kontributor Awal", "description": "Selamat! Anda mendapatkan XP pertama Anda.", "criteria": "Dapatkan poin XP pertama Anda."},
        {"id": BADGE_ID_XP_100, "name": "Pejuang XP", "description": "Anda telah mencapai 100 Poin Pengalaman!", "criteria": "Kumpulkan 100 XP."},
        {"id": BADGE_ID_FIRST_POST, "name": "Pembicara Publik", "description": "Anda telah membuat postingan forum pertama Anda!", "criteria": "Buat 1 postingan forum."},
        # Tambahkan lencana default lainnya di sini
    ]

    existing_badge_count = db.query(Badge).count()
    if existing_badge_count == 0: # Hanya inisialisasi jika tabel kosong
        print("Menginisialisasi lencana default ke database...")
        for badge_data in default_badges:
            # Cek dulu apakah badge dengan ID atau nama tersebut sudah ada (untuk idempotensi jika dipanggil lagi)
            exists = db.query(Badge).filter(Badge.id == badge_data["id"]).first()
            if not exists:
                new_badge = Badge(**badge_data)
                db.add(new_badge)
        try:
            db.commit()
            print(f"{len(default_badges)} lencana default berhasil ditambahkan.")
        except Exception as e:
            db.rollback()
            print(f"Error saat menginisialisasi lencana default: {e}")
    else:
        print("Tabel lencana sudah berisi data, inisialisasi dilewati.")


# Anda mungkin ingin menambahkan fungsi untuk memperbarui streak_days di sini.
# def update_user_streak(db: Session, user_id: int, last_login_date: datetime.date):
#     user = db.query(User).filter(User.id == user_id).first()
#     if user:
#         today = datetime.date.today()
#         # Logika untuk memeriksa apakah login terakhir adalah kemarin, dll.
#         # ... (implementasi logika streak) ...
#         db.commit()

```
Beberapa poin penting:
*   **`add_xp`**:
    *   Menemukan pengguna berdasarkan `user_id`.
    *   Menambahkan `points` ke `user.xp_points`.
    *   Memanggil `check_and_award_new_badges` setelah XP ditambahkan dan di-commit.
    *   Melakukan commit ke database dan me-refresh objek pengguna.
    *   Mengembalikan data pengguna yang diperbarui (menggunakan skema `UserRead`).
*   **`award_badge_if_not_exists`**:
    *   Fungsi pembantu untuk memberikan lencana tertentu jika pengguna belum memilikinya dan lencana tersebut ada.
*   **`check_and_award_new_badges`**:
    *   Menerima objek `User` SQLAlchemy.
    *   Berisi logika placeholder untuk memberikan lencana berdasarkan total XP. Ini dapat diperluas dengan kriteria lain (misalnya, jumlah postingan, streak, dll.).
    *   Menggunakan `award_badge_if_not_exists` untuk mencegah duplikasi lencana.
    *   Melakukan commit setelah semua pemeriksaan lencana untuk sesi tersebut.
*   **`initialize_badges`**:
    *   Fungsi opsional yang dapat Anda panggil saat startup aplikasi (misalnya, di `main.py` setelah `create_db_and_tables`) untuk mengisi tabel `badges` dengan beberapa data lencana default jika tabel tersebut kosong. Ini berguna untuk pengembangan dan memastikan lencana yang direferensikan oleh ID ada.
*   **Definisi Lencana**: Saya telah menambahkan beberapa konstanta ID lencana sebagai contoh. Dalam aplikasi nyata, Anda mungkin ingin ID ini lebih dinamis atau nama lencana sebagai kunci.
*   **Commit dan Rollback**: Penanganan transaksi dasar (commit, rollback) disertakan.

Layanan ini menyediakan dasar untuk sistem gamifikasi. Logika di `check_and_award_new_badges` perlu diperluas dengan kriteria yang lebih spesifik sesuai kebutuhan aplikasi Anda. Anda juga perlu memanggil `add_xp` dan `check_and_award_new_badges` dari tempat yang sesuai dalam aplikasi Anda (misalnya, setelah pengguna menyelesaikan modul, membuat postingan, login harian, dll.).
