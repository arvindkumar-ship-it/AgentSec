// import { ShieldCheck } from "lucide-react"

// export default function Navbar() {
//   return (
//     <div className="w-full flex justify-center pt-4">
//       <nav className="flex items-center justify-between w-[95%] max-w-6xl rounded-full bg-panel border border-border px-6 py-3">
//         <div className="flex items-center gap-2">
//           <ShieldCheck className="w-5 h-5 text-accent" />
//           <span className="font-bold text-white">AgentSec</span>
//           <span className="text-xs text-gray-500 bg-surface px-2 py-0.5 rounded-full">v1.0</span>
//         </div>

//         <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
//           <a href="#" className="text-white font-medium">Dashboard</a>
//           <a href="#" className="hover:text-white">Scan</a>
//           <a href="#" className="hover:text-white">Shield</a>
//           <a href="#" className="hover:text-white">Eval</a>
//         </div>

//         <button className="bg-accent text-white text-sm font-medium px-5 py-2 rounded-full hover:opacity-90">
//           Run Scan
//         </button>
//       </nav>
//     </div>
//   )
// }





// import { ShieldCheck } from "lucide-react"
// import Link from "next/link"
// import { usePathname } from "next/navigation"

// export default function Navbar() {
//   const pathname = usePathname()

//   const links = [
//     { href: "/", label: "Dashboard" },
//     { href: "/scan", label: "Scan" },
//     { href: "/shield", label: "Shield" },
//     { href: "/eval", label: "Eval" },
//   ]

//   return (
//     <div className="w-full flex justify-center pt-4">
//       <nav className="flex items-center justify-between w-[95%] max-w-6xl rounded-full bg-panel border border-border px-6 py-3">
//         <div className="flex items-center gap-2">
//           <ShieldCheck className="w-5 h-5 text-accent" />
//           <span className="font-bold text-gray-900">AgentSec</span>
//           <span className="text-xs text-gray-500 bg-surface px-2 py-0.5 rounded-full">v1.0</span>
//         </div>

//         <div className="hidden md:flex items-center gap-8 text-sm text-gray-500">
//           {links.map(({ href, label }) => (
//             <Link
//               key={href}
//               href={href}
//               className={pathname === href ? "text-gray-900 font-medium" : "hover:text-gray-900"}
//             >
//               {label}
//             </Link>
//           ))}
//         </div>

//         <Link href="/scan">
//           <button className="bg-accent text-white text-sm font-medium px-5 py-2 rounded-full hover:opacity-90">
//             Run Scan
//           </button>
//         </Link>
//       </nav>
//     </div>
//   )
// }




"use client";
import { useEffect, useRef, useState } from "react";
import { ShieldCheck, ChevronDown, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { authStorage } from "@/lib/auth";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isAdmin, setIsAdmin] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsAdmin(authStorage.isAdmin());
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setSettingsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const links = [
    { href: "/", label: "Dashboard" },
    { href: "/scan", label: "Scan" },
    { href: "/shield", label: "Shield" },
    { href: "/eval", label: "Eval" },
  ];

  const settingsLinks = [
    { href: "/settings/organizations", label: "Organizations" },
    { href: "/settings/audit", label: "Audit Logs" },
    { href: "/settings/policies", label: "Policies" },
    { href: "/settings/billing", label: "Billing" },
    { href: "/settings/sso", label: "SSO Config" },
  ];

  const logout = () => {
    authStorage.clearToken();
    router.push("/login");
  };

  return (
    <div className="w-full flex justify-center pt-4">
      <nav className="flex items-center justify-between w-[95%] max-w-6xl rounded-full bg-panel border border-border px-6 py-3 relative">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-accent" />
          <span className="font-bold text-gray-900">AgentSec</span>
          <span className="text-xs text-gray-500 bg-surface px-2 py-0.5 rounded-full">v1.0</span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-sm text-gray-500">
          {links.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={pathname === href ? "text-gray-900 font-medium" : "hover:text-gray-900"}
            >
              {label}
            </Link>
          ))}

          {isAdmin && (
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setSettingsOpen((v) => !v)}
                className={`flex items-center gap-1 ${
                  pathname.startsWith("/settings") ? "text-gray-900 font-medium" : "hover:text-gray-900"
                }`}
              >
                Admin <ChevronDown className="w-3.5 h-3.5" />
              </button>
              {settingsOpen && (
                <div className="absolute top-full mt-2 right-0 bg-panel border border-border rounded-xl shadow-lg py-2 w-44 z-10">
                  {settingsLinks.map(({ href, label }) => (
                    <Link
                      key={href}
                      href={href}
                      onClick={() => setSettingsOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-surface"
                    >
                      {label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Link href="/scan">
            <button className="bg-accent text-white text-sm font-medium px-5 py-2 rounded-full hover:opacity-90">
              Run Scan
            </button>
          </Link>
          <button onClick={logout} title="Logout" className="text-gray-500 hover:text-gray-900">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </nav>
    </div>
  );
}