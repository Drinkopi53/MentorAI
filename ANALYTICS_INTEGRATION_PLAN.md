# Rencana Integrasi Analitik untuk MentorAI

Dokumen ini menguraikan rencana dasar untuk mengintegrasikan analitik ke dalam aplikasi MentorAI guna memahami perilaku pengguna, mengukur keberhasilan fitur, dan mengidentifikasi area untuk perbaikan.

## 1. Pentingnya Analitik

Mengintegrasikan analitik sangat penting untuk:
- **Memahami Pengguna:** Bagaimana pengguna berinteraksi dengan platform? Fitur mana yang paling sering digunakan? Di mana pengguna mengalami kesulitan?
- **Mengukur Keterlibatan:** Berapa lama pengguna bertahan? Seberapa sering mereka kembali?
- **Optimalisasi Konversi:** Jika ada alur penting (misalnya, onboarding, langganan), analitik membantu mengidentifikasi bottleneck.
- **Validasi Fitur:** Apakah fitur baru diadopsi? Apakah mereka memberikan nilai yang diharapkan?
- **Pengambilan Keputusan Berbasis Data:** Membuat keputusan produk dan bisnis yang didukung oleh data nyata, bukan asumsi.

## 2. Pemilihan Alat Analitik

Ada banyak alat analitik yang tersedia. Beberapa pilihan populer untuk aplikasi web meliputi:

*   **Google Analytics (GA4):** Alat gratis yang kuat dari Google, bagus untuk melacak lalu lintas situs, demografi pengguna, dan event kustom. `react-ga4` adalah pustaka populer untuk integrasi React.
*   **Mixpanel:** Berfokus pada analitik berbasis event dan pengguna, sangat baik untuk memahami alur pengguna dan retensi.
*   **Amplitude:** Mirip dengan Mixpanel, kuat untuk analitik produk.
*   **PostHog:** Platform analitik produk open-source yang bisa di-host sendiri atau menggunakan versi cloud mereka. Menawarkan fitur seperti session recording dan feature flags.
*   **Plausible Analytics / Fathom Analytics:** Alternatif yang lebih berfokus pada privasi dan lebih sederhana dari Google Analytics.

**Rekomendasi Awal:**
Untuk MentorAI, memulai dengan **Google Analytics 4 (GA4)** adalah pilihan yang baik karena gratis, banyak digunakan, dan memiliki banyak sumber daya. Jika kebutuhan analitik produk yang lebih mendalam muncul, alat seperti Mixpanel atau PostHog dapat dipertimbangkan nanti.

## 3. Rencana Implementasi Dasar (Menggunakan Google Analytics 4)

### Langkah 1: Buat Properti GA4
1.  Buka [Google Analytics](https://analytics.google.com/).
2.  Buat properti baru untuk MentorAI.
3.  Dapatkan **Measurement ID** (misalnya, `G-XXXXXXXXXX`).

### Langkah 2: Inisialisasi di Aplikasi React
Kita bisa menggunakan pustaka seperti `react-ga4` atau menginisialisasi secara manual. Menggunakan `react-ga4` lebih mudah.

**a. Instalasi `react-ga4`:**
```bash
npm install react-ga4
# atau
yarn add react-ga4
```

**b. Inisialisasi di `App.tsx` (atau file entri utama):**
Cuplikan kode ini menunjukkan bagaimana menginisialisasi GA4. Idealnya, Measurement ID akan berasal dari variabel lingkungan.

```typescript
// frontend/src/App.tsx (atau index.tsx)

import React, { useEffect } from 'react';
import ReactGA from 'react-ga4';
// ... impor lainnya ...

// Ambil Measurement ID dari variabel lingkungan
// Pastikan variabel ini tersedia saat build atau runtime, tergantung cara Anda mengelolanya.
// Contoh: REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX di file .env Anda
const GA_MEASUREMENT_ID = process.env.REACT_APP_GA_MEASUREMENT_ID;

function App() {
  useEffect(() => {
    if (GA_MEASUREMENT_ID) {
      ReactGA.initialize(GA_MEASUREMENT_ID);
      console.log("Google Analytics diinisialisasi dengan ID:", GA_MEASUREMENT_ID);
      // Pelacakan tampilan halaman awal (jika tidak ditangani oleh konfigurasi default GA4)
      // ReactGA.send({ hitType: "pageview", page: window.location.pathname + window.location.search });
    } else {
      console.warn("Google Analytics Measurement ID tidak ditemukan. Pelacakan tidak akan aktif.");
    }
  }, []);

  // ... sisa komponen App ...
  return (
    // JSX Anda
  );
}

export default App;
```

### Langkah 3: Pelacakan Tampilan Halaman (Page Views)
Jika Anda menggunakan React Router, Anda perlu melacak perubahan tampilan halaman. Buat komponen atau hook untuk ini.

Contoh dengan `useEffect` di komponen router level atas atau di setiap komponen halaman:
```typescript
// Di dalam komponen halaman atau komponen yang merender Routes
import React, { useEffect } from 'react';
import ReactGA from 'react-ga4';
import { useLocation } from 'react-router-dom';

const PageViewTracker: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    if (process.env.REACT_APP_GA_MEASUREMENT_ID) {
      ReactGA.send({ hitType: "pageview", page: location.pathname + location.search, title: document.title });
      console.log(`GA Pageview sent: ${location.pathname + location.search}`);
    }
  }, [location]);

  return null; // Komponen ini tidak merender apa pun
};

// Kemudian gunakan <PageViewTracker /> di dalam <Router> Anda di App.tsx
// <Router>
//   <PageViewTracker />
//   <Routes>
//     {/* ... rute Anda ... */}
//   </Routes>
// </Router>
```

### Langkah 4: Pelacakan Event Kustom
Lacak interaksi pengguna yang penting.

**Contoh Pelacakan Klik Tombol "Hasilkan Kurikulum" di `Onboarding.tsx`:**

```typescript
// frontend/src/components/Onboarding/Onboarding.tsx

import ReactGA from 'react-ga4';
// ... impor lainnya ...

const Onboarding: React.FC<OnboardingProps> = ({ onCurriculumGenerated }) => {
  // ... state dan logika lainnya ...

  const handleGoalSubmit = async (e: FormEvent<HTMLFormElement>) => {
    // ... logika submit ...

    if (process.env.REACT_APP_GA_MEASUREMENT_ID) {
      ReactGA.event({
        category: 'Onboarding',
        action: 'Click Generate Curriculum',
        label: goal, // Opsional: kirim tujuan sebagai label
        // value: 1 // Opsional: nilai numerik jika relevan
      });
    }

    // ... sisa logika setelah submit ...
  };

  // ... JSX ...
};
```

**Contoh Pelacakan Pengiriman Pesan di `ChatWidget.tsx`:**
```typescript
// frontend/src/components/ChatWidget/ChatWidget.tsx

import ReactGA from 'react-ga4';
// ... impor lainnya ...

const ChatWidget: React.FC<ChatWidgetProps> = ({ isOpen, onClose }) => {
  // ... state dan logika lainnya ...

  const handleSendMessage = async (e: FormEvent<HTMLFormElement>) => {
    // ... logika submit pesan ...

    if (process.env.REACT_APP_GA_MEASUREMENT_ID && userMessageText) {
      ReactGA.event({
        category: 'Chatbot',
        action: 'Send Message',
        label: `Panjang Pesan: ${userMessageText.length}`, // Contoh label
      });
    }

    // ... sisa logika setelah mengirim pesan ...
  };

  // ... JSX ...
};
```

## 4. Event Utama yang Perlu Dilacak (Contoh Awal)

*   **Onboarding:**
    *   `onboarding_started` (saat pengguna masuk ke halaman onboarding)
    *   `goal_submitted` (saat pengguna mengirimkan tujuan pembelajaran)
    *   `curriculum_generated_success`
    *   `curriculum_generated_fail`
*   **Kurikulum & Pembelajaran:**
    *   `module_viewed` (parameter: `module_title`)
    *   `topic_completed` (parameter: `topic_title`, `module_title`)
    *   `learning_path_completed`
*   **Chatbot:**
    *   `chat_opened`
    *   `chat_message_sent` (parameter: `message_length`)
    *   `chat_feedback_received` (jika ada fitur feedback)
*   **Komunitas (Forum):**
    *   `forum_post_created`
    *   `forum_reply_created`
    *   `forum_post_viewed` (parameter: `post_id`)
    *   `forum_vote_casted` (parameter: `item_type` (post/reply), `vote_type` (up/down))
*   **Gamifikasi:**
    *   `xp_earned` (parameter: `amount`, `source_action`)
    *   `badge_awarded` (parameter: `badge_name`)
*   **Akun Pengguna:**
    *   `user_login_google`
    *   `user_logout`
    *   `profile_updated`
*   **Monetisasi (jika ada):**
    *   `view_premium_feature_locked` (saat pengguna mencoba akses fitur premium tapi masih free)
    *   `upgrade_to_premium_clicked`
    *   `subscription_successful`
    *   `subscription_cancelled`

## 5. Daftar Periksa Pasca-Peluncuran (Terkait Analitik)

Setelah MentorAI diluncurkan dan analitik terintegrasi:

1.  `[ ]` **Verifikasi Pelacakan Data:** Pastikan data masuk ke platform analitik Anda (misalnya, Realtime reports di GA4).
2.  `[ ]` **Uji Event Kustom:** Picu semua event kustom yang telah Anda siapkan dan verifikasi bahwa mereka muncul di analitik dengan parameter yang benar.
3.  `[ ]` **Periksa Pelacakan Tampilan Halaman:** Navigasi ke berbagai halaman dan pastikan tampilan halaman dilacak dengan benar.
4.  `[ ]` **Konfigurasi Tujuan/Konversi (Goals/Conversions):** Siapkan tujuan di platform analitik Anda untuk aksi pengguna kunci (misalnya, penyelesaian onboarding, pembuatan kurikulum, upgrade langganan).
5.  `[ ]` **Buat Dasbor Dasar:** Siapkan dasbor di alat analitik Anda untuk memantau metrik kunci (pengguna aktif, sesi, event teratas, funnel konversi).
6.  `[ ]` **Tinjau Data Secara Berkala:** Jadwalkan waktu untuk meninjau data analitik secara rutin (harian, mingguan, bulanan) untuk mengidentifikasi tren, masalah, dan peluang.
7.  `[ ]` **Iterasi berdasarkan Data:** Gunakan wawasan dari analitik untuk menginformasikan pengembangan produk, perbaikan UX, dan strategi pemasaran.
8.  `[ ]` **Pastikan Kepatuhan Privasi:** Pastikan implementasi analitik Anda mematuhi peraturan privasi yang relevan (misalnya, GDPR, CCPA) dan informasikan pengguna tentang pengumpulan data melalui kebijakan privasi.

Rencana ini menyediakan titik awal. Kebutuhan analitik akan berkembang seiring pertumbuhan MentorAI.
```

Penjelasan:
*   **Pentingnya Analitik & Pemilihan Alat**: Bagian ini menjelaskan mengapa analitik itu penting dan memberikan beberapa contoh alat, merekomendasikan GA4 untuk memulai.
*   **Rencana Implementasi Dasar**:
    *   Langkah-langkah untuk membuat properti GA4 dan mendapatkan Measurement ID.
    *   Cara menginstal `react-ga4`.
    *   Cuplikan kode untuk inisialisasi GA4 di `App.tsx` (atau file entri utama aplikasi React Anda). Penting untuk menggunakan variabel lingkungan untuk Measurement ID.
    *   Contoh pelacakan tampilan halaman menggunakan `useLocation` dari `react-router-dom`.
    *   Contoh pelacakan event kustom untuk klik tombol "Hasilkan Kurikulum" di `Onboarding.tsx` dan pengiriman pesan di `ChatWidget.tsx`.
*   **Event Utama yang Perlu Dilacak**: Daftar contoh event yang relevan untuk MentorAI di berbagai kategori fitur. Ini perlu disesuaikan dan diperluas.
*   **Daftar Periksa Pasca-Peluncuran (Analitik)**: Langkah-langkah yang perlu dilakukan setelah peluncuran untuk memastikan analitik berfungsi dan digunakan dengan benar.

File ini memberikan panduan yang baik untuk memulai integrasi analitik di MentorAI. Ingatlah untuk mengganti `REACT_APP_GA_MEASUREMENT_ID` dengan ID Anda yang sebenarnya dan sesuaikan nama event/kategori sesuai kebutuhan.
