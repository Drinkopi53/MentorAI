from pydantic import BaseModel, Field
from typing import List, Optional

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

# Jika Anda ingin contoh data untuk pengujian atau dokumentasi:
# example_topic = Topic(title="Contoh Topik", description="Ini adalah contoh topik.")
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
