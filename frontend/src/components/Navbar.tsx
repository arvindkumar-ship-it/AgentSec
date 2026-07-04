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





import { ShieldCheck } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

export default function Navbar() {
  const pathname = usePathname()

  const links = [
    { href: "/", label: "Dashboard" },
    { href: "/scan", label: "Scan" },
    { href: "/shield", label: "Shield" },
    { href: "/eval", label: "Eval" },
  ]

  return (
    <div className="w-full flex justify-center pt-4">
      <nav className="flex items-center justify-between w-[95%] max-w-6xl rounded-full bg-panel border border-border px-6 py-3">
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
        </div>

        <Link href="/scan">
          <button className="bg-accent text-white text-sm font-medium px-5 py-2 rounded-full hover:opacity-90">
            Run Scan
          </button>
        </Link>
      </nav>
    </div>
  )
}