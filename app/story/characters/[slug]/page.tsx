import { notFound } from "next/navigation";
import { characters } from "@/data/characters";

interface PageProps {
  params: {
    slug: string;
  };
}

export default function CharacterPage({ params }: PageProps) {
  const character = characters.find(
    (item) => item.slug === params.slug
  );

  if (!character) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-black text-white">
      {/* Hero */}
      <section className="relative overflow-hidden py-28 text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-violet-700/20 to-black" />

        <div className="relative z-10 mx-auto max-w-5xl px-6">
          <span className="rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-2 text-sm text-violet-300">
            {character.status}
          </span>

          <h1 className="mt-8 text-6xl font-black">
            {character.name}
          </h1>

          <p className="mt-4 text-xl text-violet-400">
            {character.role}
          </p>

          <p className="mx-auto mt-8 max-w-3xl text-lg text-gray-400">
            {character.description}
          </p>
        </div>
      </section>

      {/* Placeholder */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="rounded-3xl border border-white/10 bg-zinc-900 p-10">
          <h2 className="text-3xl font-bold">
            Character Biography
          </h2>

          <p className="mt-6 text-gray-400">
            More official Rockstar information about{" "}
            <span className="font-semibold text-white">
              {character.name}
            </span>{" "}
            will be added here.
          </p>
        </div>
      </section>
    </main>
  );
}