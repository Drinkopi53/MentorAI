from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from .database import Base # Impor Base dari database.py
# Enum ContentType mungkin tidak diperlukan di sini kecuali User memiliki preferensi konten

# Model Pengguna (User)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    full_name = Column(String(255), nullable=True)
    profile_picture_url = Column(String(1024), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    # is_superuser = Column(Boolean, default=False) # Jika Anda memerlukan peran admin

    # Kolom Gamifikasi
    xp_points = Column(Integer, default=0, nullable=False, index=True)
    streak_days = Column(Integer, default=0, nullable=False)

    # Hubungan
    badges = relationship("UserBadge", back_populates="user")
    posts = relationship("ForumPost", back_populates="author")
    replies = relationship("ForumReply", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# Model Lencana (Badge)
class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(1024), nullable=True) # URL ke gambar ikon lencana
    criteria = Column(Text, nullable=True) # Deskripsi kriteria untuk mendapatkan lencana

    # Hubungan
    user_badges = relationship("UserBadge", back_populates="badge_info")

    def __repr__(self):
        return f"<Badge(id={self.id}, name='{self.name}')>"

# Model Lencana Pengguna (UserBadges) - Tabel join untuk hubungan many-to-many User dan Badge
class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False, index=True)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Hubungan
    user = relationship("User", back_populates="badges")
    badge_info = relationship("Badge", back_populates="user_badges")

    def __repr__(self):
        return f"<UserBadge(user_id={self.user_id}, badge_id={self.badge_id}, awarded_at='{self.awarded_at}')>"

# Model Postingan Forum (ForumPosts)
class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(512), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    upvotes = Column(Integer, default=0, nullable=False)
    # downvotes = Column(Integer, default=0) # Jika Anda ingin downvote terpisah
    # views = Column(Integer, default=0) # Jika Anda ingin melacak tampilan
    # category_id = Column(Integer, ForeignKey("forum_categories.id"), nullable=True) # Jika ada kategori

    # Hubungan
    author = relationship("User", back_populates="posts")
    replies = relationship("ForumReply", back_populates="post", cascade="all, delete-orphan", order_by="ForumReply.created_at")
    # category = relationship("ForumCategory", back_populates="posts")

    def __repr__(self):
        return f"<ForumPost(id={self.id}, title='{self.title}', author_id={self.author_id})>"

# Model Balasan Forum (ForumReplies)
class ForumReply(Base):
    __tablename__ = "forum_replies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # Untuk balasan berulir (nested replies)
    parent_reply_id = Column(Integer, ForeignKey("forum_replies.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    upvotes = Column(Integer, default=0, nullable=False)

    # Hubungan
    post = relationship("ForumPost", back_populates="replies")
    author = relationship("User", back_populates="replies")

    # Hubungan untuk balasan berulir
    parent_reply = relationship("ForumReply", remote_side=[id], back_populates="child_replies")
    child_replies = relationship("ForumReply", back_populates="parent_reply", cascade="all, delete-orphan", order_by="ForumReply.created_at")

    def __repr__(self):
        return f"<ForumReply(id={self.id}, post_id={self.post_id}, author_id={self.author_id}, parent_id={self.parent_reply_id})>"

# Anda mungkin ingin menambahkan tabel lain seperti ForumCategory, UserVotes (untuk melacak siapa yang vote apa), dll.
# tergantung pada kedalaman fitur yang diinginkan.
```

Poin-poin penting dalam file `models.py` ini:
*   **`User` Model**:
    *   Kolom dasar seperti `username`, `email`, `hashed_password`, `created_at`.
    *   Kolom gamifikasi yang diminta: `xp_points` (default 0) dan `streak_days` (default 0).
    *   Hubungan ke `UserBadge`, `ForumPost`, dan `ForumReply`.
*   **`Badge` Model**: Menyimpan informasi tentang lencana yang tersedia.
*   **`UserBadge` Model**: Tabel join untuk hubungan many-to-many antara `User` dan `Badge`, mencatat kapan lencana diberikan.
*   **`ForumPost` Model**:
    *   Menyimpan postingan forum dengan `author_id`, `title`, `content`, `created_at`, `upvotes`.
    *   Hubungan ke `User` (penulis) dan `ForumReply` (balasan untuk postingan ini). `cascade="all, delete-orphan"` pada balasan berarti jika postingan dihapus, semua balasannya juga akan dihapus.
*   **`ForumReply` Model**:
    *   Menyimpan balasan untuk postingan, termasuk `post_id`, `author_id`, `content`.
    *   `parent_reply_id`: Kolom kunci asing self-referential untuk mendukung balasan berulir (nested).
    *   Hubungan ke `ForumPost`, `User`, dan juga ke dirinya sendiri untuk `parent_reply` dan `child_replies`.

Semua model ini mewarisi dari `Base` yang didefinisikan di `database.py`, sehingga mereka akan disertakan saat `Base.metadata.create_all(bind=engine)` dipanggil.
