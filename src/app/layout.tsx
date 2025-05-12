// src/app/layout.tsx  (server component — no 'use client' here)
import './globals.css';
import { Inter } from 'next/font/google';
import Providers from './providers';
import ThemeToggle from '@/components/ThemeToggle';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'CheckMyMeds',
  description: 'A patient-first, AI-powered medication safety platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {/* UI that needs theming */}
          <ThemeToggle />
          {children}
        </Providers>
      </body>
    </html>
  );
}

