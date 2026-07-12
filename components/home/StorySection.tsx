import Link from "next/link";
import { storySections } from "@/data/story";

export default function StorySection() {
  return (
    <section
      id="story"
      className="relative bg-gradient-to-b from-black via-zinc-950 to-black px-6 py-24"
    >
      <div className="mx-auto max-w-7xl">
        <div className="mb-16 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-violet-400">
            Story Hub
          </p>

          <h2 className="mt-4 text-4xl font-black text-white md:text-5xl">
            Explore GTA VI
          </h2>

          <p className="mx-auto mt-5 max-w-3xl text-lg text-zinc-400">
            Every page is built using official Rockstar information, trailers,
            screenshots and verified details.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
          {storySections.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.title}
                href={item.href}
                className="group relative overflow-hidden rounded-3xl border border-white/10 bg-zinc-900/70 p-8 backdrop-blur-sm transition-all duration-300 hover:-translate-y-2 hover:border-violet-500 hover:shadow-[0_0_40px_rgba(139,92,246,0.25)]"
              >
                {/* Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-violet-500/0 via-transparent to-pink-500/0 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

                {/* Icon */}
                <div className="relative mb-6 inline-flex rounded-2xl bg-violet-500/10 p-4">
                  <Icon className="h-8 w-8 text-violet-400 transition-transform duration-300 group-hover:scale-110" />
                </div>

                {/* Title */}
                <h3 className="relative text-2xl font-bold text-white">
                  {item.title}
                </h3>

                {/* Description */}
                <p className="relative mt-4 leading-7 text-zinc-400">
                  {item.description}
                </p>

                {/* CTA */}
                <div className="relative mt-8 inline-flex items-center gap-2 font-semibold text-violet-400 transition-all duration-300 group-hover:gap-3">
                  Explore
                  <span>→</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}