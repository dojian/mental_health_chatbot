import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from './components/Header';
import Footer from './components/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GenZen - AI Mental Health Support',
  description: '24/7 AI-powered mental health assistance',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          {/* Header */}
          <Header />

          {/* Main Content */}
          <main className="flex-grow container mx-auto px-4 py-8">{children}</main>

          {/* Footer */}
          <Footer />
        </div>
      </body>
    </html>
  );
}
