"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authStorage } from "@/lib/auth";

export default function RouteGuard({
  children,
  adminOnly = false,
}: {
  children: React.ReactNode;
  adminOnly?: boolean;
}) {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!authStorage.isLoggedIn()) {
      router.push("/login");
      return;
    }
    if (adminOnly && !authStorage.isAdmin()) {
      router.push("/");
      return;
    }
    setChecked(true);
  }, [router, adminOnly]);

  if (!checked) return null;
  return <>{children}</>;
}