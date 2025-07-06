from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime # Ditambahkan untuk field tanggal

class Topic(BaseModel):
    """
    Mewakili satu topik pembelajaran dalam sebuah modul.
    """
    title: str = Field(..., description="Judul topik.", example="Pengenalan Variabel dalam Python")
    description: Optional[str] = Field(None, description="Deskripsi singkat tentang topik.", example="Memahami apa itu variabel, bagaimana mendeklarasikannya, dan jenis data dasar.")
    # Anda dapat menambahkan bidang lain seperti 'estimated_duration_minutes', 'sub_topics', dll.

class Module(BaseModel):
    """
    Mewakili satu modul dalam kurikulum pembelajaran.
    """
    title: str = Field(..., description="Judul modul.", example="Dasar-Dasar Python")
    description: Optional[str] = Field(None, description="Deskripsi umum tentang apa yang dicakup modul ini.", example="Modul ini mencakup konsep dasar pemrograman Python yang penting untuk pemula.")
    learning_objectives: List[str] = Field(default_factory=list, description="Daftar tujuan pembelajaran untuk modul ini.", example=["Memahami sintaks dasar Python.", "Mampu menulis skrip Python sederhana."])
    topics: List[Topic] = Field(default_factory=list, description="Daftar topik yang dibahas dalam modul ini.")
    keywords: List[str] = Field(default_factory=list, description="Kata kunci yang relevan dengan modul ini.", example=["Python", "Pemrograman", "Variabel", "Loop", "Fungsi"])

class Curriculum(BaseModel):
    """
    Mewakili seluruh kurikulum pembelajaran yang dihasilkan berdasarkan tujuan pengguna.
    """
    goal: str = Field(..., description="Tujuan pembelajaran awal yang diberikan oleh pengguna.", example="Belajar Python untuk analisis data")
    title: str = Field(..., description="Judul keseluruhan untuk kurikulum yang dihasilkan.", example="Kurikulum Pembelajaran Python untuk Analisis Data")
    description: Optional[str] = Field(None, description="Deskripsi singkat tentang kurikulum secara keseluruhan.", example="Kurikulum ini dirancang untuk membimbing Anda dari dasar-dasar Python hingga aplikasi praktis dalam analisis data.")
    modules: List[Module] = Field(default_factory=list, description="Daftar modul yang menyusun kurikulum ini.")
    # Anda dapat menambahkan bidang lain seperti 'total_estimated_duration_hours', 'target_audience', dll.

class CurriculumGoalRequest(BaseModel):
    """
    Model permintaan untuk membuat kurikulum baru.
    """
    goal: str = Field(..., min_length=10, max_length=500, description="Tujuan pembelajaran yang ingin dicapai pengguna.", example="Saya ingin belajar membuat REST API dengan FastAPI dan Python.")


class SearchResultItem(BaseModel):
    """
    Mewakili satu item hasil pencarian konten pembelajaran.
    """
    id: int
    title: Optional[str] = None
    source_url: Optional[str] = None
    content_type: str # Akan menjadi nilai dari enum ContentType
    text_chunk: str
    # Anda bisa menambahkan 'similarity_score' jika dihitung dan ingin ditampilkan
    # similarity_score: Optional[float] = None

    class Config:
        orm_mode = True # Untuk kompatibilitas dengan objek SQLAlchemy


class SearchResponse(BaseModel):
    """
    Model respons untuk hasil pencarian.
    """
    query: str
    results: List[SearchResultItem]

# --- Skema untuk User ---
class UserBase(BaseModel):
    email: str = Field(..., example="user@example.com")
    username: str = Field(..., example="johndoe")
    full_name: Optional[str] = Field(None, example="John Doe")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profile.jpg")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="strongpassword123")

class UserRead(UserBase):
    id: int
    xp_points: int = 0
    streak_days: int = 0
    created_at: datetime # Impor datetime
    is_active: bool = True
    subscription_status: str = Field(default='free', example='free')

    class Config:
        orm_mode = True

class UserPublic(BaseModel): # Untuk leaderboard atau tampilan publik
    id: int
    username: str
    xp_points: int
    profile_picture_url: Optional[str] = None
    subscription_status: str = Field(default='free', example='free') # Mungkin tidak ingin ini publik, tergantung kebutuhan
    # Mungkin tambahkan jumlah lencana atau info publik lainnya

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    # Jangan izinkan update username, xp, streak, password secara langsung melalui ini

# --- Skema untuk Badge ---
class BadgeBase(BaseModel):
    name: str = Field(..., example="Pionir Belajar")
    description: Optional[str] = Field(None, example="Diberikan untuk menyelesaikan modul pertama.")
    icon_url: Optional[str] = Field(None, example="https://example.com/badge_pionir.svg")
    criteria: Optional[str] = Field(None, example="Selesaikan 1 modul.")

class BadgeCreate(BadgeBase):
    pass

class BadgeRead(BadgeBase):
    id: int

    class Config:
        orm_mode = True

# --- Skema untuk UserBadge ---
class UserBadgeRead(BaseModel):
    awarded_at: datetime # Impor datetime
    badge: BadgeRead # Nested skema BadgeRead

    class Config:
        orm_mode = True

# Tambahkan UserRead untuk menyertakan lencana pengguna
class UserReadWithBadges(UserRead):
    badges: List[UserBadgeRead] = []


# --- Skema untuk ForumPost ---
class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, example="Bagaimana cara memulai dengan FastAPI?")
    content: str = Field(..., min_length=20, description="Konten utama postingan forum.")

class PostCreate(PostBase):
    pass # author_id akan diambil dari pengguna yang terotentikasi

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    content: Optional[str] = Field(None, min_length=20)

class PostAuthor(BaseModel): # Skema sederhana untuk info penulis dalam PostRead
    id: int
    username: str
    profile_picture_url: Optional[str] = None
    class Config:
        orm_mode = True

class PostRead(PostBase):
    id: int
    author_id: int
    author: PostAuthor # Informasi penulis yang disederhanakan
    created_at: datetime # Impor datetime
    updated_at: Optional[datetime] = None # Impor datetime
    upvotes: int = 0
    # reply_count: int = 0 # Bisa ditambahkan jika dihitung di query

    class Config:
        orm_mode = True

# --- Skema untuk ForumReply ---
class ReplyBase(BaseModel):
    content: str = Field(..., min_length=1, description="Konten balasan.")

class ReplyCreate(ReplyBase):
    post_id: int # Perlu post_id saat membuat balasan
    parent_reply_id: Optional[int] = None # Untuk balasan berulir

class ReplyUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class ReplyRead(ReplyBase):
    id: int
    post_id: int
    author_id: int
    author: PostAuthor # Informasi penulis yang disederhanakan
    parent_reply_id: Optional[int] = None
    created_at: datetime # Impor datetime
    updated_at: Optional[datetime] = None # Impor datetime
    upvotes: int = 0
    # child_replies: List['ReplyRead'] = [] # Untuk balasan berulir, perlu forward ref atau update_forward_refs()

    class Config:
        orm_mode = True

# Untuk PostReadWithReplies, kita bisa mendefinisikan ReplyRead yang tidak menyertakan child_replies
# untuk menghindari rekursi tak terbatas jika skema dikembalikan langsung, atau menangani kedalaman di query.
# Atau, buat versi sederhana dari ReplyRead untuk PostReadWithReplies.
class SimpleReplyRead(ReplyBase): # Versi sederhana untuk menghindari rekursi dalam PostReadWithReplies
    id: int
    author: PostAuthor
    created_at: datetime
    upvotes: int
    parent_reply_id: Optional[int] = None
    # Tidak ada child_replies di sini untuk menghindari rekursi saat mengambil postingan dengan semua balasan
    class Config:
        orm_mode = True


class PostReadWithReplies(PostRead):
    replies: List[SimpleReplyRead] = [] # Menggunakan SimpleReplyRead

# Memperbarui forward references untuk ReplyRead jika menggunakan self-referencing type hint secara langsung
# ReplyRead.update_forward_refs() # Panggil ini di akhir file jika 'ReplyRead' digunakan di List['ReplyRead']

# Jika Anda ingin contoh data untuk pengujian atau dokumentasi:
# example_topic = Topic(title="Contoh Topik", description="Ini adalah contoh topik.")

# --- Skema untuk Token JWT ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    # Payload yang akan kita masukkan ke dalam JWT dan dapat diekstrak kembali.
    # 'sub' biasanya digunakan untuk subject (misalnya username atau user_id).
    # Kita akan menggunakan user_id sebagai 'sub' untuk identifikasi unik.
    sub: str # Seharusnya user_id, tapi JWT spec sering menggunakan string untuk 'sub'
    user_id: Optional[int] = None # Untuk kemudahan akses setelah decode
    username: Optional[str] = None # Bisa juga disertakan jika berguna
    role: Optional[str] = None # Misal 'free_user', 'premium_user'
    # Anda bisa menambahkan klaim lain seperti 'exp' (expiration time) di sini,
    # tetapi 'exp' biasanya ditangani oleh pustaka JWT saat pembuatan token.
# example_module = Module(
#     title="Contoh Modul",
#     description="Ini adalah contoh modul.",
#     learning_objectives=["Belajar A", "Memahami B"],
#     topics=[example_topic],
#     keywords=["contoh", "pembelajaran"]
# )
# example_curriculum = Curriculum(
#     goal="Belajar membuat contoh Pydantic",
#     title="Kurikulum Contoh Pydantic",
#     description="Kurikulum untuk mendemonstrasikan model Pydantic.",
#     modules=[example_module]
# )
```
