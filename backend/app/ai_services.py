import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

from .schemas import Curriculum, Module, Topic # Pastikan path impor ini benar
from sentence_transformers import SentenceTransformer # Untuk embedding
from typing import List, Dict, Any, Optional # Tambahkan Optional

# Muat variabel lingkungan dari .env jika ada (terutama untuk pengembangan lokal)
load_dotenv()

# Inisialisasi model embedding Sentence Transformer
# Model ini akan dimuat sekali saat modul diimpor dan digunakan kembali.
# Ini menghemat waktu pemuatan model pada setiap panggilan fungsi.
# Pastikan model 'all-MiniLM-L6-v2' sudah di-cache atau dapat diunduh oleh lingkungan.
# Dimensi embedding untuk 'all-MiniLM-L6-v2' adalah 384.
try:
    embedding_model_name = 'all-MiniLM-L6-v2'
    embedding_model = SentenceTransformer(embedding_model_name)
    print(f"Model Sentence Transformer '{embedding_model_name}' berhasil dimuat.")
except Exception as e:
    print(f"PERINGATAN PENTING: Gagal memuat model Sentence Transformer '{embedding_model_name}': {e}")
    print("Fungsi get_embedding tidak akan berfungsi. Pastikan model tersedia atau ada koneksi internet untuk mengunduhnya.")
    embedding_model = None # Set ke None jika gagal dimuat

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Ini akan menyebabkan error jika kunci tidak disetel.
    # Dalam aplikasi produksi, Anda mungkin ingin menangani ini dengan cara yang berbeda,
    # misalnya, dengan menonaktifkan fitur AI atau memberikan pesan error yang lebih ramah.
    print("PERINGATAN: GEMINI_API_KEY tidak disetel di variabel lingkungan.")
    # raise ValueError("GEMINI_API_KEY tidak disetel di variabel lingkungan.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Konfigurasi untuk model generatif
# Pilih model yang sesuai, misalnya 'gemini-pro' untuk tugas teks kompleks.
# Untuk output JSON, model yang lebih baru mungkin memiliki dukungan yang lebih baik.
# 'gemini-1.5-flash' atau 'gemini-1.5-pro' mungkin pilihan yang baik jika tersedia dan mendukung output JSON.
# Untuk saat ini, kita akan menggunakan 'gemini-pro' sebagai contoh umum.
GENERATION_CONFIG = {
  "temperature": 0.7, # Sedikit kreatif tapi tidak terlalu acak
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 8192, # Sesuaikan sesuai kebutuhan
}

SAFETY_SETTINGS = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

# Inisialisasi model Gemini
# Kita akan menginisialisasi model di dalam fungsi untuk memastikan konfigurasi terbaru digunakan jika ada perubahan.
# Atau, Anda dapat menginisialisasinya secara global jika konfigurasi tidak berubah.

def parse_gemini_json_response(response_text: str) -> Dict[str, Any]:
    """
    Mencoba mem-parse teks respons dari Gemini yang diharapkan dalam format JSON.
    Menghapus ```json ... ``` jika ada.
    """
    try:
        # Hapus backtick dan penanda 'json' jika model mengembalikannya
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:-3].strip()
        elif response_text.strip().startswith("```"):
             response_text = response_text.strip()[3:-3].strip()
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Gemini response: {e}")
        print(f"Response text was: {response_text}")
        raise ValueError(f"Gagal mem-parse output JSON dari AI: {response_text}") from e

async def generate_curriculum_from_goal(goal: str) -> Curriculum:
    """
    Menghasilkan struktur kurikulum pembelajaran berdasarkan tujuan (goal) yang diberikan pengguna,
    menggunakan Google Gemini API dengan prompt chaining.
    """
    if not GEMINI_API_KEY:
        # Mengembalikan struktur kosong atau error jika API key tidak ada
        # return Curriculum(goal=goal, title=f"Kurikulum untuk: {goal}", description="Kunci API Gemini tidak dikonfigurasi.", modules=[])
        # Untuk pengembangan, kita akan raise error agar lebih jelas.
        raise ValueError("GEMINI_API_KEY tidak dikonfigurasi. Tidak dapat menghasilkan kurikulum.")

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest", # Gunakan model yang mendukung output JSON jika memungkinkan
        generation_config=GENERATION_CONFIG,
        safety_settings=SAFETY_SETTINGS,
        # system_instruction="Anda adalah asisten AI yang ahli dalam merancang kurikulum pembelajaran. Jawab selalu dalam format JSON yang valid."
    )

    # Langkah 1: Hasilkan judul-judul modul dari tujuan (goal)
    # ----------------------------------------------------
    prompt_step1 = f"""
    Anda adalah seorang perancang kurikulum ahli.
    Berdasarkan tujuan pembelajaran pengguna berikut: "{goal}",
    pecah tujuan tersebut menjadi daftar judul modul pembelajaran tingkat tinggi yang logis dan berurutan.
    Setiap judul modul harus ringkas dan jelas.
    Kembalikan HANYA daftar string JSON dari judul-judul modul tersebut.

    Contoh jika tujuannya adalah "Belajar memasak masakan Italia dasar":
    ["Pengenalan Masakan Italia dan Peralatan Dasar", "Teknik Memasak Pasta Sempurna", "Saus Tomat Klasik dan Variasinya", "Hidangan Pembuka dan Salad Italia", "Hidangan Penutup Italia Populer"]

    Tujuan pengguna: "{goal}"
    Daftar judul modul (JSON):
    """
    print(f"DEBUG: Prompt Step 1:\n{prompt_step1}")

    module_titles_str_list: List[str] = []
    try:
        response_step1 = await model.generate_content_async(prompt_step1)
        print(f"DEBUG: Response Step 1 (text): {response_step1.text}")
        # Asumsikan responsnya adalah daftar string JSON, atau string yang berisi daftar JSON
        parsed_titles_json = parse_gemini_json_response(response_step1.text)
        if isinstance(parsed_titles_json, list) and all(isinstance(title, str) for title in parsed_titles_json):
            module_titles_str_list = parsed_titles_json
        else:
            raise ValueError("Output dari langkah 1 tidak menghasilkan daftar judul modul yang valid.")

        if not module_titles_str_list:
             # Fallback jika AI tidak menghasilkan judul, mungkin karena tujuan terlalu sempit
             # Atau coba prompt yang berbeda/lebih sederhana
             print(f"PERINGATAN: Langkah 1 tidak menghasilkan judul modul untuk tujuan: {goal}. Mencoba fallback.")
             # Anda bisa mencoba prompt alternatif di sini atau mengembalikan error/kurikulum kosong
             # Untuk sekarang, kita akan lanjutkan dengan list kosong, yang akan menghasilkan kurikulum kosong.

    except Exception as e:
        print(f"Error pada Langkah 1 (Generasi Judul Modul): {e}")
        # Anda mungkin ingin mengembalikan error HTTP yang sesuai di endpoint
        # atau kurikulum default jika terjadi kesalahan.
        # Untuk sekarang, kita akan re-raise atau biarkan menghasilkan kurikulum kosong.
        raise RuntimeError(f"Gagal menghasilkan judul modul dari AI: {e}") from e

    # Langkah 2: Hasilkan detail untuk setiap modul
    # --------------------------------------------
    generated_modules: List[Module] = []
    for module_title in module_titles_str_list:
        prompt_step2 = f"""
        Anda adalah seorang perancang kurikulum ahli.
        Untuk sebuah modul pembelajaran dengan judul "{module_title}", yang merupakan bagian dari kurikulum untuk mencapai tujuan utama "{goal}", hasilkan detail berikut dalam format JSON yang ketat:
        - "title": (string) Judul modul (gunakan kembali judul yang diberikan: "{module_title}").
        - "description": (string) Deskripsi singkat dan menarik tentang modul ini (2-3 kalimat).
        - "learning_objectives": (list of strings) Daftar 3-5 tujuan pembelajaran utama yang akan dicapai siswa setelah menyelesaikan modul ini.
        - "topics": (list of objects) Daftar topik utama yang akan dibahas. Setiap objek topik harus memiliki:
            - "title": (string) Judul topik yang spesifik.
            - "description": (string, opsional) Deskripsi singkat 1-2 kalimat tentang topik tersebut.
        - "keywords": (list of strings) Daftar 3-5 kata kunci yang relevan dengan konten modul ini.

        Pastikan output adalah objek JSON tunggal yang valid dan sesuai dengan struktur yang diminta. Jangan sertakan teks atau penjelasan lain di luar objek JSON.

        Contoh struktur JSON untuk satu modul:
        {{
          "title": "Contoh Judul Modul",
          "description": "Deskripsi contoh modul ada di sini.",
          "learning_objectives": ["Belajar A", "Memahami B", "Menerapkan C"],
          "topics": [
            {{"title": "Topik 1.1", "description": "Detail untuk topik 1.1"}},
            {{"title": "Topik 1.2", "description": "Detail untuk topik 1.2"}}
          ],
          "keywords": ["kata kunci1", "kata kunci2", "contoh"]
        }}

        Judul Modul Saat Ini: "{module_title}"
        Tujuan Utama Kurikulum: "{goal}"

        Output JSON untuk modul "{module_title}":
        """
        print(f"DEBUG: Prompt Step 2 (untuk modul '{module_title}'):\n{prompt_step2[:500]}...") # Print sebagian prompt

        try:
            # Pastikan menggunakan model yang dikonfigurasi untuk JSON jika ada
            # Beberapa model Gemini mungkin memerlukan konfigurasi khusus untuk output JSON (misalnya, melalui response_mime_type)
            # Jika model Anda mendukung, tambahkan: response_mime_type="application/json" di generation_config atau pemanggilan model
            # Saat ini, kita akan mengandalkan parsing manual dari teks.

            # model_for_json = genai.GenerativeModel(
            #     model_name="gemini-1.5-flash-latest", # atau model lain yang lebih baik untuk JSON
            #     generation_config=GENERATION_CONFIG_JSON, # jika ada config khusus JSON
            #     safety_settings=SAFETY_SETTINGS,
            #     # system_instruction="Anda adalah asisten AI yang ahli dalam merancang kurikulum pembelajaran. Jawab selalu dalam format JSON yang valid dan sesuai skema yang diberikan."
            # )
            # response_step2 = await model_for_json.generate_content_async(prompt_step2)

            # Untuk saat ini, kita gunakan model yang sama
            response_step2 = await model.generate_content_async(prompt_step2)

            print(f"DEBUG: Response Step 2 (untuk modul '{module_title}', text): {response_step2.text}")

            module_data_json = parse_gemini_json_response(response_step2.text)

            # Validasi dengan Pydantic (jika tidak, akan error saat pembuatan instance Module)
            # Pastikan semua field yang dibutuhkan ada dan tipenya benar
            # Pydantic akan melakukan validasi saat membuat instance Module
            current_module = Module(**module_data_json)
            generated_modules.append(current_module)

        except Exception as e:
            print(f"Error pada Langkah 2 (Generasi Detail Modul untuk '{module_title}'): {e}")
            # Anda bisa memilih untuk melewati modul ini dan melanjutkan,
            # atau menghentikan seluruh proses.
            # Untuk sekarang, kita akan mencatat error dan melanjutkan (modul ini tidak akan ditambahkan).
            # Jika ini sering terjadi, prompt atau model mungkin perlu penyesuaian.
            # Atau, tambahkan modul placeholder:
            # generated_modules.append(Module(title=module_title, description=f"Gagal menghasilkan detail untuk modul ini: {e}", topics=[], learning_objectives=[], keywords=[]))
            continue # Lanjutkan ke judul modul berikutnya


    # Buat objek Kurikulum akhir
    # Anda mungkin ingin AI menghasilkan judul dan deskripsi kurikulum secara keseluruhan juga.
    # Untuk saat ini, kita buat secara manual berdasarkan goal.
    curriculum_title = f"Kurikulum Pembelajaran untuk: {goal}"
    curriculum_description = f"Kurikulum ini dirancang untuk membantu Anda mencapai tujuan: '{goal}'. Ini mencakup beberapa modul yang akan memandu Anda melalui berbagai topik dan konsep penting."

    if not generated_modules and module_titles_str_list:
        # Jika ada judul modul tetapi tidak ada modul yang berhasil dibuat detailnya
        curriculum_description += " Sayangnya, terjadi kesalahan saat menghasilkan detail untuk modul-modul tersebut."
    elif not module_titles_str_list:
        curriculum_description = f"Tidak dapat membuat modul untuk tujuan: '{goal}'. Silakan coba tujuan yang lebih spesifik atau periksa konfigurasi AI."


    final_curriculum = Curriculum(
        goal=goal,
        title=curriculum_title,
        description=curriculum_description,
        modules=generated_modules
    )

    return final_curriculum

# Contoh penggunaan (untuk pengujian lokal jika file ini dijalankan langsung):
# if __name__ == "__main__":
#     import asyncio
#     async def main_test():
#         # Pastikan GEMINI_API_KEY Anda disetel di .env atau lingkungan Anda
#         if not GEMINI_API_KEY:
#             print("Harap setel GEMINI_API_KEY Anda di file .env untuk menjalankan tes ini.")
#             return

#         test_goal = "Belajar dasar-dasar FastAPI untuk membuat REST API dengan Python"
#         print(f"Menghasilkan kurikulum untuk tujuan: {test_goal}")
#         try:
#             curriculum_result = await generate_curriculum_from_goal(test_goal)
#             print("\n--- Hasil Kurikulum ---")
#             print(curriculum_result.model_dump_json(indent=2))
#         except Exception as e:
#             print(f"Terjadi kesalahan selama pengujian: {e}")

#     asyncio.run(main_test())


def get_embedding(text: str) -> Optional[List[float]]:
    """
    Menghasilkan embedding vektor untuk teks yang diberikan menggunakan model Sentence Transformer.

    Args:
        text: Teks input yang akan di-embed.

    Returns:
        Daftar float yang mewakili embedding vektor (384 dimensi untuk 'all-MiniLM-L6-v2'),
        atau None jika model embedding tidak berhasil dimuat atau teks kosong.
    """
    if embedding_model is None:
        print("Error: Model embedding tidak tersedia. Tidak dapat menghasilkan embedding.")
        return None
    if not text or not text.strip():
        print("Peringatan: Teks input untuk embedding kosong atau hanya berisi spasi.")
        return None # Atau kembalikan embedding untuk string kosong jika model mendukungnya secara berbeda

    try:
        # Model SentenceTransformer.encode() mengembalikan array NumPy secara default.
        # Kita perlu mengonversinya ke daftar Python standar untuk kompatibilitas JSON dan pgvector.
        embedding_vector = embedding_model.encode(text)
        return embedding_vector.tolist() # Konversi numpy.ndarray ke list[float]
    except Exception as e:
        print(f"Error saat menghasilkan embedding untuk teks '{text[:50]}...': {e}")
        return None
```

Beberapa catatan penting tentang implementasi ini:
*   **Kunci API**: Kode ini mengharapkan `GEMINI_API_KEY` diatur dalam variabel lingkungan.
*   **Pemilihan Model**: Saya menggunakan `gemini-1.5-flash-latest` sebagai contoh. Anda mungkin perlu menyesuaikannya berdasarkan model yang tersedia untuk Anda dan yang paling cocok untuk menghasilkan JSON. Model "Pro" biasanya lebih mumpuni.
*   **Output JSON dari Gemini**: Saya telah menyertakan fungsi `parse_gemini_json_response` untuk mencoba membersihkan output JSON jika model membungkusnya dengan ```json ... ```. Model Gemini yang lebih baru dan konfigurasi yang tepat (seperti `response_mime_type="application/json"` jika didukung oleh pustaka dan model) dapat menyederhanakan ini. Untuk sekarang, saya mengandalkan parsing teks.
*   **Prompt Engineering**: Prompt yang saya buat adalah titik awal. Prompt ini mungkin memerlukan banyak penyempurnaan dan pengujian untuk mendapatkan hasil yang konsisten dan berkualitas tinggi. Struktur JSON yang diminta dalam prompt harus dijaga seketat mungkin.
*   **Error Handling**: Saya telah menyertakan beberapa blok `try-except` dasar. Dalam aplikasi produksi, Anda memerlukan strategi penanganan error yang lebih kuat.
*   **Asinkron**: Fungsi `generate_curriculum_from_goal` dibuat `async` karena pustaka `google-generativeai` mendukung panggilan `generate_content_async`. Ini cocok untuk FastAPI.
*   **Debugging**: Saya telah menyertakan beberapa pernyataan `print` untuk debug. Ini harus dihapus atau diganti dengan logging yang tepat dalam produksi.
*   **Validasi Pydantic**: Pembuatan instance `Module(**module_data_json)` secara implisit akan memvalidasi data yang diterima dari Gemini terhadap skema `Module`. Jika ada ketidakcocokan, ini akan memunculkan error.

Langkah selanjutnya adalah membuat endpoint API di `backend/app/main.py` yang menggunakan layanan ini.
