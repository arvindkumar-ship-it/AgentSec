"use client";
import { useEffect, useState } from "react";
import Script from "next/script";
import RouteGuard from "@/components/RouteGuard";
import Navbar from "@/components/Navbar";
import { agentSecAPI } from "@/lib/api";

const PLANS = ["free", "pro", "enterprise"];

export default function BillingPage() {
  const [currentPlan, setCurrentPlan] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);

  const loadPlan = () => agentSecAPI.me().then((r) => setCurrentPlan(r.data.plan_name));
  useEffect(() => { loadPlan(); }, []);

  const switchToFree = async () => {
    await agentSecAPI.changePlan("free");
    setMsg("Switched to free");
    loadPlan();
  };

  const payAndSwitch = async (plan: string) => {
    setLoadingPlan(plan);
    setMsg("");
    try {
      const res = await agentSecAPI.createOrder(plan);
      const { order_id, amount, currency, key_id } = res.data;

      const options = {
        key: key_id,
        amount,
        currency,
        name: "AgentSec",
        description: `Upgrade to ${plan} plan`,
        order_id,
        handler: async (response: any) => {
          try {
            await agentSecAPI.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              plan_name: plan,
            });
            setMsg(`Payment successful — switched to ${plan}`);
            loadPlan();
          } catch (err: any) {
            setMsg(err.response?.data?.detail || "Payment verification failed");
          }
        },
        modal: {
          ondismiss: () => setLoadingPlan(null),
        },
        theme: { color: "#6366f1" },
      };

      // @ts-ignore — Razorpay injected globally via script tag
      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || "Failed to start payment");
    } finally {
      setLoadingPlan(null);
    }
  };

  const switchPlan = (plan: string) => {
    if (plan === "free") return switchToFree();
    return payAndSwitch(plan);
  };

  return (
    <RouteGuard adminOnly>
      <Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="lazyOnload" />
      <Navbar />
      <div className="p-6 max-w-2xl mx-auto text-gray-900">
        <h1 className="text-2xl font-bold mb-2">Billing</h1>
        {currentPlan && (
          <p className="text-sm text-muted mb-4">
            Current plan: <span className="font-semibold text-gray-900 capitalize">{currentPlan}</span>
          </p>
        )}
        {msg && <p className="text-safe mb-2">{msg}</p>}
        <div className="flex gap-3">
          {PLANS.map((p) => (
            <button
              key={p}
              disabled={loadingPlan === p}
              onClick={() => switchPlan(p)}
              className={`px-5 py-3 rounded-xl capitalize border disabled:opacity-50 ${
                currentPlan === p ? "bg-accent text-white border-accent" : "bg-panel border-border hover:border-accent"
              }`}
            >
              {loadingPlan === p ? "Processing..." : p}
            </button>
          ))}
        </div>
        <p className="text-xs text-subtle mt-4">Pro/Enterprise open Razorpay checkout (test mode). Free switches instantly, no payment.</p>
      </div>
    </RouteGuard>
  );
}