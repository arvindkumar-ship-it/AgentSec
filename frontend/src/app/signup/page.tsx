"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { agentSecAPI } from "@/lib/api";
import { authStorage } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", name: "", org_name: "" });
  const [error, setError] = useState("");

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await agentSecAPI.register(form);
      authStorage.setToken(res.data.access_token);
      const me = await agentSecAPI.me();
      authStorage.setRole(me.data.role);
      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSignup} className="w-full max-w-sm space-y-4 p-8 bg-panel border border-border rounded-2xl">
        <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
        {error && <p className="text-danger text-sm">{error}</p>}
        <input placeholder="Your Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="w-full p-2 bg-surface border border-border rounded-lg text-gray-900 placeholder:text-subtle focus:outline-none focus:border-accent" required />
        <input placeholder="Organization Name" value={form.org_name} onChange={(e) => setForm({ ...form, org_name: e.target.value })}
          className="w-full p-2 bg-surface border border-border rounded-lg text-gray-900 placeholder:text-subtle focus:outline-none focus:border-accent" required />
        <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="w-full p-2 bg-surface border border-border rounded-lg text-gray-900 placeholder:text-subtle focus:outline-none focus:border-accent" required />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
          className="w-full p-2 bg-surface border border-border rounded-lg text-gray-900 placeholder:text-subtle focus:outline-none focus:border-accent" required />
        <button type="submit" className="w-full p-2 bg-accent text-white rounded-full hover:opacity-90">Sign Up</button>
      </form>
    </div>
  );
}