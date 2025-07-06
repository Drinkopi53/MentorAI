// Mencerminkan backend/app/schemas.py

export interface Topic {
  title: string;
  description?: string | null;
  completed?: boolean; // Properti khusus frontend
}

export interface Module {
  title: string;
  description?: string | null;
  learning_objectives: string[];
  topics: Topic[];
  keywords: string[];
}

export interface Curriculum {
  goal: string;
  title: string;
  description?: string | null;
  modules: Module[];
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface LearningPath {
  title: string;
  progress: number;
}

export interface UpNextItem {
  id: string;
  title: string;
  description: string;
  type: 'module' | 'topic' | 'quiz';
}

export interface Achievement {
  id: string;
  name: string;
  iconUrl?: string;
  dateAwarded: string;
}

// --- Tipe Baru untuk Gamifikasi dan Komunitas ---

export interface UserPublic {
  id: number;
  username: string;
  xp_points: number;
  profile_picture_url?: string | null;
  // Tambahkan info publik lain jika ada, misal jumlah lencana
}

export interface Badge {
  id: number;
  name: string;
  description?: string | null;
  icon_url?: string | null;
  criteria?: string | null;
}

export interface UserBadge {
  awarded_at: string; // atau Date jika Anda akan mengonversinya
  badge: Badge; // Detail lencana yang bersarang
}

export interface UserProfile extends UserPublic { // Bisa lebih detail dari UserPublic
  email?: string; // Hanya untuk pengguna yang login
  full_name?: string | null;
  streak_days: number;
  created_at: string; // atau Date
  is_active: boolean;
  badges: UserBadge[];
}


// Tipe untuk Forum
export interface PostAuthor {
  id: number;
  username: string;
  profile_picture_url?: string | null;
}

export interface ForumReplyData {
  id: number;
  post_id: number;
  author: PostAuthor;
  content: string;
  parent_reply_id?: number | null;
  created_at: string; // atau Date
  updated_at?: string | null; // atau Date
  upvotes: number;
  // child_replies: ForumReplyData[]; // Untuk balasan berulir, bisa ditambahkan
}

export interface ForumPostData {
  id: number;
  author: PostAuthor;
  title: string;
  content: string;
  created_at: string; // atau Date
  updated_at?: string | null; // atau Date
  upvotes: number;
  replies: ForumReplyData[]; // Untuk PostReadWithReplies
  reply_count?: number; // Opsional, jika backend mengirimkannya
}

// Tipe untuk request pembuatan postingan/balasan
export interface PostCreatePayload {
  title: string;
  content: string;
  // author_id akan ditangani oleh backend (dari pengguna yang terotentikasi)
}

export interface ReplyCreatePayload {
  content: string;
  post_id: number; // Diperlukan saat mengirim, tapi mungkin tidak di form jika sudah di konteks post
  parent_reply_id?: number | null;
  // author_id akan ditangani oleh backend
}
```
Catatan:
*   Saya telah menambahkan `UserPublic`, `Badge`, `UserBadge`, `UserProfile` (versi lebih detail dari `UserReadWithBadges`), `PostAuthor`, `ForumReplyData`, dan `ForumPostData`.
*   Untuk `created_at`, `updated_at`, dan `awarded_at`, saya menggunakan `string` karena biasanya data JSON mengirim tanggal sebagai string ISO. Anda dapat mengonversinya menjadi objek `Date` di frontend jika diperlukan.
*   `ForumReplyData` menyertakan `parent_reply_id` untuk balasan berulir. Representasi `child_replies` juga dikomentari sebagai kemungkinan.
*   `PostCreatePayload` dan `ReplyCreatePayload` ditambahkan untuk tipe data saat mengirim postingan/balasan baru. `author_id` diasumsikan akan ditangani oleh backend dari sesi pengguna yang terotentikasi.

Dengan file `types.ts` ini, kita memiliki dasar tipe yang kuat untuk komponen frontend.
