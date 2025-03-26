import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from './components/Header';
import Footer from './components/Footer';
import { AuthProvider } from '@/contexts/AuthContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GenZen - Mental Health Chatbot',
  description: 'Your AI-powered mental health companion',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className}`}>
        <AuthProvider>
          <div className="flex flex-col min-h-screen">
            {/* Header */}
            <Header />

            {/* Main Content with gradient background */}
            <main className="flex-grow bg-gradient-to-b from-purple-300 via-pink-300 to-red-200">
              <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 max-w-4xl">
                {children}
              </div>
            </main>

            {/* Footer */}
            <Footer />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
