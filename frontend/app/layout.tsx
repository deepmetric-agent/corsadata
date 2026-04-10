import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Director Hub PRO",
  description: "Plataforma SaaS para directores deportivos de ciclismo",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
