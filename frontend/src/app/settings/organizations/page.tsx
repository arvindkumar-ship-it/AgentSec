"use client";
import { useEffect, useState } from "react";
import RouteGuard from "@/components/RouteGuard";
import Navbar from "@/components/Navbar";
import { agentSecAPI } from "@/lib/api";

export default function OrgsPage() {
  const [orgs, setOrgs] = useState<any[]>([]);

  const load = () => agentSecAPI.listOrganizations().then((r) => setOrgs(r.data.organizations));
  useEffect(() => { load(); }, []);

  const act = async (fn: (id: string) => any, id: string) => {
    await fn(id);
    load();
  };

  return (
    <RouteGuard adminOnly>
      <Navbar />
      <div className="p-6 max-w-6xl mx-auto text-gray-900">
        <h1 className="text-2xl font-bold mb-4">Organizations</h1>
        <div className="bg-panel border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-muted border-b border-border">
              <th className="p-3">Name</th><th className="p-3">State</th><th className="p-3">Scans/Limit</th><th className="p-3">Actions</th>
            </tr></thead>
            <tbody>
              {orgs.map((o) => (
                <tr key={o.org_id} className="border-t border-border">
                  <td className="p-3">{o.name}</td>
                  <td className="p-3 capitalize">{o.state}</td>
                  <td className="p-3">{o.scans_today}/{o.max_scans_per_day ?? "∞"}</td>
                  <td className="p-3 space-x-3">
                    <button onClick={() => act(agentSecAPI.suspendOrg, o.org_id)} className="text-danger">Suspend</button>
                    <button onClick={() => act(agentSecAPI.reactivateOrg, o.org_id)} className="text-safe">Reactivate</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </RouteGuard>
  );
}