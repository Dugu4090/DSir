"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchMastery, fetchStrengthsWeaknesses } from "@/lib/api";
import { useAuthStore } from "@/hooks/use-auth";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";

export default function ProfilePage() {
  const { user } = useAuthStore();
  const {
    data: mastery,
    isLoading: masteryLoading,
    error: masteryError,
    refetch: refetchMastery,
  } = useQuery({
    queryKey: ["mastery"],
    queryFn: fetchMastery,
  });

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ["strengths-weaknesses"],
    queryFn: fetchStrengthsWeaknesses,
  });

  const avgScore =
    mastery?.items && mastery.items.length > 0
      ? Math.round(mastery.items.reduce((acc, m) => acc + m.score, 0) / mastery.items.length)
      : 0;

  if (masteryError || statsError) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Profile</h1>
        <p className="text-slate-600 dark:text-slate-400">Manage your account and view progress.</p>
        <ErrorMessage>
          Failed to load profile data.{" "}
          <Button onClick={() => { refetchMastery(); refetchStats(); }} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      </div>
    );
  }

  if (masteryLoading || statsLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Profile</h1>
        <p className="text-slate-600 dark:text-slate-400">Manage your account and view progress.</p>
        <div className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Profile</h1>
        <p className="text-slate-600 dark:text-slate-400">Manage your account and view progress.</p>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Account</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Name</label>
            <p className="text-slate-900 dark:text-white">{user?.full_name ?? "-"}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-500 dark:text-slate-400">Email</label>
            <p className="text-slate-900 dark:text-white">{user?.email}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Average Mastery</p>
          <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{avgScore}%</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Strengths</p>
          <p className="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">
            {stats?.strengths.length ?? 0}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Weaknesses</p>
          <p className="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
            {stats?.weaknesses.length ?? 0}
          </p>
        </div>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Learning History</h2>
        {mastery?.items.length ? (
          <ul className="mt-4 space-y-2">
            {mastery.items.slice(0, 10).map((item) => (
              <li
                key={item.concept_id}
                className="flex items-center justify-between rounded-lg border border-slate-200 p-3 dark:border-slate-700"
              >
                <span className="font-medium text-slate-900 dark:text-white">{item.concept_id}</span>
                <span className="text-sm text-slate-600 dark:text-slate-400">{item.score}% mastery</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-slate-600 dark:text-slate-400">No learning history yet.</p>
        )}
      </section>
    </div>
  );
}
