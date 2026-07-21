import { apiClient } from "./axios";

// Types
export interface PaginatedResponse<T = unknown> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface Course {
  id: string;
  slug: string;
  title: string;
  description: string;
  technology: string;
  is_published: boolean;
  created_at: string;
}

export interface Roadmap {
  id: string;
  slug: string;
  title: string;
  description: string;
  is_published: boolean;
  created_at: string;
}

export interface Concept {
  id: string;
  slug: string;
  title: string;
  description: string;
  course_id: string;
}

export interface Lesson {
  id: string;
  title: string;
  content: string;
  position: number;
  concept_id: string;
}

export interface Enrollment {
  id: string;
  roadmap_id: string | null;
  course_id: string | null;
  started_at: string;
}

export interface Mastery {
  concept_id: string;
  score: number;
  confidence: number;
  attempts: number;
  correct_streak: number;
}

export interface RevisionSchedule {
  concept_id: string;
  due_at: string;
  interval_days: number;
}

export interface Project {
  id: string;
  title: string;
  slug: string;
  description: string;
  course_id: string;
}

export interface ExecutionResult {
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time_ms: number;
}

// Auth
export { login, register, logout, fetchMe } from "./axios";

// Courses
export async function fetchCourses(technology?: string) {
  const res = await apiClient.get<PaginatedResponse<Course>>("/courses/", {
    params: { technology },
  });
  return res.data;
}

export async function fetchCourse(id: string) {
  const res = await apiClient.get<Course>(`/courses/${id}`);
  return res.data;
}

export async function fetchCourseConcepts(courseId: string) {
  const res = await apiClient.get<PaginatedResponse<Concept>>(`/courses/${courseId}/concepts`);
  return res.data;
}

// Roadmaps
export async function fetchRoadmaps() {
  const res = await apiClient.get<PaginatedResponse<Roadmap>>("/roadmaps/");
  return res.data;
}

export async function fetchRoadmap(id: string) {
  const res = await apiClient.get<Roadmap>(`/roadmaps/${id}`);
  return res.data;
}

export async function fetchRoadmapCourses(id: string) {
  const res = await apiClient.get<PaginatedResponse<Course>>(`/roadmaps/${id}/courses`);
  return res.data;
}

// Enrollments
export async function fetchEnrollments() {
  const res = await apiClient.get<PaginatedResponse<Enrollment>>("/enrollments/");
  return res.data;
}

export async function createEnrollment(data: { roadmap_id?: string; course_id?: string }) {
  const res = await apiClient.post<Enrollment>("/enrollments/", data);
  return res.data;
}

// Lessons
export async function fetchConceptLessons(conceptId: string) {
  const res = await apiClient.get<PaginatedResponse<Lesson>>(`/lessons/concept/${conceptId}`);
  return res.data;
}

export async function fetchLesson(lessonId: string) {
  const res = await apiClient.get<Lesson>(`/lessons/${lessonId}`);
  return res.data;
}

// Mastery
export async function fetchMastery() {
  const res = await apiClient.get<PaginatedResponse<Mastery>>("/mastery/");
  return res.data;
}

export async function fetchStrengthsWeaknesses() {
  const res = await apiClient.get<{ strengths: Mastery[]; weaknesses: Mastery[] }>(
    "/mastery/strengths-weaknesses"
  );
  return res.data;
}

// Revision
export async function fetchDueRevisions() {
  const res = await apiClient.get<RevisionSchedule[]>("/revision/due");
  return res.data;
}

export async function submitReview(conceptId: string, quality: number) {
  const res = await apiClient.post("/revision/review", { concept_id: conceptId, quality });
  return res.data;
}

// Projects
export async function fetchCourseProjects(courseId: string) {
  const res = await apiClient.get<PaginatedResponse<Project>>(`/projects/course/${courseId}`);
  return res.data;
}

export async function fetchProject(projectId: string) {
  const res = await apiClient.get<Project>(`/projects/${projectId}`);
  return res.data;
}

export async function createProjectSubmission(data: {
  project_id: string;
  repository_url: string;
}) {
  const res = await apiClient.post("/projects/submissions", data);
  return res.data;
}

// Execution
export async function runCode(data: { language: string; code: string }) {
  const res = await apiClient.post<ExecutionResult>("/execution/run", data);
  return res.data;
}

// AI
export async function sendChatMessage(messages: { role: "user" | "assistant"; content: string }[]) {
  const res = await apiClient.post("/ai/chat", { messages });
  return res.data as { content: string };
}

export async function reviewCode(data: { language: string; code: string; context?: string }) {
  const res = await apiClient.post("/ai/code-review", data);
  return res.data as { feedback: string };
}
