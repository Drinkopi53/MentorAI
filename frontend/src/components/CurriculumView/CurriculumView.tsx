import React, { useState } from 'react';
import { Curriculum, Module as CurriculumModule, Topic } from '../../types'; // Impor tipe

// Ikon contoh (Anda akan menggunakan pustaka ikon atau SVG Anda sendiri)
const ChevronDownIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
  </svg>
);

const ChevronUpIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
  </svg>
);

const CheckCircleIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

const CircleIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => ( // Placeholder untuk topik yang belum selesai
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);


interface CurriculumViewProps {
  curriculum: Curriculum;
}

const CurriculumView: React.FC<CurriculumViewProps> = ({ curriculum }) => {
  const [openModuleId, setOpenModuleId] = useState<string | null>(null);

  const toggleModule = (moduleId: string) => {
    setOpenModuleId(openModuleId === moduleId ? null : moduleId);
  };

  if (!curriculum || !curriculum.modules) {
    return <p className="text-gray-600 dark:text-gray-400">Kurikulum tidak tersedia atau kosong.</p>;
  }

  return (
    <div className="container mx-auto p-4 md:p-8 bg-gray-50 dark:bg-gray-900 rounded-xl shadow-lg">
      <header className="mb-6 md:mb-8 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white">
          {curriculum.title || 'Kurikulum Pembelajaran'}
        </h1>
        {curriculum.description && (
          <p className="mt-2 text-md text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            {curriculum.description}
          </p>
        )}
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Tujuan Awal: {curriculum.goal}
        </p>
      </header>

      <div className="space-y-4">
        {curriculum.modules.map((module, index) => (
          <div key={module.title + index} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            {/* Header Akordeon Modul */}
            <button
              onClick={() => toggleModule(module.title + index)} // Gunakan ID unik jika title bisa duplikat
              className="w-full flex justify-between items-center p-4 md:p-5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none transition-colors duration-150"
            >
              <div className="text-left">
                <h2 className="text-lg md:text-xl font-semibold text-blue-600 dark:text-blue-400">{module.title}</h2>
                {module.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 hidden sm:block">{module.description}</p>
                )}
              </div>
              {openModuleId === (module.title + index) ? (
                <ChevronUpIcon className="h-6 w-6 text-gray-600 dark:text-gray-400" />
              ) : (
                <ChevronDownIcon className="h-6 w-6 text-gray-600 dark:text-gray-400" />
              )}
            </button>

            {/* Konten Akordeon Modul (Daftar Topik) */}
            {openModuleId === (module.title + index) && (
              <div className="p-4 md:p-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                {module.learning_objectives && module.learning_objectives.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-md text-gray-700 dark:text-gray-300 mb-1">Tujuan Pembelajaran:</h4>
                    <ul className="list-disc list-inside pl-1 space-y-1">
                      {module.learning_objectives.map((obj, i) => (
                        <li key={i} className="text-sm text-gray-600 dark:text-gray-400">{obj}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <h3 className="text-md font-semibold text-gray-700 dark:text-gray-300 mb-3">Topik:</h3>
                {module.topics && module.topics.length > 0 ? (
                  <ul className="space-y-3">
                    {module.topics.map((topic, topicIndex) => (
                      <li
                        key={topic.title + topicIndex}
                        className="flex items-start p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md hover:bg-gray-100 dark:hover:bg-gray-600/50 transition-colors duration-150"
                      >
                        {topic.completed ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                        ) : (
                          <CircleIcon className="h-5 w-5 text-gray-400 dark:text-gray-500 mr-3 mt-0.5 flex-shrink-0" />
                        )}
                        <div>
                            <span className="font-medium text-sm text-gray-800 dark:text-gray-100">{topic.title}</span>
                            {topic.description && (
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{topic.description}</p>
                            )}
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-400">Belum ada topik untuk modul ini.</p>
                )}

                {module.keywords && module.keywords.length > 0 && (
                  <div className="mt-5 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <h4 className="font-semibold text-xs text-gray-600 dark:text-gray-400 mb-1">Kata Kunci:</h4>
                    <div className="flex flex-wrap gap-2">
                      {module.keywords.map((keyword, i) => (
                        <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-700 dark:text-blue-100 text-xs rounded-full">{keyword}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Contoh Data Tiruan untuk CurriculumView (bisa diletakkan di file terpisah atau di App.tsx)
// export const mockCurriculumData: Curriculum = {
//   goal: "Belajar Pengembangan Web Modern dengan React dan TypeScript",
//   title: "Panduan Lengkap Pengembangan Web Modern",
//   description: "Kurikulum ini akan memandu Anda melalui dasar-dasar hingga konsep lanjutan dalam pengembangan web menggunakan React, TypeScript, dan alat modern lainnya.",
//   modules: [
//     {
//       title: "Modul 1: Pengenalan HTML, CSS, dan JavaScript",
//       description: "Memahami blok bangunan dasar web.",
//       learning_objectives: [
//         "Mengerti struktur dasar halaman HTML.",
//         "Mampu men-style elemen dengan CSS.",
//         "Memahami konsep dasar JavaScript seperti variabel, fungsi, dan DOM."
//       ],
//       topics: [
//         { title: "Dasar-Dasar HTML", description: "Tag, atribut, dan struktur dokumen.", completed: true },
//         { title: "Styling dengan CSS", description: "Selektor, properti, dan layout.", completed: true },
//         { title: "Pengenalan JavaScript", description: "Sintaks dasar dan manipulasi DOM.", completed: false },
//       ],
//       keywords: ["HTML", "CSS", "JavaScript", "Dasar Web"]
//     },
//     {
//       title: "Modul 2: Deep Dive ke React dan JSX",
//       description: "Membangun komponen UI interaktif dengan React.",
//       learning_objectives: [
//         "Memahami Virtual DOM dan cara kerja React.",
//         "Mampu membuat dan menyusun komponen React.",
//         "Mengelola state dan props."
//       ],
//       topics: [
//         { title: "Pengenalan React dan JSX", description: "Setup proyek dan sintaks JSX.", completed: false },
//         { title: "Komponen dan Props", description: "Membangun UI modular.", completed: false },
//         { title: "State dan Lifecycle", description: "Mengelola data dalam komponen.", completed: false },
//         { title: "Event Handling di React", description: "Membuat UI interaktif.", completed: false },
//       ],
//       keywords: ["React", "JSX", "Komponen", "State", "Props"]
//     },
//     // Tambahkan modul lain jika perlu
//   ],
// };

export default CurriculumView;
```
Catatan tentang implementasi ini:
*   **Props**: Komponen menerima `curriculum` sebagai prop, yang tipenya adalah `Curriculum` dari `types.ts`.
*   **State Akordeon**: Menggunakan `useState` (`openModuleId`) untuk melacak modul mana yang saat ini terbuka. Hanya satu modul yang bisa terbuka pada satu waktu dalam implementasi ini.
*   **Rendering**:
    *   Menampilkan judul, deskripsi, dan tujuan kurikulum.
    *   Setiap modul dirender sebagai tombol yang dapat diklik untuk membuka/menutup kontennya.
    *   Di dalam setiap modul yang terbuka, tujuan pembelajaran, topik, dan kata kunci ditampilkan.
    *   Topik memiliki ikon tanda centang (jika `topic.completed` adalah `true`) atau ikon lingkaran. Properti `completed` ini adalah tambahan di sisi frontend pada tipe `Topic`.
*   **Styling**: Kelas Tailwind CSS digunakan untuk styling, termasuk untuk membuat tampilan seperti akordeon dan memformat daftar.
*   **Ikon**: SVG inline sederhana digunakan untuk ikon chevron (atas/bawah) dan tanda centang/lingkaran. Anda bisa menggantinya dengan pustaka ikon.
*   **Data Tiruan (Dikomentari)**: Saya menyertakan contoh `mockCurriculumData` yang dikomentari di bagian bawah. Ini berguna untuk pengembangan dan pengujian komponen secara terpisah. Idealnya, data ini akan datang dari state aplikasi utama atau panggilan API.

Langkah selanjutnya adalah membuat `ChatWidget.tsx`.
