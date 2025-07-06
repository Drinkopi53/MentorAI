# Daftar Periksa Kualitas (QA) Pra-Peluncuran MentorAI

Dokumen ini berisi daftar item yang harus diperiksa dan diverifikasi sebelum peluncuran resmi platform MentorAI. Tujuannya adalah untuk memastikan kualitas, fungsionalitas, dan pengalaman pengguna yang optimal.

## Legenda Status:
- `[ ]` Belum Diuji / Tertunda
- `[x]` Lulus / Selesai
- `[!]` Gagal / Memerlukan Perhatian
- `[NA]` Tidak Berlaku

---

## 1. Konten & Desain Visual (UI/UX)

| ID  | Item Pemeriksaan                                                                 | Status | Catatan Tambahan                 |
|-----|----------------------------------------------------------------------------------|--------|---------------------------------|
| CD1 | Verifikasi semua teks (copywriting) bebas dari kesalahan ketik dan tata bahasa.    | `[ ]`  | Termasuk pesan error, label, dll. |
| CD2 | Pastikan konsistensi desain (font, warna, spasi, ikon) di semua halaman/komponen. | `[ ]`  |                                 |
| CD3 | Uji responsivitas desain di berbagai ukuran layar (desktop, tablet, mobile).      | `[ ]`  | Chrome DevTools, perangkat fisik |
| CD4 | Pastikan semua gambar dan ikon ditampilkan dengan benar dan dioptimalkan.          | `[ ]`  | Tidak ada gambar rusak/blur        |
| CD5 | Verifikasi navigasi intuitif dan alur pengguna jelas serta mudah diikuti.        | `[ ]`  |                                 |
| CD6 | Periksa keterbacaan teks (kontras warna, ukuran font) untuk aksesibilitas dasar. | `[ ]`  |                                 |
| CD7 | Pastikan semua link internal dan eksternal berfungsi dengan benar.                 | `[ ]`  |                                 |
| CD8 | Verifikasi tampilan halaman error kustom (404, 500) informatif dan ramah pengguna. | `[ ]`  |                                 |

---

## 2. Fungsionalitas Inti (Core Features)

| ID  | Item Pemeriksaan                                                                             | Status | Catatan Tambahan                     |
|-----|----------------------------------------------------------------------------------------------|--------|--------------------------------------|
| FC1 | **Otentikasi (Google OAuth):** Uji alur login dengan akun Google yang valid.                  | `[ ]`  |                                      |
| FC2 | **Otentikasi:** Uji penanganan jika otentikasi Google gagal atau dibatalkan pengguna.           | `[ ]`  |                                      |
| FC3 | **Otentikasi:** Uji alur logout dan pastikan sesi/cookie JWT dihapus dengan benar.            | `[ ]`  |                                      |
| FC4 | **Otentikasi:** Verifikasi akses ke endpoint yang dilindungi setelah login berhasil.            | `[ ]`  | Coba akses `/api/auth/me`.             |
| FC5 | **Otentikasi:** Verifikasi penolakan akses ke endpoint yang dilindungi tanpa token/token tidak valid. | `[ ]`  |                                      |
| FC6 | **Onboarding:** Uji pengiriman tujuan pembelajaran yang valid pada form onboarding.             | `[ ]`  |                                      |
| FC7 | **Onboarding:** Verifikasi pengalihan ke dasbor setelah kurikulum berhasil dibuat.           | `[ ]`  |                                      |
| FC8 | **Onboarding:** Uji penanganan error jika API `/api/curriculum` gagal (misalnya, input tidak valid, error server). | `[ ]`  | Pesan error ditampilkan, tidak crash. |
| FC9 | **Generasi Kurikulum:** Verifikasi struktur data kurikulum yang diterima dari backend sesuai skema. | `[ ]`  |                                      |
| FC10| **Tampilan Kurikulum:** Pastikan semua modul dan topik dalam kurikulum ditampilkan dengan benar.   | `[ ]`  | Termasuk fungsi akordeon.            |
| FC11| **Pencarian Semantik:** Uji fungsi pencarian dengan berbagai kueri (valid, kosong, terlalu umum). | `[ ]`  | Verifikasi relevansi hasil.          |
| FC12| **Pencarian Semantik:** Pastikan penanganan jika tidak ada hasil pencarian yang ditemukan.         | `[ ]`  | Pesan yang sesuai.                   |
| FC13| **Dasbor:** Verifikasi semua elemen placeholder di dasbor menampilkan data (tiruan/nyata) dengan benar. | `[ ]`  | Kemajuan, Up Next, dll.            |

---

## 3. Fungsionalitas Komunitas & Gamifikasi

| ID  | Item Pemeriksaan                                                                         | Status | Catatan Tambahan                               |
|-----|------------------------------------------------------------------------------------------|--------|------------------------------------------------|
| CG1 | **Registrasi Pengguna (Lokal):** Uji pendaftaran pengguna dengan email/username yang valid.   | `[ ]`  | Jika diimplementasikan selain OAuth.            |
| CG2 | **Registrasi Pengguna (Lokal):** Uji dengan email/username yang sudah ada (verifikasi error). | `[ ]`  |                                                |
| CG3 | **Forum (Buat Postingan):** Uji pembuatan postingan baru dengan judul dan konten yang valid.   | `[ ]`  | Pastikan `author_id` dari `current_user`.      |
| CG4 | **Forum (Lihat Postingan):** Verifikasi semua postingan dapat dilihat di halaman forum utama.    | `[ ]`  |                                                |
| CG5 | **Forum (Detail Postingan):** Pastikan detail postingan dan balasan ditampilkan dengan benar. | `[ ]`  |                                                |
| CG6 | **Forum (Buat Balasan):** Uji penambahan balasan baru pada postingan.                       | `[ ]`  | Termasuk balasan ke balasan (jika didukung). |
| CG7 | **Forum (Voting):** Uji fungsionalitas upvote pada postingan dan balasan.                  | `[ ]`  | Verifikasi jumlah vote bertambah.              |
| CG8 | **Gamifikasi (XP):** Verifikasi penambahan XP setelah aksi tertentu (misal, buat postingan, vote). | `[ ]`  | Cek `xp_points` pengguna.                      |
| CG9 | **Gamifikasi (Lencana):** Uji logika pemberian lencana (misal, setelah XP pertama, postingan pertama). | `[ ]`  | Cek tabel `UserBadges`.                        |
| CG10| **Leaderboard:** Verifikasi leaderboard menampilkan pengguna berdasarkan XP dengan urutan yang benar. | `[ ]`  |                                                |
| CG11| **Chatbot RAG:** Uji interaksi dasar dengan chatbot, ajukan pertanyaan relevan dengan konten yang diindeks. | `[ ]`  |                                                |
| CG12| **Chatbot RAG:** Verifikasi respons streaming dari chatbot berfungsi.                       | `[ ]`  |                                                |
| CG13| **Chatbot RAG:** Uji penanganan jika chatbot tidak menemukan jawaban relevan.                 | `[ ]`  |                                                |

---

## 4. Kompatibilitas & Aksesibilitas

| ID  | Item Pemeriksaan                                                                          | Status | Catatan Tambahan                                      |
|-----|-------------------------------------------------------------------------------------------|--------|-------------------------------------------------------|
| CA1 | **Browser:** Uji fungsionalitas inti di versi terbaru Chrome, Firefox, Safari, dan Edge.   | `[ ]`  |                                                       |
| CA2 | **Perangkat Mobile:** Uji pengalaman pengguna dan fungsionalitas di iOS (Safari) dan Android (Chrome). | `[ ]`  |                                                       |
| CA3 | **Aksesibilitas (Keyboard):** Pastikan semua elemen interaktif dapat diakses dan dioperasikan menggunakan keyboard saja. | `[ ]`  | Fokus terlihat, urutan tab logis.                 |
| CA4 | **Aksesibilitas (Screen Reader):** Uji alur utama dengan screen reader (misalnya, NVDA, VoiceOver). | `[ ]`  | Label ARIA, peran, teks alternatif gambar.         |
| CA5 | **Zoom Halaman:** Pastikan tata letak tidak rusak saat halaman di-zoom hingga 200%.           | `[ ]`  |                                                       |
| CA6 | **Orientasi Perangkat:** Uji tampilan dan fungsionalitas dalam mode potret dan lanskap di perangkat mobile/tablet. | `[ ]`  |                                                       |

---

## 5. Kinerja

| ID  | Item Pemeriksaan                                                                               | Status | Catatan Tambahan                                      |
|-----|------------------------------------------------------------------------------------------------|--------|-------------------------------------------------------|
| PE1 | **Waktu Muat Halaman Awal:** Ukur waktu muat untuk halaman utama (misalnya, Dasbor, Forum).      | `[ ]`  | Target < 3 detik. Gunakan Lighthouse, WebPageTest.  |
| PE2 | **Ukuran Aset:** Periksa ukuran total aset (JS, CSS, gambar) dan optimalkan jika perlu.        | `[ ]`  | Minifikasi, kompresi, lazy loading.                  |
| PE3 | **Responsivitas API:** Ukur waktu respons untuk endpoint API utama (kurikulum, search, forum). | `[ ]`  | Target < 500ms untuk sebagian besar.                  |
| PE4 | **Penggunaan Memori (Frontend):** Pantau penggunaan memori browser selama penggunaan normal.    | `[ ]`  | Tidak ada kebocoran memori yang signifikan.           |
| PE5 | **Penggunaan CPU (Frontend):** Pastikan aplikasi tidak menyebabkan penggunaan CPU yang berlebihan. | `[ ]`  | Terutama saat animasi atau interaksi kompleks.       |
| PE6 | **Kinerja Database:** Uji kueri database yang kompleks (misalnya, pencarian, leaderboard) di bawah beban. | `[ ]`  | Pastikan indeks digunakan dengan benar.                 |
| PE7 | **Kinerja Chatbot Streaming:** Pastikan respons streaming terasa cepat dan tidak ada jeda besar. | `[ ]`  |                                                       |

---

## 6. Keamanan

| ID  | Item Pemeriksaan                                                                           | Status | Catatan Tambahan                                       |
|-----|--------------------------------------------------------------------------------------------|--------|--------------------------------------------------------|
| SE1 | **HTTPS:** Pastikan semua komunikasi menggunakan HTTPS di lingkungan produksi.                 | `[ ]`  |                                                        |
| SE2 | **Keamanan JWT:** Verifikasi JWT disimpan dengan aman (HTTPOnly cookie) dan divalidasi dengan benar di backend. | `[ ]`  | Periksa masa berlaku token.                            |
| SE3 | **Google OAuth:** Pastikan konfigurasi OAuth (Client ID/Secret, Redirect URI) aman dan benar. | `[ ]`  | Kunci rahasia tidak terekspos di frontend.             |
| SE4 | **Proteksi Input:** Uji terhadap input berbahaya (XSS, SQL Injection) pada semua form dan parameter API. | `[ ]`  | Gunakan data uji yang sesuai. Sanitasi output.           |
| SE5 | **Manajemen Error:** Pastikan pesan error tidak membocorkan informasi sensitif.             | `[ ]`  |                                                        |
| SE6 | **Kontrol Akses:** Verifikasi endpoint yang dilindungi hanya dapat diakses oleh pengguna terotentikasi. | `[ ]`  |                                                        |
| SE7 | **Kontrol Akses (Premium):** Uji bahwa fitur premium hanya dapat diakses oleh pengguna premium. | `[ ]`  |                                                        |
| SE8 | **Keamanan Header HTTP:** Implementasikan header keamanan yang direkomendasikan (CSP, HSTS, X-Frame-Options, dll.). | `[ ]`  |                                                        |
| SE9 | **Dependensi:** Periksa dependensi proyek (frontend & backend) untuk kerentanan yang diketahui. | `[ ]`  | `npm audit`, `pip audit` atau alat serupa.             |
| SE10| **Kebijakan Kata Sandi (jika ada login lokal):** Pastikan kebijakan kata sandi yang kuat diterapkan. | `[NA]` | Jika hanya OAuth, ini kurang relevan.                  |

---

Daftar periksa ini harus ditinjau dan diperbarui secara berkala seiring berkembangnya aplikasi.
Setiap item yang gagal harus dicatat, diprioritaskan, dan diperbaiki sebelum peluncuran.
