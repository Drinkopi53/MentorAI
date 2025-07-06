import React, { useState } from 'react';
import { LearningPath, UpNextItem, Achievement } from '../../types'; // Impor tipe

// Impor ikon (contoh menggunakan Heroicons sebagai SVG inline atau komponen)
// Dalam proyek nyata, Anda akan menginstal @heroicons/react atau pustaka ikon lain
const ChatBubbleOvalLeftEllipsisIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 9.75a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a.38.38 0 0 1 .266-.112c2.008-.05 3.956-.223 5.743-.525C20.285 16.233 21 14.838 21 13.23V7.724c0-1.602-1.123-2.995-2.707-3.228A48.344 48.344 0 0 0 12 4.125C9.715 4.002 7.468 3.884 5.245 3.696A3.003 3.003 0 0 0 2.25 6.696v6.514Zm0 0a3.003 3.003 0 0 0 2.25 2.995" />
  </svg>
);

const TrophyIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 0 1 3 3h-15a3 3 0 0 1 3-3m9 0v-4.5A3.375 3.375 0 0 0 12.75 9.75H11.25A3.375 3.375 0 0 0 7.5 13.125V18.75m9 0h-9" />
  </svg>
);


// Data Tiruan
const mockLearningPath: LearningPath = {
  title: 'Mastering Advanced TypeScript for Frontend Wizards',
  progress: 65,
};

const mockUpNextItem: UpNextItem = {
  id: 'module-5',
  title: 'Module 5: Asynchronous Patterns & Error Handling',
  description: 'Dive deep into async/await, Promises, and robust error handling techniques in TypeScript applications.',
  type: 'module',
};

const mockAchievements: Achievement[] = [
  { id: 'ach1', name: 'TypeScript Initiate', dateAwarded: '2024-07-01', iconUrl: 'path/to/ts-initiate-badge.svg' },
  { id: 'ach2', name: 'React Fundamentals', dateAwarded: '2024-06-15', iconUrl: 'path/to/react-fund-badge.svg' },
  { id: 'ach3', name: 'CSS Grid Guru', dateAwarded: '2024-05-20', iconUrl: 'path/to/css-grid-badge.svg' },
  { id: 'ach4', name: 'First Component', dateAwarded: '2024-06-10', iconUrl: 'path/to/css-grid-badge.svg' },
];

interface DashboardProps {
  onChatIconClick: () => void; // Fungsi untuk menangani klik ikon obrolan
}

const Dashboard: React.FC<DashboardProps> = ({ onChatIconClick }) => {
  const [learningPath] = useState<LearningPath>(mockLearningPath);
  const [upNext] = useState<UpNextItem>(mockUpNextItem);
  const [achievements] = useState<Achievement[]>(mockAchievements);

  // Placeholder untuk komponen yang lebih kompleks
  const ProgressBar: React.FC<{ progress: number }> = ({ progress }) => (
    <div className="w-full bg-gray-200 rounded-full h-6 dark:bg-gray-700">
      <div
        className="bg-blue-600 h-6 rounded-full text-xs font-medium text-blue-100 text-center p-0.5 leading-none"
        style={{ width: `${progress}%` }}
      >
        {progress}%
      </div>
    </div>
  );

  const AchievementCard: React.FC<{ achievement: Achievement }> = ({ achievement }) => (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow flex flex-col items-center text-center">
      {/* Placeholder untuk ikon lencana */}
      <div className="p-2 bg-yellow-400 rounded-full mb-2">
        <TrophyIcon className="h-8 w-8 text-white" />
      </div>
      <h4 className="font-semibold text-sm text-gray-700 dark:text-gray-200">{achievement.name}</h4>
      <p className="text-xs text-gray-500 dark:text-gray-400">{achievement.dateAwarded}</p>
    </div>
  );


  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-4 md:p-8 text-gray-900 dark:text-white">
      <header className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white">
          {learningPath.title}
        </h1>
      </header>

      <main className="space-y-8">
        {/* Bagian Kemajuan */}
        <section className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-1 text-gray-700 dark:text-gray-200">Current Progress</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">You are making great strides! Keep it up.</p>
          <ProgressBar progress={learningPath.progress} />
        </section>

        {/* Bagian "Up Next" */}
        <section className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-3 text-gray-700 dark:text-gray-200">Up Next: {upNext.title}</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-4 text-sm">
            {upNext.description}
          </p>
          <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition duration-150 ease-in-out">
            Start {upNext.type === 'module' ? 'Module' : 'Topic'}
          </button>
        </section>

        {/* Bagian "Recent Achievements" */}
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Recent Achievements</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {achievements.slice(0, 4).map(ach => ( // Tampilkan maksimal 4
              <AchievementCard key={ach.id} achievement={ach} />
            ))}
          </div>
        </section>
      </main>

      {/* Ikon Obrolan Mengambang */}
      <button
        onClick={onChatIconClick}
        title="Open MentorAI Chat"
        className="fixed bottom-6 right-6 md:bottom-8 md:right-8 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-xl transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
      >
        <ChatBubbleOvalLeftEllipsisIcon className="h-8 w-8" />
      </button>
    </div>
  );
};

export default Dashboard;
```
Catatan tentang implementasi ini:
*   **TypeScript**: Komponen ini menggunakan TypeScript (`.tsx`) dan mengimpor tipe dari `../../types`.
*   **Tailwind CSS**: Kelas Tailwind digunakan secara ekstensif untuk styling. Saya telah mencoba membuat tata letak yang responsif secara dasar (`md:`, `sm:`).
*   **Data Tiruan**: Data untuk jalur pembelajaran, item "Up Next", dan pencapaian diambil dari objek tiruan yang didefinisikan di dalam file.
*   **Placeholder Komponen**: `ProgressBar` dan `AchievementCard` diimplementasikan sebagai komponen fungsional sederhana di dalam `Dashboard.tsx` untuk saat ini. Dalam aplikasi yang lebih besar, ini idealnya akan menjadi komponen terpisah.
*   **Ikon**: Saya telah menyertakan kode SVG inline untuk ikon `ChatBubbleOvalLeftEllipsisIcon` dan `TrophyIcon` sebagai contoh. Dalam proyek nyata, Anda mungkin menggunakan pustaka seperti `@heroicons/react` atau mengimpor SVG sebagai komponen.
*   **Props `onChatIconClick`**: Komponen `Dashboard` menerima prop `onChatIconClick`. Ini adalah fungsi callback yang akan dipanggil ketika ikon obrolan diklik, yang memungkinkan komponen induk (misalnya, `App.tsx`) untuk mengelola visibilitas `ChatWidget`.

File ini sekarang menyediakan kerangka kerja visual dasar untuk dasbor. Langkah selanjutnya adalah membuat `CurriculumView.tsx`.
