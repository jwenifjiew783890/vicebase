import Link from "next/link";
import { creators } from "@/data/creators";

export default function FeaturedCreators() {
  const featuredCreators = creators.filter(
    (creator) => creator.featured
  );

  return (
    <section className="bg-black px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <div className="mb-12 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-violet-400">
            Featured Creators
          </p>

          <h2 className="mt-3 text-5xl font-black text-white">
            Discover GTA VI Creators
          </h2>

          <p className="mx-auto mt-4 max-w-3xl text-gray-400">
            Follow talented creators producing GTA VI news, gameplay,
            guides and community content.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {featuredCreators.map((creator) => (
            <div
              key={creator.id}
              className="rounded-3xl border border-white/10 bg-zinc-900 p-8 transition-all duration-300 hover:-translate-y-2 hover:border-violet-500 hover:shadow-[0_0_40px_rgba(139,92,246,.25)]"
            >
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-zinc-800 text-4xl">
                👤
              </div>

              <h3 className="mt-6 text-2xl font-bold text-white">
                {creator.name}
              </h3>

              <p className="mt-1 text-violet-400">
                {creator.role}
              </p>

              <p className="mt-4 text-gray-400">
                {creator.description}
              </p>

              <div className="mt-8 flex gap-4 text-2xl">
                <a href={creator.youtube}>▶️</a>
                <a href={creator.tiktok}>🎵</a>
                <a href={creator.discord}>💬</a>
                <a href={creator.instagram}>📷</a>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Link
            href="/creators"
            className="rounded-full bg-violet-600 px-8 py-4 font-semibold text-white transition hover:bg-violet-500"
          >
            View All Creators
          </Link>
        </div>
      </div>
    </section>
  );
}