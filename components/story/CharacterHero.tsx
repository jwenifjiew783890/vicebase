export default function CharacterHero() {
  return (
    <section className="relative overflow-hidden bg-black py-32">
      {/* Background */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url('/images/characters/hero.jpg')",
        }}
      />

      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black/75" />

      {/* Purple Glow */}
      <div className="absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-600/20 blur-3xl" />

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
        <span className="inline-flex rounded-full border border-violet-500/30 bg-violet-500/10 px-5 py-2 text-sm font-semibold uppercase tracking-[0.2em] text-violet-300">
          Official Rockstar Information
        </span>

        <h1 className="mt-8 text-5xl font-black text-white md:text-7xl">
          GTA VI Characters
        </h1>

        <p className="mx-auto mt-8 max-w-3xl text-lg leading-8 text-zinc-300">
          Meet every officially revealed protagonist and confirmed story
          character from Grand Theft Auto VI, based on Rockstar Games'
          trailers, screenshots and official Newswire posts.
        </p>
      </div>
    </section>
  );
}