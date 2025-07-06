import React, { useState, useEffect, useRef, FormEvent } from 'react';
import { ChatMessage } from '../../types'; // Impor tipe ChatMessage

// Ikon contoh (Anda akan menggunakan pustaka ikon atau SVG Anda sendiri)
const PaperAirplaneIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
  </svg>
);

const XMarkIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
  </svg>
);


interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (isOpen) {
      // Fokus pada input field ketika widget terbuka
      inputRef.current?.focus();
      // Tambahkan pesan sambutan jika belum ada pesan
      if (messages.length === 0) {
        setMessages([
          {
            id: 'welcome-' + Date.now(),
            sender: 'ai',
            text: 'Halo! Saya MentorAI, tutor virtual Anda. Ada yang bisa saya bantu hari ini?',
            timestamp: new Date(),
          },
        ]);
      }
    }
  }, [isOpen]); // Hanya jalankan saat isOpen berubah


  const handleSendMessage = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const userMessageText = inputValue.trim();
    if (!userMessageText) return;

    const newUserMessage: ChatMessage = {
      id: 'user-' + Date.now(),
      sender: 'user',
      text: userMessageText,
      timestamp: new Date(),
    };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInputValue('');
    setIsLoading(true);

    // Tambahkan pesan AI placeholder dengan status isStreaming
    const aiMessageId = 'ai-' + Date.now();
    const placeholderAiMessage: ChatMessage = {
      id: aiMessageId,
      sender: 'ai',
      text: '', // Teks akan diisi oleh stream
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages(prevMessages => [...prevMessages, placeholderAiMessage]);

    try {
      const response = await fetch('/api/chat', { // Pastikan URL ini benar
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessageText }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Gagal mengambil detail error."}));
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}. Detail: ${errorData.detail || "Tidak ada detail tambahan."}`);
      }

      // Proses stream dari backend
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let streamedText = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          streamedText += chunk;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId ? { ...msg, text: streamedText } : msg
            )
          );
        }
      }
      // Setelah stream selesai, update pesan AI terakhir untuk menandakan stream selesai
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMessageId ? { ...msg, isStreaming: false, text: streamedText || "Maaf, saya tidak dapat memberikan respons saat ini." } : msg
        )
      );

    } catch (error) {
      console.error('Error sending message or processing stream:', error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMessageId ? { ...msg, text: `Maaf, terjadi kesalahan: ${error instanceof Error ? error.message : String(error)}`, isStreaming: false } : msg
        )
      );
    } finally {
      setIsLoading(false);
      // Fokus kembali ke input setelah mengirim
      inputRef.current?.focus();
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed bottom-20 right-6 md:bottom-24 md:right-8 w-full max-w-md h-[70vh] max-h-[600px] bg-white dark:bg-gray-800 rounded-xl shadow-2xl flex flex-col z-50 transform transition-all duration-300 ease-out">
      {/* Header Widget */}
      <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">MentorAI Tutor</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          aria-label="Close chat"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>
      </div>

      {/* Area Pesan */}
      <div className="flex-grow p-4 space-y-4 overflow-y-auto bg-gray-50 dark:bg-gray-700/50">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[75%] p-3 rounded-xl ${
                message.sender === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-100 rounded-bl-none'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">
                {message.text}
                {message.isStreaming && <span className="inline-block w-1 h-4 ml-1 bg-gray-500 dark:bg-gray-300 animate-pulse rounded-full"></span>}
              </p>
              <p className={`text-xs mt-1 ${message.sender === 'user' ? 'text-blue-200 text-right' : 'text-gray-500 dark:text-gray-400 text-left'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} /> {/* Elemen dummy untuk auto-scroll */}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ketik pertanyaan Anda..."
            disabled={isLoading}
            className="flex-grow p-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none dark:bg-gray-700 dark:text-white disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
            aria-label="Send message"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <PaperAirplaneIcon className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatWidget;
```
Catatan tentang implementasi ini:
*   **Props `isOpen` dan `onClose`**: Komponen ini menerima `isOpen` untuk mengontrol visibilitasnya dan `onClose` sebagai callback untuk menutup widget. Ini akan dikelola oleh komponen induk (misalnya, `App.tsx` atau `Dashboard.tsx` jika ikon obrolan ada di sana dan mengelola state ini).
*   **State**:
    *   `messages`: Array untuk menyimpan riwayat percakapan. Setiap pesan memiliki `id`, `sender`, `text`, dan `timestamp`. Properti `isStreaming` ditambahkan untuk memberikan umpan balik visual saat AI sedang mengetik/mengalirkan respons.
    *   `inputValue`: Untuk input teks pengguna.
    *   `isLoading`: Untuk menunjukkan status pemuatan saat menunggu respons dari backend.
*   **`handleSendMessage`**:
    *   Mengirim pesan pengguna ke array `messages`.
    *   Membuat permintaan POST ke `/api/chat` (pastikan URL ini benar dan sesuai dengan konfigurasi `REACT_APP_API_BASE_URL` jika digunakan).
    *   **Streaming**: Menggunakan `ReadableStream` (`response.body?.getReader()`) untuk membaca respons yang dialirkan dari backend. Setiap potongan (chunk) yang diterima ditambahkan ke teks pesan AI terakhir dalam state `messages`.
    *   Indikator "mengetik" sederhana (`animate-pulse`) ditambahkan saat `isStreaming` true.
*   **Auto-scroll**: `messagesEndRef` dan `scrollToBottom` digunakan untuk secara otomatis menggulir ke pesan terbaru.
*   **Fokus Input**: `inputRef` digunakan untuk secara otomatis memfokuskan bidang input saat widget terbuka atau setelah pesan dikirim.
*   **Styling**: Kelas Tailwind CSS digunakan untuk membuat antarmuka widget obrolan.
*   **Pesan Sambutan**: Pesan sambutan otomatis ditambahkan saat widget pertama kali dibuka dan belum ada riwayat obrolan.
*   **Penanganan Error**: Penanganan error dasar disertakan untuk permintaan fetch. Jika terjadi error, pesan error akan ditampilkan di widget obrolan.

Komponen ini sekarang menyediakan fungsionalitas inti untuk widget obrolan interaktif dengan kemampuan streaming. Integrasi dengan `Dashboard.tsx` (untuk memicu buka/tutup) dan `App.tsx` (untuk manajemen state global jika diperlukan) akan menjadi langkah berikutnya dalam pengembangan aplikasi penuh.
