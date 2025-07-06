import React, { useState, useEffect } from 'react';
import { UserPublic } from '../../types'; // Impor tipe UserPublic

// Ikon contoh
const StarIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path fillRule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.006 5.404.434c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.434 2.082-5.005Z" clipRule="evenodd" />
  </svg>
);

const defaultUserProfilePic = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0idy02IGgtNiI+CiAgPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMTguNzUgMTkuMTI1Yy0xLjU5MS41MzItMy4zNTMuODI1LTUuMjUuODI1Yy0xLjg5NyAwLTMuNjU5LS4yOTMtNS4yNS0uODI1QzYuNzI2IDE5LjEyNSA1LjI1IDE5LjkzNiA1LjI1IDIxLjM3NWMwIC42MjEuMzU0IDEuMTg2Ljg3OCAxLjQ5M2MuNTI1LjMwNyAxLjE2My40NyAxLjgyMi40N2gzLjc1YzEuMTMxIDAgMi4xNzYtLjQ1NyAyLjkyOS0xLjIwNGMuNzUzLS43NDcgMS4yMDEtMS43NzIgMS4yMDEtMi45MjdjMC0xLjQzOC0xLjQ3Ni0yLjI1LTMyLjcyNC0yLjI1Wk0xMiAzdDMuMzg2IDYuOTE0YzEuMTg3LjI1NiAyLjIzMy45OTMgMi43NjcgMi4wMDFjLjU1MiAxLjAyOC44NDcgMi4xNDYuODQ3IDMuMjg2YzAgMy4xNzItMi45MDEgNS43NS02LjUgNS43NVM1LjUgMTguNDE4IDUuNSAxNS4yNWMwLTEuMTQuMjk1LTIuMjU4Ljg0Ny0zLjI4NmMuNTM0LTEuMDA3IDEuNTgtMS43NDQgMi43NjctMi4wMDFMMTIgM1oiIGNsaXAtcnVsZT0iZXZlbm9kZCIgLz4KPC9zdmc+Cg=="; // Placeholder SVG sederhana


const Leaderboard: React.FC = () => {
  const [leaderboardData, setLeaderboardData] = useState<UserPublic[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Ganti dengan URL API backend Anda yang sebenarnya untuk leaderboard
        // Asumsikan endpointnya adalah /api/users/leaderboard (sesuai router users.py)
        // dan sudah termasuk dalam --root-path /api jika ada
        const response = await fetch('/api/users/leaderboard?limit=10');
        if (!response.ok) {
          throw new Error(`Gagal mengambil data leaderboard: ${response.statusText}`);
        }
        const data: UserPublic[] = await response.json();
        setLeaderboardData(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan tidak diketahui.';
        console.error("Error fetching leaderboard:", errorMessage);
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-10">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
        <p className="ml-4 text-lg text-gray-600 dark:text-gray-300">Memuat Papan Peringkat...</p>
      </div>
    );
  }

  if (error) {
    return <div className="text-center p-10 text-red-500 dark:text-red-400">Error: {error}</div>;
  }

  if (leaderboardData.length === 0) {
    return <div className="text-center p-10 text-gray-500 dark:text-gray-400">Papan peringkat masih kosong. Jadilah yang pertama!</div>;
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <h1 className="text-3xl md:text-4xl font-bold text-center mb-8 text-gray-800 dark:text-white">
        🏆 Papan Peringkat MentorAI 🏆
      </h1>
      <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg overflow-hidden">
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {leaderboardData.map((user, index) => (
            <li key={user.id} className={`p-4 md:p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-150 ${index < 3 ? 'bg-yellow-50 dark:bg-yellow-800/20' : ''}`}>
              <div className="flex items-center space-x-4">
                <span className={`text-xl font-semibold w-8 text-center ${
                  index === 0 ? 'text-yellow-500' :
                  index === 1 ? 'text-gray-400 dark:text-gray-300' :
                  index === 2 ? 'text-yellow-700 dark:text-yellow-600' :
                  'text-gray-500 dark:text-gray-400'
                }`}>
                  {index + 1}
                </span>
                <img
                  src={user.profile_picture_url || defaultUserProfilePic}
                  alt={user.username}
                  className="h-12 w-12 rounded-full object-cover border-2 border-gray-300 dark:border-gray-600"
                />
                <div className="flex-grow">
                  <p className="text-lg font-medium text-blue-600 dark:text-blue-400 truncate">{user.username}</p>
                  {/* Anda bisa menambahkan detail lain seperti jumlah lencana jika ada di UserPublic */}
                </div>
                <div className="flex items-center text-lg font-semibold text-yellow-500 dark:text-yellow-400">
                  <StarIcon className="h-5 w-5 mr-1" />
                  {user.xp_points.toLocaleString()} XP
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
      <p className="text-center mt-6 text-sm text-gray-500 dark:text-gray-400">
        Teruslah belajar dan raih peringkat teratas!
      </p>
    </div>
  );
};

export default Leaderboard;
```
Catatan:
*   **Pengambilan Data**: Menggunakan `useEffect` dan `fetch` untuk mengambil data dari `/api/users/leaderboard` (sesuai dengan router backend yang direncanakan). Penanganan status `isLoading` dan `error` disertakan.
*   **Tampilan**: Menampilkan daftar pengguna dengan peringkat, gambar profil (dengan placeholder jika tidak ada), nama pengguna, dan poin XP.
*   **Styling**: Kelas Tailwind CSS digunakan untuk styling, termasuk highlight untuk 3 peringkat teratas.
*   **Ikon**: Ikon `StarIcon` sederhana disertakan. Placeholder SVG untuk gambar profil default juga ada.
*   **URL API**: Pastikan URL `/api/users/leaderboard` benar dan sesuai dengan konfigurasi `REACT_APP_API_BASE_URL` atau proxy di `package.json` jika frontend dan backend berjalan di port yang berbeda selama pengembangan.

Komponen ini siap untuk menampilkan data leaderboard. Selanjutnya adalah komponen Forum.
