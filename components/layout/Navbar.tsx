"use client";

import Link from "next/link";

const navItems = [
  { name: "News", href: "#" },
  { name: "Businesses", href: "#" },
  { name: "Heists", href: "#" },
  { name: "Vehicles", href: "#" },
  { name: "Money Hub", href: "#" },
];

export default function Navbar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/30 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
        <Link href="/" className="text-2xl font-black tracking-wider">
          <span className="text-white">VICE</span>
          <span className="text-violet-500">BASE</span>
        </Link>

        <nav className="hidden gap-8 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="text-gray-300 transition hover:text-violet-400"
            >
              {item.name}
            </Link>
          ))}
        </nav>

        <button className="rounded-full bg-violet-600 px-5 py-2 font-semibold text-white transition hover:bg-violet-500">
          Join Discord
        </button>
      </div>
    </header>
  );
}