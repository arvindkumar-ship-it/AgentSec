"use client";
import { useEffect, useState } from "react";
import RouteGuard from "@/components/RouteGuard";
import Navbar from "@/components/Navbar";
import { agentSecAPI } from "@/lib/api";

const PROVIDERS = ["google", "microsoft", "okta"];

export default function SSOPage() {
  const [configured, setConfigured] = useState(false);
  const [form, setForm] = useState({
    provider: "google",
    client_id: "",
    client_secret: "",
    redirect_uri: "",
    issuer: "",
    sso_only: false,
  });
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    agentSecAPI.getSSOConfig()
      .then((r) => {
        setConfigured(!!r.data?.configured);
        if (r.data?.provider) {
          setForm((f) => ({ ...f, provider: r.data.provider, redirect_uri: r.data.redirect_uri || "", issuer: r.data.issuer || "", sso_only: r.data.sso_only || false }));
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("");
    try {
      await agentSecAPI.setSSOConfig(form);
      setMsg("SSO config saved.");
      setConfigured(true);
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Failed to save.");
    }
  };

  if (loading) return null;

  return (
    <RouteGuard adminOnly>
      <Navbar />
      <div className="p-6 max-w-2xl mx-auto text-gray-900">
        <h1 className="text-2xl font-bold mb-2">SSO Configuration</h1>
        <p className="text-xs text-subtle mb-4">
          Storage only — no real "Sign in with SSO" login flow exists yet. This just saves provider config for future OAuth wiring.
        </p>

        {configured && <p className="text-sm text-safe mb-4">SSO is currently configured for your organization.</p>}
        {msg && <p className="text-sm text-muted mb-4">{msg}</p>}

        <form onSubmit={save} className="bg-panel border border-border rounded-2xl p-5 space-y-4">
          <div>
            <label className="block text-sm text-muted mb-1">Provider</label>
            <select
              value={form.provider}
              onChange={(e) => setForm({ ...form, provider: e.target.value })}
              className="w-full bg-surface border border-border p-2 rounded-lg"
            >
              {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm text-muted mb-1">Client ID</label>
            <input
              value={form.client_id}
              onChange={(e) => setForm({ ...form, client_id: e.target.value })}
              className="w-full bg-surface border border-border p-2 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-muted mb-1">Client Secret</label>
            <input
              type="password"
              value={form.client_secret}
              onChange={(e) => setForm({ ...form, client_secret: e.target.value })}
              className="w-full bg-surface border border-border p-2 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-muted mb-1">Redirect URI</label>
            <input
              value={form.redirect_uri}
              onChange={(e) => setForm({ ...form, redirect_uri: e.target.value })}
              placeholder="https://yourapp.com/auth/sso/callback"
              className="w-full bg-surface border border-border p-2 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-muted mb-1">Issuer</label>
            <input
              value={form.issuer}
              onChange={(e) => setForm({ ...form, issuer: e.target.value })}
              className="w-full bg-surface border border-border p-2 rounded-lg"
            />
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.sso_only}
              onChange={(e) => setForm({ ...form, sso_only: e.target.checked })}
            />
            SSO only (disable password login for this org)
          </label>

          <button type="submit" className="bg-accent text-white px-5 py-2 rounded-full text-sm">
            Save Config
          </button>
        </form>
      </div>
    </RouteGuard>
  );
}