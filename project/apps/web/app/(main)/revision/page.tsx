"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchDueRevisions, fetchStrengthsWeaknesses } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";

export default function RevisionPage() {
  const {
    data: due,
    isLoading: dueLoading,
    error: dueError,
    refetch: refetchDue,
  } = useQuery({
    queryKey: ["revision-due"],
    queryFn: fetchDueRevisions,
  });

  const {
    data: masteryStats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ["strengths-weaknesses"],
    queryFn: fetchStrengthsWeaknesses,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Revision Dashboard</h1>
        <p className="text-slate-600 dark:text-slate-400">Keep concepts fresh with spaced repetition.</p>
      </div>

      {(dueError || statsError) && (
        <ErrorMessage>
          Failed to load revision data.{" "}
          <Button onClick={() => { refetchDue(); refetchStats(); }} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Due Today</h2>
          {dueLoading ? (
            <RevisionSkeleton count={3} />
          ) : due && due.length > 0 ? (
            <ul className="mt-4 space-y-3">
              {due.map((item) => (
                <li
                  key={item.concept_id}
                  className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800"
                >
                  <span className="font-medium text-slate-900 dark:text-white">{item.concept_id}</span>
                  <Link
                    href={`/revision/active?concept=${item.concept_id}`}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                  >
                    Review
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-slate-600 dark:text-slate-400">No concepts due today. Great job!</p>
          )}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Weak Concepts</h2>
          {statsLoading ? (
            <RevisionSkeleton count={3} />
          ) : masteryStats?.weaknesses.length ? (
            <ul className="mt-4 space-y-3">
              {masteryStats.weaknesses.slice(0, 5).map((item) => (
                <li
                  key={item.concept_id}
                  className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-900 dark:text-white">{item.concept_id}</span>
                    <span className="text-sm text-red-600 dark:text-red-400">{item.score}%</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-slate-600 dark:text-slate-400">No weak concepts. Keep it up!</p>
          )}
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Active Recall</h2>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Start a focused revision session to test your knowledge.
        </p>
        <Link
          href="/revision/active"
          className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Start Session
        </Link>
      </section>
    </div>
  );
}

function RevisionSkeleton({ count }: { count: number }) {
  return (
    <div className="mt-4 space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-16 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
      ))}
    </div>
  );
}
