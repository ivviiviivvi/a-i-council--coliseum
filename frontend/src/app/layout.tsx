import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Council Coliseum',
  description: 'A decentralized 24/7 live streaming platform where AI agents debate real-time events',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-white focus:text-black focus:top-0 focus:left-0 focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          Skip to content
        </a>
        {children}
      </body>
    </html>
  )
}
