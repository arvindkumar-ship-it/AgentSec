"use client";
import { useEffect, useState } from "react";
import RouteGuard from "@/components/RouteGuard";
import Navbar from "@/components/Navbar";
import { agentSecAPI } from "@/lib/api";

const ALL_MODELS = ["groq", "gemini", "openai", "anthropic"];

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<any>({});
  const [thresholds, setThresholds] = useState<any>(null);

  const load = () => agentSecAPI.getPolicies().then((r) => {
    setPolicies(r.data);
    setThresholds(r.data.risk_thresholds?.value ?? null);
  });
  useEffect(() => { load(); }, []);

  const update = async (key: string, value: any) => {
    await agentSecAPI.updatePolicy(key, value);
    load();
  };

  const toggleModel = (model: string) => {
    const current: string[] = policies.allowed_models?.value ?? [];
    const next = current.includes(model) ? current.filter((m) => m !== model) : [...current, model];
    update("allowed_models", next);
  };

  return (
    <RouteGuard adminOnly>
      <Navbar />
      <div className="p-6 max-w-2xl mx-auto text-gray-900 space-y-6">
        <h1 className="text-2xl font-bold">Policy Settings</h1>

        {policies.prompt_injection_strictness && (
          <div className="bg-panel border border-border rounded-2xl p-4">
            <label className="block text-sm text-muted mb-2">Prompt Injection Strictness</label>
            <select
              value={policies.prompt_injection_strictness.value}
              onChange={(e) => update("prompt_injection_strictness", e.target.value)}
              className="bg-surface border border-border p-2 rounded-lg"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        )}

        {thresholds && (
          <div className="bg-panel border border-border rounded-2xl p-4 space-y-3">
            <label className="block text-sm text-muted">Risk Thresholds</label>
            {(["critical", "high", "medium", "low"] as const).map((level) => (
              <div key={level} className="flex items-center justify-between gap-3">
                <span className="capitalize text-sm">{level}</span>
                <input
                  type="number"
                  value={thresholds[level]}
                  onChange={(e) => setThresholds({ ...thresholds, [level]: Number(e.target.value) })}
                  onBlur={() => update("risk_thresholds", thresholds)}
                  className="w-24 bg-surface border border-border p-1 rounded-lg text-right"
                />
              </div>
            ))}
          </div>
        )}

        {policies.allowed_models && (
          <div className="bg-panel border border-border rounded-2xl p-4">
            <label className="block text-sm text-muted mb-2">Allowed Models</label>
            <div className="flex flex-wrap gap-2">
              {ALL_MODELS.map((m) => {
                const active = policies.allowed_models.value.includes(m);
                return (
                  <button
                    key={m}
                    onClick={() => toggleModel(m)}
                    className={`px-3 py-1 rounded-full text-sm border ${active ? "bg-accent text-white border-accent" : "border-border text-muted"}`}
                  >
                    {m}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </RouteGuard>
  );
}