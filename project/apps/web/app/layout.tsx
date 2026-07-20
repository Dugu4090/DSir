import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DSir - Learn to Code with AI",
  description: "An AI-powered programming education platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
