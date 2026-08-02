export default function Loading() {
  return (
    <div className="mx-auto max-w-7xl animate-pulse space-y-4 px-4 py-10 md:px-8">
      <div className="h-10 w-1/3 rounded-2xl bg-white/50 dark:bg-white/10" />
      <div className="h-4 w-2/3 rounded-xl bg-white/40 dark:bg-white/5" />
      <div className="grid gap-4 md:grid-cols-3">
        <div className="h-28 rounded-3xl bg-white/50 dark:bg-white/10" />
        <div className="h-28 rounded-3xl bg-white/50 dark:bg-white/10" />
        <div className="h-28 rounded-3xl bg-white/50 dark:bg-white/10" />
      </div>
    </div>
  );
}
