import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-5xl font-bold tracking-tight text-slate-900">
        Welcome to DSir
      </h1>
      <p className="mt-4 text-lg text-slate-600">
        Master programming with an AI-powered, personalized learning path.
      </p>
      <div className="mt-8 flex gap-4">
        <Link
          href="/courses"
          className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
        >
          Browse Courses
        </Link>
        <Link
          href="/roadmaps"
          className="rounded-lg border border-slate-300 px-6 py-3 font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          Explore Roadmaps
        </Link>
      </div>
    </main>
  );
}
