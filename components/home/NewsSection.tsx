import Link from "next/link";
import { news } from "@/data/news";

export default function NewsSection() {
  return (
    <section className="bg-black px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <div className="mb-12 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-violet-400">
            Latest News
          </p>

          <h2 className="mt-3 text-5xl font-black text-white">
            Official Rockstar Updates
          </h2>

          <p className="mx-auto mt-4 max-w-3xl text-gray-400">
            Every trailer, Newswire article and official announcement from
            Rockstar Games.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {news.map((item) => (
            <article
              key={item.id}
              className="overflow-hidden rounded-3xl border border-white/10 bg-zinc-900 transition duration-300 hover:border-violet-500 hover:shadow-[0_0_35px_rgba(139,92,246,.25)]"
            >
              <div className="flex h-56 items-center justify-center bg-zinc-800 text-gray-500">
                Image Coming Soon
              </div>

              <div className="p-7">
                <p className="text-sm text-violet-400">
                  {item.date}
                </p>

                <h3 className="mt-3 text-2xl font-bold text-white">
                  {item.title}
                </h3>

                <p className="mt-4 text-gray-400">
                  {item.description}
                </p>

                <Link
                  href="#"
                  className="mt-6 inline-block font-semibold text-violet-400"
                >
                  Read More →
                </Link>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}