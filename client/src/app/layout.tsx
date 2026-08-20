import type { Metadata } from 'next';
import { Inter, Geist_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  display: 'swap',
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Privacy-First Chatbot — Secure Local AI',
  description:
    'A privacy-first AI chatbot that runs entirely on your machine. Upload documents and chat with your data — no data ever leaves your device.',
  keywords: ['privacy', 'chatbot', 'RAG', 'AI', 'local', 'Ollama', 'secure'],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${geistMono.variable} dark h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-surface-base text-text-primary">
        {children}
      </body>
    </html>
  );
}
