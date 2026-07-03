import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentSec — AI Agent Security Platform",
  description: "Scan, Shield, and Eval your AI agents",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
