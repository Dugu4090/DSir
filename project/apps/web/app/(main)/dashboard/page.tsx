"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  fetchCourses,
  fetchDueRevisions,
  fetchEnrollments,
  fetchMastery,
  fetchRoadmaps,
  fetchStrengthsWeaknesses,
} from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const {
    data: enrollments,
    isLoading: enrollmentsLoading,
    error: enrollmentsError,
  } = useQuery({
    queryKey: ["enrollments"],
    queryFn: fetchEnrollments,
  });

  const { data: roadmaps, isLoading: roadmapsLoading, error: roadmapsError } = useQuery({
    queryKey: ["roadmaps"],
    queryFn: fetchRoadmaps,
  });

  const { data: dueRevisions, isLoading: dueLoading, error: revisionsError } = useQuery({
    queryKey: ["revision-due"],
    queryFn: fetchDueRevisions,
  });

  const { data: masteryStats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ["strengths-weaknesses"],
    queryFn: fetchStrengthsWeaknesses,
  });

  const { data: mastery, isLoading: masteryLoading, error: masteryError } = useQuery({
    queryKey: ["mastery"],
    queryFn: fetchMastery,
  });

  const { data: courses, isLoading: coursesLoading, error: coursesError } = useQuery({
    queryKey: ["courses"],
    queryFn: () => fetchCourses(),
  });

  const isLoading =
    enrollmentsLoading || roadmapsLoading || dueLoading || statsLoading || masteryLoading || coursesLoading;

  const hasError =
    enrollmentsError || roadmapsError || revisionsError || statsError || masteryError || coursesError;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-1/3 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
          ))}
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
        <ErrorMessage>
          We couldn&apos;t load your dashboard. Please refresh the page or try again later.
        </ErrorMessage>
      </div>
    );
  }

  const currentRoadmap = roadmaps?.items[0];
  const dueCount = dueRevisions?.length ?? 0;
  const avgScore =
    mastery?.items && mastery.items.length > 0
      ? Math.round(
          mastery.items.reduce((acc, m) => acc + m.score, 0) / mastery.items.length
        )
      : 0;
  const weakCount = masteryStats?.weaknesses.length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Welcome back! Here is your learning overview.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Average Mastery" value={`${avgScore}%`} href="/profile" />
        <StatCard label="Due for Review" value={String(dueCount)} href="/revision" />
        <StatCard label="Weak Concepts" value={String(weakCount)} href="/revision" />
        <StatCard label="Enrollments" value={String(enrollments?.items.length ?? 0)} href="/courses" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Current Roadmap</h2>
          {currentRoadmap ? (
            <div className="mt-4">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">{currentRoadmap.title}</h3>
              <p className="mt-1 text-slate-600 dark:text-slate-400">{currentRoadmap.description}</p>
              <Link
                href={`/roadmaps/${currentRoadmap.id}`}
                className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                Continue Roadmap
              </Link>
            </div>
          ) : (
            <div className="mt-4">
              <p className="text-slate-600 dark:text-slate-400">You haven&apos;t enrolled in a roadmap yet.</p>
              <Link
                href="/roadmaps"
                className="mt-2 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                Browse Roadmaps
              </Link>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Revision Reminders</h2>
          {dueCount > 0 ? (
            <div className="mt-4">
              <p className="text-slate-900 dark:text-white">
                You have <strong>{dueCount}</strong> concepts due for review today.
              </p>
              <Link
                href="/revision"
                className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                Start Revision
              </Link>
            </div>
          ) : (
            <p className="mt-4 text-slate-600 dark:text-slate-400">No concepts due for review today. Great job!</p>
          )}
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Continue Learning</h2>
        {courses && courses.items.length > 0 ? (
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {courses.items.slice(0, 3).map((course) => (
              <Link
                key={course.id}
                href={`/courses/${course.id}`}
                className="rounded-xl border border-slate-200 bg-slate-50 p-4 transition hover:border-blue-300 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-blue-500"
              >
                <h3 className="font-semibold text-slate-900 dark:text-white">{course.title}</h3>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{course.technology}</p>
              </Link>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-slate-600 dark:text-slate-400">No courses available right now.</p>
        )}
      </section>
    </div>
  );
}

function StatCard({ label, value, href }: { label: string; value: string; href: string }) {
  return (
    <Link
      href={href}
      className="rounded-2xl border border-slate-200 bg-white p-6 transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
    >
      <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{value}</p>
    </Link>
  );
}
