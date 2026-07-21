"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { createEnrollment, fetchCourse, fetchCourseConcepts } from "@/lib/api";

export default function CourseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [enrolled, setEnrolled] = useState(false);

  const { data: course, isLoading: courseLoading } = useQuery({
    queryKey: ["course", id],
    queryFn: () => fetchCourse(id),
  });

  const { data: conceptsData, isLoading: conceptsLoading } = useQuery({
    queryKey: ["course-concepts", id],
    queryFn: () => fetchCourseConcepts(id),
  });

  const enrollMutation = useMutation({
    mutationFn: () => createEnrollment({ course_id: id }),
    onSuccess: () => {
      setEnrolled(true);
      queryClient.invalidateQueries({ queryKey: ["enrollments"] });
    },
  });

  if (courseLoading || !course) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-1/2 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
        <div className="h-4 w-1/3 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
        <div className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div>
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              {course.technology}
            </span>
          </div>
          <h1 className="mt-3 text-3xl font-bold text-slate-900 dark:text-white">{course.title}</h1>
          <p className="mt-2 max-w-2xl text-slate-600 dark:text-slate-400">{course.description}</p>
        </div>
        <button
          onClick={() => enrollMutation.mutate()}
          disabled={enrolled || enrollMutation.isPending}
          className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
        >
          {enrolled ? "Enrolled" : enrollMutation.isPending ? "Enrolling..." : "Enroll Now"}
        </button>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">Concepts</h2>
        {conceptsLoading ? (
          <div className="mt-4 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" />
            ))}
          </div>
        ) : conceptsData?.items.length ? (
          <ul className="mt-4 space-y-3">
            {conceptsData.items.map((concept) => (
              <li
                key={concept.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800"
              >
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{concept.title}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{concept.description}</p>
                </div>
                <Link
                  href={`/workspace/${concept.id}`}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                >
                  Start
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-slate-600 dark:text-slate-400">No concepts available yet.</p>
        )}
      </section>
    </div>
  );
}
