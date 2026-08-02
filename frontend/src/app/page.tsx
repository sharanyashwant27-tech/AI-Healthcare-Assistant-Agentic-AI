import Link from "next/link";

export default function HomePage() {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-[var(--line)]">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage:
            "linear-gradient(120deg, rgba(11,31,42,0.78), rgba(15,110,122,0.45)), url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1800&q=80')",
        }}
      />
      <div className="relative grid min-h-[78vh] content-end gap-6 px-6 py-12 md:px-12 md:py-16">
        <p className="animate-rise brand-mark font-display text-5xl font-semibold text-white md:text-7xl">
          AI Healthcare Assistant
        </p>
        <p className="animate-rise max-w-2xl text-lg text-white/85 md:text-xl" style={{ animationDelay: "120ms" }}>
          Agentic guidance for symptoms, knowledge, appointments, and care workflows —
          always with uncertainty and clinician oversight.
        </p>
        <div className="animate-rise flex flex-wrap gap-3" style={{ animationDelay: "220ms" }}>
          <Link
            href="/login"
            className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-ink shadow-soft transition hover:-translate-y-0.5"
          >
            Sign in
          </Link>
          <Link
            href="/register"
            className="rounded-full border border-white/40 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            Create account
          </Link>
        </div>
        <p className="animate-pulseSoft text-sm text-white/70">
          Not a diagnosis. For emergencies, call local emergency services.
        </p>
      </div>
    </section>
  );
}
