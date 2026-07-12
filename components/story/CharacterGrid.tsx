import Link from "next/link";
import Image from "next/image";
import { characters } from "@/data/characters";

export default function CharacterGrid() {
  return (
    <section className="bg-black px-6 pb-24">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {characters.map((character) => (
            <article
              key={character.id}
              className="group overflow-hidden rounded-3xl border border-white/10 bg-zinc-900 transition-all duration-300 hover:-translate-y-2 hover:border-violet-500 hover:shadow-[0_0_35px_rgba(139,92,246,.25)]"
            >
              {/* Character Image */}
              <div className="relative h-64 overflow-hidden">
                <Image
                  src={character.image}
                  alt={character.name}
                  fill
                  className="object-cover transition duration-500 group-hover:scale-105"
                />
              </div>

              {/* Content */}
              <div className="p-7">
                <span className="inline-block rounded-full bg-violet-600/20 px-3 py-1 text-sm font-medium text-violet-300">
                  {character.status}
                </span>

                <h2 className="mt-5 text-3xl font-black text-white">
                  {character.name}
                </h2>

                <p className="mt-2 font-medium text-violet-400">
                  {character.role}
                </p>

                <p className="mt-5 leading-7 text-gray-400">
                  {character.description}
                </p>

                <Link
                  href={`/story/characters/${character.slug}`}
                  className="mt-8 inline-flex items-center font-semibold text-violet-400 transition-transform duration-300 group-hover:translate-x-1"
                >
                  View Character →
                </Link>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}