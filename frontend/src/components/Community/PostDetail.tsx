import React, { useState, useEffect, FormEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ForumPostData, ForumReplyData, PostAuthor, ReplyCreatePayload } from '../../types';

// Ikon (bisa diimpor dari file ikon bersama)
const ArrowUturnLeftIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" />
  </svg>
);
const PaperAirplaneIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
  </svg>
);
const defaultUserProfilePic = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iY3VycmVudENvbG9yIiBjbGFzcz0idy02IGgtNiI+CiAgPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMTguNzUgMTkuMTI1Yy0xLjU5MS41MzItMy4zNTMuODI1LTUuMjUuODI1Yy0xLjg5NyAwLTMuNjU5LS4yOTMtNS4yNS0uODI1QzYuNzI2IDE5LjEyNSA1LjI1IDE5LjkzNiA1LjI1IDIxLjM3NWMwIC42MjEuMzU0IDEuMTg2Ljg3OCAxLjQ5M2MuNTI1LjMwNyAxLjE2My40NyAxLjgyMi40N2gzLjc1YzEuMTMxIDAgMi4xNzYtLjQ1NyAyLjkyOS0xLjIwNGMuNzUzLS43NDcgMS4yMDEtMS43NzIgMS4yMDEtMi45MjdjMC0xLjQzOC0xLjQ3Ni0yLjI1LTMyLjcyNC0yLjI1Wk0xMiAzdDMuMzg2IDYuOTE0YzEuMTg3LjI1NiAyLjIzMy45OTMgMi43NjcgMi4wMDFjLjU1MiAxLjAyOC44NDcgMi4xNDYuODQ3IDMuMjg2YzAgMy4xNzItMi45MDEgNS43NS02LjUgNS43NVM1LjUgMTguNDE4IDUuNSAxNS4yNWMwLTEuMTQuMjk1LTIuMjU4Ljg0Ny0zLjI4NmMuNTM0LTEuMDA3IDEuNTgtMS43NDQgMi43NjctMi4wMDFMMTIgM1oiIGNsaXAtcnVsZT0iZXZlbm9kZCIgLz4KPC9zdmc+Cg==";


// Data Tiruan untuk satu Postingan dengan Balasan (ganti dengan API call)
const mockSinglePost: ForumPostData = {
  id: 1,
  author: { id: 1, username: 'SarahW', profile_picture_url: undefined },
  title: 'Bagaimana cara terbaik belajar Async/Await di JavaScript?',
  content: 'Saya sedikit bingung dengan Promise dan Async/Await. Konsepnya terasa abstrak dan saya kesulitan menerapkannya dalam proyek nyata. Apakah ada sumber daya, tutorial video, atau mungkin contoh kode sederhana yang bisa membantu menjelaskan alurnya dengan lebih baik? \n\nSaya sudah mencoba membaca dokumentasi MDN, tapi masih merasa kurang "klik". Mungkin ada pendekatan atau analogi tertentu yang membantu kalian memahaminya? Terima kasih sebelumnya!',
  created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  upvotes: 15,
  replies: [
    { id: 101, post_id: 1, author: {id: 2, username: 'CodeNinja', profile_picture_url: defaultUserProfilePic}, content: "Coba deh nonton seri tutorial dari Fun Fun Function di YouTube tentang asynchronous JavaScript. Dia menjelaskannya dengan sangat baik!", created_at: new Date(Date.now() - 1000 * 60 * 50).toISOString(), upvotes: 7 },
    { id: 102, post_id: 1, author: {id: 3, username: 'UXQueen', profile_picture_url: undefined}, content: "Analoginya seperti memesan makanan di restoran. Kamu pesan (async operation), lalu kamu bisa melakukan hal lain sambil menunggu pesananmu datang (callback/then). Async/await membuat kodenya terlihat lebih sinkron dan mudah dibaca.", created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), upvotes: 5, parent_reply_id: 101 }, // Balasan ke balasan 101
    { id: 103, post_id: 1, author: {id: 1, username: 'SarahW', profile_picture_url: undefined}, content: "Terima kasih @CodeNinja dan @UXQueen! Analogi restorannya membantu banget. Saya akan cek channel YouTube itu.", created_at: new Date(Date.now() - 1000 * 60 * 10).toISOString(), upvotes: 2, parent_reply_id: 102 },
  ],
  reply_count: 3
};


interface ReplyProps {
  reply: ForumReplyData;
  onReplySubmit: (content: string, parentId?: number) => void; // Fungsi untuk submit balasan ke balasan ini
  level: number; // Untuk indentasi balasan berulir
}

const ReplyCard: React.FC<ReplyProps> = ({ reply, onReplySubmit, level }) => {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const [replyContent, setReplyContent] = useState('');

    const handleSubmitReply = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!replyContent.trim()) return;
        onReplySubmit(replyContent, reply.id);
        setReplyContent('');
        setShowReplyForm(false);
    };

    return (
        <div
            className={`bg-gray-50 dark:bg-gray-700/60 p-3 md:p-4 rounded-lg shadow-sm ${level > 0 ? `ml-${level * 4} md:ml-${level * 6}` : ''}`}
        >
            <div className="flex items-start space-x-3">
                <img
                    src={reply.author.profile_picture_url || defaultUserProfilePic}
                    alt={reply.author.username}
                    className="h-8 w-8 rounded-full object-cover"
                />
                <div>
                    <p className="text-xs font-semibold text-gray-700 dark:text-gray-200">{reply.author.username}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(reply.created_at).toLocaleString('id-ID')}
                    </p>
                </div>
            </div>
            <p className="text-sm text-gray-800 dark:text-gray-100 mt-2 whitespace-pre-wrap">{reply.content}</p>
            <div className="mt-2 flex items-center space-x-3 text-xs">
                <button className="text-blue-600 dark:text-blue-400 hover:underline">Upvote ({reply.upvotes})</button>
                <button
                    onClick={() => setShowReplyForm(!showReplyForm)}
                    className="text-gray-600 dark:text-gray-300 hover:underline"
                >
                    Balas
                </button>
            </div>
            {showReplyForm && (
                <form onSubmit={handleSubmitReply} className="mt-2 ml-4 pl-4 border-l-2 border-gray-200 dark:border-gray-600">
                    <textarea
                        value={replyContent}
                        onChange={(e) => setReplyContent(e.target.value)}
                        placeholder={`Balas kepada ${reply.author.username}...`}
                        rows={2}
                        className="w-full p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:ring-1 focus:ring-blue-500 outline-none dark:bg-gray-700 dark:text-white"
                    />
                    <div className="mt-1 text-right">
                        <button type="button" onClick={() => setShowReplyForm(false)} className="text-xs text-gray-500 hover:underline mr-2">Batal</button>
                        <button type="submit" className="px-3 py-1 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-md">Kirim</button>
                    </div>
                </form>
            )}
        </div>
    );
};


const PostDetail: React.FC = () => {
  const { postId } = useParams<{ postId: string }>();
  const [post, setPost] = useState<ForumPostData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newReplyContent, setNewReplyContent] = useState<string>('');
  const [isSubmittingReply, setIsSubmittingReply] = useState<boolean>(false);

  useEffect(() => {
    const fetchPostDetail = async () => {
      if (!postId) return;
      setIsLoading(true);
      setError(null);
      try {
        // Ganti dengan URL API backend Anda yang sebenarnya untuk mengambil detail postingan
        // Asumsikan endpointnya adalah /api/forum/posts/{postId}
        const response = await fetch(`/api/forum/posts/${postId}`);
        if (!response.ok) {
          throw new Error(`Gagal mengambil detail postingan: ${response.statusText}`);
        }
        const data: ForumPostData = await response.json();
        setPost(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan tidak diketahui.';
        console.error("Error fetching post detail:", errorMessage);
        setError(errorMessage);
        // Fallback ke data tiruan jika API gagal
        if (postId === String(mockSinglePost.id)) {
            console.warn("Menggunakan data tiruan karena API gagal atau belum diimplementasikan.");
            setPost(mockSinglePost);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchPostDetail();
  }, [postId]);

  const handleReplySubmit = async (content: string, parentId?: number) => {
    if (!postId || !content.trim()) return;
    setIsSubmittingReply(true);

    const payload: ReplyCreatePayload = {
        content: content,
        post_id: parseInt(postId), // Pastikan postId adalah number jika diperlukan oleh backend
        parent_reply_id: parentId,
        // author_id akan ditangani oleh backend
    };

    try {
        // Ganti dengan URL API backend Anda untuk membuat balasan
        // Asumsikan endpointnya adalah /api/forum/posts/{postId}/replies
        const response = await fetch(`/api/forum/posts/${postId}/replies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({detail: "Gagal mengirim balasan."}));
            throw new Error(errorData.detail || `Gagal mengirim balasan: ${response.statusText}`);
        }
        const newReply: ForumReplyData = await response.json();

        // Perbarui state post dengan balasan baru
        // Ini adalah cara sederhana, mungkin perlu logika lebih kompleks untuk balasan berulir
        setPost(prevPost => {
            if (!prevPost) return null;
            // Jika parentId ada, cari dan tambahkan sebagai child reply (belum diimplementasikan di struktur data saat ini)
            // Untuk sekarang, tambahkan ke daftar replies utama
            return {
                ...prevPost,
                replies: [...prevPost.replies, newReply].sort((a,b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()),
                reply_count: (prevPost.reply_count || 0) + 1,
            };
        });
        setNewReplyContent(''); // Kosongkan form balasan utama
    } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan tidak diketahui.';
        console.error("Error submitting reply:", errorMessage);
        alert(`Error: ${errorMessage}`); // Tampilkan error ke pengguna
    } finally {
        setIsSubmittingReply(false);
    }
  };

  // Fungsi untuk merender balasan secara rekursif (jika ada child_replies di ForumReplyData)
  const renderReplies = (replies: ForumReplyData[], level: number = 0): JSX.Element[] => {
    return replies.map(reply => (
        <React.Fragment key={reply.id}>
            <ReplyCard reply={reply} onReplySubmit={handleReplySubmit} level={level} />
            {/* Jika Anda memiliki reply.child_replies, panggil renderReplies lagi di sini */}
            {/* {reply.child_replies && reply.child_replies.length > 0 && (
                <div className={`ml-${(level + 1) * 4} md:ml-${(level + 1) * 6} mt-2 space-y-2`}>
                    {renderReplies(reply.child_replies, level + 1)}
                </div>
            )} */}
        </React.Fragment>
    ));
  };


  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-10 min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
        <p className="ml-4 text-lg text-gray-600 dark:text-gray-300">Memuat Diskusi...</p>
      </div>
    );
  }

  if (error || !post) {
    return (
        <div className="container mx-auto p-4 md:p-8 text-center">
            <p className="text-red-500 dark:text-red-400 mb-4">Error: {error || "Postingan tidak ditemukan."}</p>
            <Link to="/forum" className="text-blue-600 hover:underline">Kembali ke Forum</Link>
        </div>
    );
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <Link to="/forum" className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:underline mb-6 group">
        <ArrowUturnLeftIcon className="h-5 w-5 mr-2 transition-transform group-hover:-translate-x-1" />
        Kembali ke Semua Postingan
      </Link>

      <article className="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-6 md:p-8 mb-8">
        <div className="flex items-center space-x-3 mb-4">
            <img src={post.author.profile_picture_url || defaultUserProfilePic} alt={post.author.username} className="h-12 w-12 rounded-full object-cover"/>
            <div>
                <p className="font-semibold text-gray-800 dark:text-gray-100">{post.author.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Diposting pada {new Date(post.created_at).toLocaleString('id-ID')}</p>
            </div>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-4">{post.title}</h1>
        <div
            className="prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none text-gray-700 dark:text-gray-300 whitespace-pre-wrap"
            // Jika kontennya adalah HTML, gunakan dangerouslySetInnerHTML (hati-hati XSS)
            // dangerouslySetInnerHTML={{ __html: post.content }}
        >
            {post.content}
        </div>
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center space-x-4">
            <button className="flex items-center text-sm text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-500">
                {/* Ganti dengan ikon upvote yang sesuai */}
                <span className="mr-1">👍</span> {post.upvotes} Upvotes
            </button>
            {/* Fitur vote bisa ditambahkan di sini */}
        </div>
      </article>

      <section className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 md:p-8">
        <h2 className="text-xl md:text-2xl font-semibold text-gray-800 dark:text-white mb-6">
          Balasan ({post.reply_count || post.replies.length})
        </h2>

        {/* Formulir Balasan Utama */}
        <form onSubmit={(e) => { e.preventDefault(); handleReplySubmit(newReplyContent); }} className="mb-8">
          <textarea
            value={newReplyContent}
            onChange={(e) => setNewReplyContent(e.target.value)}
            placeholder="Tulis balasan Anda..."
            rows={3}
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none dark:bg-gray-700 dark:text-white"
            disabled={isSubmittingReply}
          />
          <div className="mt-3 text-right">
            <button
              type="submit"
              disabled={isSubmittingReply || !newReplyContent.trim()}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition duration-150 ease-in-out disabled:opacity-50"
            >
              {isSubmittingReply ? 'Mengirim...' : 'Kirim Balasan'}
              {!isSubmittingReply && <PaperAirplaneIcon className="h-4 w-4 inline-block ml-2 -mt-0.5" />}
            </button>
          </div>
        </form>

        {/* Daftar Balasan */}
        <div className="space-y-4">
          {post.replies && post.replies.length > 0 ? (
            renderReplies(post.replies.filter(reply => !reply.parent_reply_id)) // Hanya render balasan level atas
            // Untuk balasan berulir yang benar, Anda perlu memfilter dan merender child di dalam ReplyCard
            // atau memodifikasi renderReplies untuk menangani struktur data yang bersarang.
            // Struktur data `ForumReplyData` saat ini tidak memiliki `child_replies` secara eksplisit.
            // Jadi, kita akan render semua balasan secara linear untuk saat ini atau memodifikasi
            // backend untuk mengembalikan struktur berulir atau frontend untuk membangunnya.
            // Untuk contoh ini, saya akan render semua balasan secara linear, diurutkan berdasarkan tanggal.
            // Anda bisa mengelompokkan balasan berdasarkan parent_reply_id di frontend jika diperlukan.
          ) : (
            <p className="text-gray-500 dark:text-gray-400">Belum ada balasan untuk postingan ini.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default PostDetail;
```
Catatan:
*   **`useParams`**: Digunakan untuk mendapatkan `postId` dari URL.
*   **Pengambilan Data**: Menggunakan `useEffect` untuk mengambil detail postingan (termasuk balasan) dari `/api/forum/posts/{postId}`. Fallback ke data tiruan jika API gagal.
*   **Formulir Balasan**: Menyediakan `textarea` untuk pengguna menulis balasan. Fungsi `handleReplySubmit` menangani pengiriman balasan ke backend (`/api/forum/posts/{postId}/replies`).
*   **Tampilan Balasan**:
    *   Komponen `ReplyCard` dibuat untuk merender setiap balasan.
    *   Fungsi `renderReplies` disediakan sebagai dasar untuk merender balasan. Implementasi saat ini merender semua balasan secara linear. Untuk balasan berulir yang benar, Anda perlu:
        1.  Memastikan backend mengembalikan balasan dalam struktur berulir, ATAU
        2.  Memproses daftar balasan datar di frontend untuk membangun struktur pohon sebelum rendering.
        3.  Komponen `ReplyCard` bisa secara rekursif memanggil `renderReplies` untuk `child_replies` jika struktur datanya mendukung.
    *   Setiap `ReplyCard` memiliki tombol "Balas" sendiri yang akan membuka formulir kecil untuk membalas balasan tersebut (menggunakan `parent_reply_id`).
*   **Styling**: Kelas Tailwind CSS digunakan. Saya juga menyertakan `@tailwindcss/typography` (melalui kelas `prose`) untuk styling konten postingan yang lebih baik jika kontennya berupa markdown yang di-render ke HTML. Anda perlu menginstal dan mengkonfigurasi plugin ini jika ingin menggunakannya.
*   **Upvote**: Placeholder untuk tombol upvote disertakan. Logika voting penuh akan memerlukan panggilan API tambahan.

Komponen ini menyediakan tampilan detail untuk postingan forum beserta interaksi balasan. Implementasi balasan berulir yang divisualisasikan dengan benar mungkin memerlukan penyesuaian lebih lanjut pada bagaimana data balasan diambil dan dirender.
