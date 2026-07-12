export default function Hero() {
  return (
    <section className="relative flex min-h-screen items-center justify-center overflow-hidden bg-black">
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center scale-105"
        style={{
          backgroundImage: "url('/images/hero/hero-bg.jpg')",
        }}
      />

      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black/70" />

      {/* Purple Glow */}
      <div className="absolute left-1/2 top-1/2 h-[700px] w-[700px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-600/20 blur-3xl" />

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
        <p className="mb-5 text-sm font-semibold uppercase tracking-[0.4em] text-violet-400">
          Welcome to ViceBase
        </p>

        <h1 className="text-5xl font-black leading-tight text-white md:text-7xl">
          The Ultimate
          <span className="block bg-gradient-to-r from-violet-400 to-pink-500 bg-clip-text text-transparent">
            GTA VI Companion
          </span>
        </h1>

        <p className="mx-auto mt-8 max-w-3xl text-lg leading-8 text-zinc-300">
          Official GTA VI news, verified story information, trailers,
          screenshots, guides and everything you need before and after launch.
        </p>

        <div className="mt-12 flex flex-wrap justify-center gap-5">
          <button className="rounded-full bg-violet-600 px-8 py-4 font-semibold text-white transition duration-300 hover:scale-105 hover:bg-violet-500">
            Explore Story
          </button>

          <button className="rounded-full border border-white/20 bg-white/5 px-8 py-4 font-semibold text-white backdrop-blur-md transition duration-300 hover:border-violet-500">
            Latest News
          </button>
        </div>

        <div className="mt-20 animate-bounce text-zinc-400">
          ↓ Scroll
        </div>
      </div>
    </section>
  );
}