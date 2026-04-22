import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Yudis-bit | The DeFi Security Vault',
  description: 'Uncovering vulnerabilities to build a more resilient Web3.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}