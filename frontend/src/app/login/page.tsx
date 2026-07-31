"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { agentSecAPI } from "@/lib/api";
import { authStorage } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await agentSecAPI.login({ email, password });
      authStorage.setToken(res.data.access_token);
      const me = await agentSecAPI.me();
      authStorage.setRole(me.data.role);
      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleLogin} className="w-full max-w-sm space-y-4 p-8 bg-panel border border-border rounded-2xl">
        <h1 className="text-2xl font-bold text-gray-900">AgentSec Login</h1>
        {error && <p className="text-danger text-sm">{error}</p>}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 bg-surface border border-border rounded-lg text-gray-900 placeholder:text-subtle focus:outline-none focus:border-accent" required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 bg-surface border border-border rounded-lg text-gray-900 placeholder:text-subtle focus:outline-none focus:border-accent" required />
        <button type="submit" className="w-full p-2 bg-accent text-white rounded-full hover:opacity-90">Login</button>
        <p className="text-sm text-muted">No account? <a href="/signup" className="text-accent">Sign up</a></p>
      </form>
    </div>
  );
}