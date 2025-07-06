import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Asumsikan react-router-dom digunakan
import { ForumPostData, PostAuthor } from '../../types'; // Impor tipe

// Ikon contoh
const ChatBubbleLeftRightIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3.543-3.543a.75.75 0 0 0-.53-.22H6.75a2.25 2.25 0 0 1-2.25-2.25V6.75a2.25 2.25 0 0 1 2.25-2.25H15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
  </svg>
);
const ArrowUpIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 10.5 12 3m0 0 7.5 7.5M12 3v18" />
  </svg>
);
const PlusCircleIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
 <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

const defaultUserProfilePic = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0idy02IGgtNiI+CiAgPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMTguNzUgMTkuMTI1Yy0xLjU5MS41MzItMy4zNTMuODI1LTUuMjUuODI1Yy0xLjg5NyAwLTMuNjU5LS4yOTMtNS4yNS0uODI1QzYuNzI2IDE5LjEyNSA1LjI1IDE5LjkzNiA1LjI1IDIxLjM3NWMwIC42MjEuMzU0IDEuMTg2Ljg3OCAxLjQ5M2MuNTI1LjMwNyAxLjE2My40NyAxLjgyMi40N2gzLjc1YzEuMTMxIDAgMi4xNzYtLjQ1NyAyLjkyOS0xLjIwNGMuNzUzLS43NDcgMS4yMDEtMS43NzIgMS4yMDEtMi45MjdjMC0xLjQzOC0xLjQ3Ni0yLjI1LTMyLjcyNC0yLjI1Wk0xMiAzdDMuMzg2IDYuOTE0YzEuMTg3LjI1NiAyLjIzMy45OTMgMi43NjcgMi4wMDFjLjU1MiAxLjAyOC44NDcgMi4xNDYuODQ3IDMuMjg2YzAgMy4xNzItMi45MDEgNS43NS02LjUgNS43NVM1LjUgMTguNDE4IDUuNSAxNS4yNWMwLTEuMTQuMjk1LTIuMjU4Ljg0Ny0zLjI4NmMuNTM0LTEuMDA3IDEuNTgtMS43NDQgMi43NjctMi4wMDFMMTIgM1oiIGNsaXAtcnVsZT0iZXZlbm9kZCIgLz4KPC9zdmc+Cg==";


// Data Tiruan untuk Forum (ganti dengan pengambilan data API nanti)
const mockForumPosts: ForumPostData[] = [
  {
    id: 1,
    author: { id: 1, username: 'SarahW', profile_picture_url: undefined },
    title: 'Bagaimana cara terbaik belajar Async/Await di JavaScript?',
    content: 'Saya sedikit bingung dengan Promise dan Async/Await. Ada sumber daya atau tips yang bagus untuk pemula?',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 jam lalu
    upvotes: 15,
    replies: [], // Di Forum.tsx kita mungkin hanya butuh jumlah balasan
    reply_count: 3
  },
  {
    id: 2,
    author: { id: 2, username: 'CodeNinja', profile_picture_url: defaultUserProfilePic },
    title: 'Diskusi: State Management di React - Context API vs Redux vs Zustand',
    content: 'Mana yang menjadi favorit kalian untuk proyek skala menengah dan mengapa? Mari berbagi pengalaman!',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1).toISOString(), // 1 hari lalu
    upvotes: 28,
    replies: [],
    reply_count: 12
  },
  {
    id: 3,
    author: { id: 3, username: 'UXQueen', profile_picture_url: undefined },
    title: 'Tips Desain UI/UX untuk Aplikasi Mobile yang Kompleks',
    content: 'Saya sedang mengerjakan proyek dengan banyak fitur dan navigasi. Bagaimana cara menjaga UX tetap intuitif?',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(), // 3 hari lalu
    upvotes: 8,
    replies: [],
    reply_count: 5
  },
];


const Forum: React.FC = () => {
  const [posts, setPosts] = useState<ForumPostData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPosts = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Ganti dengan URL API backend Anda yang sebenarnya untuk mengambil postingan forum
        // Asumsikan endpointnya adalah /api/forum/posts
        const response = await fetch('/api/forum/posts?limit=20'); // Ambil 20 postingan terbaru
        if (!response.ok) {
          throw new Error(`Gagal mengambil postingan forum: ${response.statusText}`);
        }
        const data: ForumPostData[] = await response.json();
        setPosts(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan tidak diketahui.';
        console.error("Error fetching forum posts:", errorMessage);
        setError(errorMessage);
        // Jika API gagal, gunakan data tiruan untuk pengembangan
        console.warn("Menggunakan data tiruan karena API gagal atau belum diimplementasikan.");
        setPosts(mockForumPosts);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosts();
  }, []);

  const handleCreatePost = () => {
    // Arahkan ke halaman/komponen pembuatan postingan baru
    // Misalnya: navigate('/forum/create-post');
    alert("Navigasi ke halaman buat postingan baru (belum diimplementasikan).");
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-10">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
        <p className="ml-4 text-lg text-gray-600 dark:text-gray-300">Memuat Forum Diskusi...</p>
      </div>
    );
  }

  if (error && posts.length === 0) { // Hanya tampilkan error jika tidak ada data tiruan
    return <div className="text-center p-10 text-red-500 dark:text-red-400">Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white">
          Forum Diskusi MentorAI
        </h1>
        <button
          onClick={handleCreatePost}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition duration-150 ease-in-out"
        >
          <PlusCircleIcon className="h-5 w-5 mr-2" />
          Buat Postingan Baru
        </button>
      </div>

      {posts.length === 0 && !isLoading && (
         <div className="text-center p-10 text-gray-500 dark:text-gray-400">
            Belum ada postingan di forum. Jadilah yang pertama memulai diskusi!
        </div>
      )}

      <div className="space-y-6">
        {posts.map((post) => (
          <div
            key={post.id}
            className="bg-white dark:bg-gray-800 shadow-lg rounded-xl p-5 md:p-6 hover:shadow-xl transition-shadow duration-200"
          >
            <div className="flex items-start space-x-3 mb-3">
              <img
                src={post.author.profile_picture_url || defaultUserProfilePic}
                alt={post.author.username}
                className="h-10 w-10 rounded-full object-cover"
              />
              <div>
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">{post.author.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(post.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })} - {new Date(post.created_at).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>

            <Link to={`/forum/post/${post.id}`} className="block mb-2 group">
              <h2 className="text-xl md:text-2xl font-bold text-blue-600 dark:text-blue-400 group-hover:underline decoration-blue-500 decoration-2">
                {post.title}
              </h2>
            </Link>

            <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed line-clamp-3 mb-4">
              {post.content}
            </p>

            <div className="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-3">
                <button className="flex items-center hover:text-green-500 dark:hover:text-green-400 transition-colors">
                  <ArrowUpIcon className="h-4 w-4 mr-1" /> {post.upvotes} Upvotes
                </button>
                <Link to={`/forum/post/${post.id}#replies`} className="flex items-center hover:text-blue-500 dark:hover:text-blue-400 transition-colors">
                  <ChatBubbleLeftRightIcon className="h-4 w-4 mr-1" /> {post.reply_count || 0} Balasan
                </Link>
              </div>
              <Link
                to={`/forum/post/${post.id}`}
                className="px-4 py-1.5 text-xs bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 font-semibold rounded-md transition-colors"
              >
                Lihat Diskusi
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Forum;
```
Catatan:
*   **Pengambilan Data**: Menggunakan `useEffect` untuk mengambil daftar postingan dari `/api/forum/posts`. Saat ini, jika API gagal, ia akan fallback ke `mockForumPosts` untuk tujuan pengembangan.
*   **Tampilan Postingan**: Setiap postingan ditampilkan sebagai kartu dengan judul, informasi penulis (termasuk gambar profil placeholder), tanggal, sebagian konten (menggunakan `line-clamp-3` dari Tailwind untuk membatasi jumlah baris), jumlah upvote, dan jumlah balasan.
*   **Navigasi**:
    *   Tombol "Buat Postingan Baru" saat ini hanya memicu `alert`. Ini akan mengarahkan ke formulir pembuatan postingan.
    *   Judul postingan dan tombol "Lihat Diskusi" adalah `Link` dari `react-router-dom` yang akan mengarahkan ke `PostDetail.tsx` dengan ID postingan.
*   **Styling**: Kelas Tailwind CSS digunakan untuk styling kartu postingan dan elemen lainnya.
*   **Ikon**: Ikon SVG inline sederhana digunakan.

Langkah selanjutnya adalah membuat `PostDetail.tsx`.
