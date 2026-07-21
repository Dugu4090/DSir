"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchCourses } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/error-message";
import { Button } from "@/components/ui/button";

const technologies = ["All", "Python", "JavaScript", "TypeScript", "Go", "Rust"];

export default function CoursesPage() {
  const [search, setSearch] = useState("");
  const [selectedTech, setSelectedTech] = useState("All");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["courses", selectedTech],
    queryFn: () => fetchCourses(selectedTech === "All" ? undefined : selectedTech),
  });

  const courses =
    data?.items.filter((course) => course.title.toLowerCase().includes(search.toLowerCase())) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Course Catalog</h1>
        <p className="text-slate-600 dark:text-slate-400">Browse our programming tracks and start learning.</p>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row">
        <input
          type="text"
          placeholder="Search courses..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white sm:w-96"
        />
        <select
          value={selectedTech}
          onChange={(e) => setSelectedTech(e.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
        >
          {technologies.map((tech) => (
            <option key={tech} value={tech}>
              {tech}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <ErrorMessage>
          Failed to load courses.{" "}
          <Button onClick={() => refetch()} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <Link
              key={course.id}
              href={`/courses/${course.id}`}
              className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
            >
              <div className="flex items-center justify-between">
                <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                  {course.technology}
                </span>
              </div>
              <h3 className="mt-4 text-lg font-bold text-slate-900 dark:text-white">{course.title}</h3>
              <p className="mt-2 line-clamp-2 flex-1 text-sm text-slate-600 dark:text-slate-400">
                {course.description}
              </p>
              <span className="mt-4 text-sm font-semibold text-blue-600 dark:text-blue-400">View course →</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
