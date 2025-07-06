import React, { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom'; // Asumsikan react-router-dom digunakan
import { Curriculum } from '../../types'; // Impor tipe Curriculum

// Spinner sederhana sebagai komponen inline
const Spinner: React.FC = () => (
  <div className="flex justify-center items-center">
    <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-600"></div>
  </div>
);

interface OnboardingProps {
  // Prop untuk callback setelah kurikulum berhasil dibuat,
  // bisa digunakan untuk menyimpan kurikulum ke state global/context.
  onCurriculumGenerated: (curriculum: Curriculum) => void;
}

const Onboarding: React.FC<OnboardingProps> = ({ onCurriculumGenerated }) => {
  const [goal, setGoal] = useState<string>('');
  const [currentStep, setCurrentStep] = useState<number>(1); // 1: Input goal, 2: Loading
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleGoalSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!goal.trim()) {
      setError('Tujuan pembelajaran tidak boleh kosong.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCurrentStep(2);

    try {
      const response = await fetch('/api/curriculum', { // Pastikan URL ini benar
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ goal: goal }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Gagal mengambil detail error dari server."}));
        throw new Error(errorData.detail || `Gagal menghasilkan kurikulum (Status: ${response.status})`);
      }

      const curriculumData: Curriculum = await response.json();

      // Panggil callback dengan data kurikulum yang diterima
      onCurriculumGenerated(curriculumData);

      setIsLoading(false);
      // Arahkan ke dasbor setelah berhasil
      // Data kurikulum bisa diteruskan melalui state navigasi jika diperlukan segera di dasbor,
      // atau lebih baik disimpan di state global/context melalui onCurriculumGenerated.
      navigate('/dashboard', { state: { newCurriculum: true } });

    } catch (err) {
      console.error('Error generating curriculum:', err);
      const errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan tidak diketahui.';
      setError(errorMessage);
      setIsLoading(false);
      setCurrentStep(1); // Kembali ke langkah input jika ada error
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-500 to-indigo-700 p-4 text-white">
      <div className="w-full max-w-xl bg-white dark:bg-gray-800 shadow-2xl rounded-xl p-8 md:p-12 text-gray-800 dark:text-white">

        {currentStep === 1 && (
          <>
            <h1 className="text-3xl md:text-4xl font-bold text-center mb-3">Selamat Datang di MentorAI!</h1>
            <p className="text-center text-gray-600 dark:text-gray-300 mb-8">
              Mari kita mulai dengan menetapkan tujuan pembelajaran utama Anda. Apa yang ingin Anda capai?
            </p>
            <form onSubmit={handleGoalSubmit} className="space-y-6">
              <div>
                <label htmlFor="learningGoal" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                  Tujuan Pembelajaran Utama Anda:
                </label>
                <textarea
                  id="learningGoal"
                  name="learningGoal"
                  rows={5}
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="Contoh: Saya ingin menguasai React dan TypeScript untuk membangun aplikasi web modern, atau Saya ingin belajar dasar-dasar analisis data menggunakan Python."
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none dark:bg-gray-700 dark:text-white transition-colors"
                  required
                />
              </div>
              {error && (
                <p className="text-sm text-red-500 dark:text-red-400 text-center">{error}</p>
              )}
              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 transition-colors disabled:opacity-50"
                >
                  {isLoading ? 'Memproses...' : 'Hasilkan Kurikulum Saya'}
                </button>
              </div>
            </form>
          </>
        )}

        {currentStep === 2 && (
          <div className="text-center py-10">
            <Spinner />
            <p className="mt-6 text-xl font-semibold text-gray-700 dark:text-gray-200">
              MentorAI sedang menyiapkan jalur pembelajaran Anda...
            </p>
            <p className="text-gray-500 dark:text-gray-400 mt-2">
              Ini mungkin memakan waktu beberapa saat. Mohon tunggu.
            </p>
          </div>
        )}

        {/* Placeholder untuk langkah-langkah berikutnya jika ada, misal konfirmasi kurikulum */}
        {/* {currentStep === 3 && curriculumData && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Kurikulum Dihasilkan!</h2>
            <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto">
              {JSON.stringify(curriculumData, null, 2)}
            </pre>
            <button
              onClick={() => navigate('/dashboard')}
              className="mt-6 w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg"
            >
              Lanjutkan ke Dasbor
            </button>
          </div>
        )} */}

      </div>
      <p className="mt-8 text-center text-sm text-blue-200">
        MentorAI &copy; {new Date().getFullYear()}
      </p>
    </div>
  );
};

export default Onboarding;
```

Catatan tentang implementasi ini:
*   **State**: Mengelola `goal`, `currentStep`, `isLoading`, dan `error`.
*   **`useNavigate`**: Digunakan untuk mengalihkan pengguna setelah kurikulum berhasil dibuat.
*   **Langkah-langkah**:
    *   **Langkah 1**: Menampilkan `textarea` untuk pengguna memasukkan tujuan pembelajaran mereka.
    *   **Langkah 2**: Menampilkan komponen `Spinner` dan pesan pemuatan saat API dipanggil.
*   **`handleGoalSubmit`**:
    *   Mengatur status pemuatan dan berpindah ke langkah 2.
    *   Melakukan panggilan `fetch` ke endpoint `/api/curriculum`.
    *   Jika berhasil, memanggil prop `onCurriculumGenerated` (yang harus disediakan oleh komponen induk untuk menangani data kurikulum, misalnya menyimpannya ke state global/context) dan kemudian mengarahkan ke `/dashboard`. Saya menyertakan `state: { newCurriculum: true }` dalam navigasi sebagai contoh bagaimana Anda bisa memberi tahu halaman dasbor bahwa kurikulum baru saja dibuat, meskipun cara terbaik untuk berbagi data kurikulum adalah melalui state management yang lebih terpusat.
    *   Jika gagal, menampilkan pesan error dan kembali ke langkah 1.
*   **Styling**: Kelas Tailwind CSS digunakan untuk styling dasar agar terlihat modern dan bersih.
*   **Prop `onCurriculumGenerated`**: Prop ini penting agar komponen induk dapat menerima dan menangani data kurikulum yang dihasilkan. Dalam aplikasi nyata, ini bisa digunakan untuk mengatur state di Redux, Zustand, Context API, atau state komponen `App.tsx`.

Komponen ini sekarang menyediakan alur onboarding dasar. Integrasi dengan sistem routing React (misalnya, di `App.tsx`) akan diperlukan untuk menampilkannya pada rute yang sesuai (misalnya, `/onboarding` atau sebagai halaman default jika tidak ada kurikulum).
