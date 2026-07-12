import Link from "next/link";

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-white/10 bg-black">
      <div className="mx-auto flex max-w-7xl flex-col gap-10 px-6 py-16 lg:flex-row lg:justify-between">
        {/* Logo */}
        <div>
          <h2 className="text-3xl font-black text-white">
            VICE<span className="text-violet-500">BASE</span>
          </h2>

          <p className="mt-4 max-w-md text-gray-400">
            Your community hub for GTA VI news, characters, trailers,
            screenshots and creator content.
          </p>
        </div>

        {/* Explore */}
        <div>
          <h3 className="mb-4 text-lg font-bold text-white">
            Explore
          </h3>

          <div className="space-y-2">
            <Link
              href="/story/characters"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              Characters
            </Link>

            <Link
              href="/story/map"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              Map
            </Link>

            <Link
              href="/story/vehicles"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              Vehicles
            </Link>

            <Link
              href="/story/trailers"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              Trailers
            </Link>
          </div>
        </div>

        {/* Community */}
        <div>
          <h3 className="mb-4 text-lg font-bold text-white">
            Community
          </h3>

          <div className="space-y-2">
            <a
              href="#"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              YouTube
            </a>

            <a
              href="#"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              Discord
            </a>

            <a
              href="#"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              TikTok
            </a>

            <a
              href="#"
              className="block text-gray-400 transition hover:text-violet-400"
            >
              Instagram
            </a>
          </div>
        </div>
      </div>

      <div className="border-t border-white/10 px-6 py-6 text-center text-sm text-gray-500">
        <p>© 2026 ViceBase. All rights reserved.</p>

        <p className="mt-2">
          ViceBase is an independent fan project and is not affiliated with,
          endorsed by, or sponsored by Rockstar Games or Take-Two Interactive.
        </p>
      </div>
    </footer>
  );
}