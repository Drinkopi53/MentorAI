import os
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Muat variabel lingkungan dari .env untuk pengembangan lokal
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def fetch_youtube_videos(keywords: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Mengambil daftar video YouTube berdasarkan kata kunci.

    Args:
        keywords: Daftar string kata kunci untuk pencarian.
        max_results: Jumlah maksimum video yang akan diambil.

    Returns:
        Daftar kamus, masing-masing berisi informasi tentang video
        (videoId, title, description, channelTitle, videoUrl, thumbnailUrl).
        Mengembalikan daftar kosong jika terjadi error atau tidak ada hasil.
    """
    if not YOUTUBE_API_KEY:
        print("Peringatan: YOUTUBE_API_KEY tidak disetel. Tidak dapat mengambil video YouTube.")
        return []

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

        query = " ".join(keywords) # Gabungkan kata kunci menjadi satu string kueri

        search_response = youtube.search().list(
            q=query,
            part="snippet", # Hanya mengambil snippet untuk efisiensi
            type="video",   # Hanya cari video
            maxResults=max_results,
            relevanceLanguage="id", # Opsional: prioritaskan bahasa tertentu
            # order="viewCount" # Opsional: urutkan berdasarkan jumlah penayangan
        ).execute()

        videos = []
        for item in search_response.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                video_id = item["id"]["videoId"]
                videos.append({
                    "videoId": video_id,
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "channelTitle": item["snippet"]["channelTitle"],
                    "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnailUrl": item["snippet"]["thumbnails"]["default"]["url"] # Atau 'medium' atau 'high'
                })
        return videos

    except HttpError as e:
        print(f"Terjadi error HTTP saat mengakses YouTube API: {e}")
        # Anda mungkin ingin log error ini atau menanganinya secara berbeda
        return []
    except Exception as e:
        print(f"Terjadi error tak terduga saat mengambil video YouTube: {e}")
        return []

def scrape_article_content(url: str) -> Optional[str]:
    """
    Mengambil dan mengurai konten teks utama dari URL artikel.

    Args:
        url: URL artikel yang akan di-scrape.

    Returns:
        Konten teks bersih dari artikel, atau None jika terjadi error.
    """
    try:
        headers = { # Meniru browser untuk menghindari blokir sederhana
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10) # Timeout 10 detik
        response.raise_for_status() # Memunculkan error untuk status HTTP 4xx/5xx

        soup = BeautifulSoup(response.content, "html.parser")

        # Strategi 1: Cari tag <article>
        article_tag = soup.find("article")
        if article_tag:
            text_content = article_tag.get_text(separator="\n", strip=True)
            return "\n".join(line.strip() for line in text_content.splitlines() if line.strip())


        # Strategi 2: Cari div dengan paragraf terbanyak (heuristik umum)
        # Ini bisa sangat tidak akurat dan perlu disesuaikan per situs jika memungkinkan
        best_candidate = None
        max_p_count = 0

        for main_content_candidate in soup.find_all(['main', 'div', 'section']): # Tag yang mungkin berisi konten utama
            # Hindari elemen navigasi dan footer yang umum
            if main_content_candidate.get('role') in ['navigation', 'banner', 'contentinfo', 'search'] or \
               main_content_candidate.find(['nav', 'footer', 'header', 'aside']):
                continue

            p_tags = main_content_candidate.find_all("p", recursive=False) # Hanya paragraf langsung
            if len(p_tags) > max_p_count:
                # Pertimbangkan juga panjang teks di dalam p_tags untuk menghindari div dengan banyak <p> kosong
                text_length = sum(len(p.get_text(strip=True)) for p in p_tags)
                if text_length > 100: # Ambang batas minimal panjang teks
                    max_p_count = len(p_tags)
                    best_candidate = main_content_candidate

        if best_candidate:
            # Ekstrak semua teks dari kandidat terbaik, termasuk teks dari child tags lainnya
            # seperti heading, list, dll., namun fokus pada paragraf.
            text_elements = best_candidate.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            if not text_elements: # Jika tidak ada tag spesifik, ambil semua teks dari kandidat
                 text_content = best_candidate.get_text(separator="\n", strip=True)
            else:
                text_lines = [el.get_text(strip=True) for el in text_elements]
                text_content = "\n".join(line for line in text_lines if line)

            return "\n".join(line.strip() for line in text_content.splitlines() if line.strip())

        # Strategi Fallback: Ambil semua teks dari body jika tidak ada yang ditemukan
        # Ini akan sangat berantakan dan biasanya tidak diinginkan.
        # body_text = soup.body.get_text(separator="\n", strip=True)
        # return "\n".join(line.strip() for line in body_text.splitlines() if line.strip())

        print(f"Peringatan: Tidak dapat menemukan konten artikel utama yang jelas untuk URL: {url}")
        return None # Atau kembalikan semua teks body jika itu lebih baik daripada None

    except requests.exceptions.RequestException as e:
        print(f"Error saat melakukan permintaan ke URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Error tak terduga saat mengurai URL {url}: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> List[str]:
    """
    Memecah teks panjang menjadi potongan-potongan yang lebih kecil.

    Args:
        text: Teks yang akan dipecah.
        chunk_size: Ukuran maksimum setiap potongan (dalam karakter).
        chunk_overlap: Jumlah karakter yang tumpang tindih antar potongan.

    Returns:
        Daftar string, di mana setiap string adalah satu potongan teks.
    """
    if not text or not text.strip():
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        # separators=["\n\n", "\n", " ", ""] # Default, bisa disesuaikan
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Contoh penggunaan (dapat dihapus atau dikomentari di produksi)
if __name__ == "__main__":
    print("--- Menguji Pengambilan Video YouTube ---")
    sample_keywords = ["Python FastAPI tutorial", "Async programming Python"]
    videos_result = fetch_youtube_videos(sample_keywords, max_results=2)
    if videos_result:
        for video in videos_result:
            print(f"Judul: {video['title']}")
            print(f"URL: {video['videoUrl']}")
            print(f"Deskripsi (awal): {video['description'][:100]}...")
            print("-" * 10)
    else:
        print("Tidak ada video YouTube yang ditemukan atau terjadi error.")

    print("\n--- Menguji Article Scraper ---")
    # Ganti dengan URL artikel yang valid untuk pengujian
    # test_article_url = "https://www.example.com/some-news-article"
    test_article_url = "https://gcn.com/emerging-tech/2024/07/darpa-looks-develop-ai-mentor-software-developers/398255/" # Contoh URL

    # Karena saya tidak bisa mengakses internet, saya akan mock hasilnya di sini
    # scraped_content = scrape_article_content(test_article_url)
    # if scraped_content:
    #     print(f"Konten dari {test_article_url} (awal):\n{scraped_content[:500]}...")
    # else:
    #     print(f"Gagal meng-scrape artikel dari {test_article_url}")
    print(f"CATATAN: Pengujian scrape_article_content memerlukan akses internet dan URL yang valid. Pengujian dilewati di lingkungan ini.")


    print("\n--- Menguji Pemecah Teks ---")
    sample_long_text = (
        "Ini adalah paragraf pertama dari teks yang sangat panjang. " * 20 +
        "\n\nIni adalah paragraf kedua, juga bagian dari teks yang panjang. " * 20 +
        "Teks ini dimaksudkan untuk didemonstrasikan bagaimana RecursiveCharacterTextSplitter "
        "akan memecahnya menjadi beberapa potongan yang lebih mudah dikelola. " * 10 +
        "Setiap potongan akan memiliki ukuran maksimum sekitar 1000 karakter "
        "dengan tumpang tindih sekitar 150 karakter antar potongan yang berdekatan. " * 5 +
        "Ini membantu menjaga konteks saat memproses setiap potongan secara individual, "
        "misalnya saat membuat embedding atau melakukan analisis lebih lanjut." * 5
    )
    if not sample_long_text.strip(): # Periksa jika teks contoh valid
        print("Teks contoh untuk chunking kosong.")
    else:
        text_chunks = chunk_text(sample_long_text)
        if text_chunks:
            print(f"Teks dipecah menjadi {len(text_chunks)} potongan:")
            for i, chunk in enumerate(text_chunks):
                print(f"--- Potongan {i+1} (panjang: {len(chunk)}) ---")
                print(chunk[:150] + "..." if len(chunk) > 150 else chunk)
                print("-" * 10)
        else:
            print("Tidak ada potongan yang dihasilkan dari teks contoh.")

```

Beberapa catatan penting tentang implementasi ini:
*   **`fetch_youtube_videos`**:
    *   Menggunakan `YOUTUBE_API_KEY` dari variabel lingkungan.
    *   Menggabungkan kata kunci menjadi satu string kueri.
    *   Mengambil `videoId`, `title`, `description`, `channelTitle`, dan membuat `videoUrl` serta mengambil `thumbnailUrl`.
    *   Menyertakan penanganan error dasar untuk `HttpError`.
*   **`scrape_article_content`**:
    *   Menggunakan `requests` dengan header User-Agent dasar.
    *   Mencoba dua strategi untuk menemukan konten utama: tag `<article>` terlebih dahulu, kemudian mencari `div` atau `section` atau `main` dengan jumlah tag `<p>` yang signifikan. Ini adalah heuristik dan mungkin tidak berfungsi dengan baik untuk semua situs web. Scraping web yang tangguh seringkali memerlukan penyesuaian per situs atau pustaka yang lebih canggih seperti `newspaper3k` atau `trafilatura`.
    *   Membersihkan teks yang diekstrak.
    *   Menyertakan penanganan error untuk permintaan dan parsing.
*   **`chunk_text`**:
    *   Menggunakan `RecursiveCharacterTextSplitter` dari `langchain` dengan `chunk_size` 1000 dan `chunk_overlap` 150 seperti yang diminta.
    *   Menangani kasus di mana teks input mungkin kosong.
*   **Contoh Penggunaan (`if __name__ == "__main__":`)**: Saya telah menyertakan blok ini untuk pengujian lokal sederhana. Pengujian `scrape_article_content` memerlukan URL yang valid dan akses internet.

Modul ini sekarang menyediakan fungsionalitas dasar untuk mengambil video YouTube, meng-scrape konten artikel, dan memecah teks. Ini dapat diimpor dan digunakan di bagian lain dari aplikasi backend.
