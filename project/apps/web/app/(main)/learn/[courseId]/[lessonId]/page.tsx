"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Circle,
  Clock,
  GraduationCap,
  MessageCircle,
  Play,
} from "lucide-react";
import { fetchCourseDetail, fetchLesson, updateLessonProgress } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Skeleton } from "@/components/ui/skeleton";
import { useAIChat } from "@/hooks/use-ai-chat";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

interface CodeBlockProps {
  language: string;
  code: string;
}

function CodeBlock({ language, code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 overflow-hidden rounded-xl border border-slate-200 bg-slate-950 dark:border-slate-700">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2">
        <span className="text-xs font-medium text-slate-400">{language}</span>
        <button
          onClick={handleCopy}
          className="text-xs text-slate-400 hover:text-slate-200"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre className="overflow-x-auto p-4">
        <code className="text-sm text-slate-100">{code}</code>
      </pre>
    </div>
  );
}

function LessonContent({ content }: { content: Record<string, unknown> }) {
  const body = typeof content.body === "string" ? content.body : JSON.stringify(content, null, 2);

  return (
    <div className="pro prose prose-slate max-w-none dark:prose-invert">
      <ReactMarkdown
        components={{
          code({ children, className }) {
            const language = className?.replace("language-", "") || "text";
            return <CodeBlock language={language} code={String(children)} />;
          },
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  );
}

export default function LearnPage() {
  const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"content" | "mentor">("content");
  const [code, setCode] = useState("");
  const { messages, setMessages, isChatting, sendMessage } = useAIChat();
  const [chatInput, setChatInput] = useState("");

  const {
    data: courseDetail,
    isLoading: courseLoading,
    error: courseError,
    refetch: refetchCourse,
  } = useQuery({
    queryKey: ["course-detail", courseId],
    queryFn: () => fetchCourseDetail(courseId),
  });

  const {
    data: lessonDetail,
    isLoading: lessonLoading,
    error: lessonError,
    refetch: refetchLesson,
  } = useQuery({
    queryKey: ["lesson-detail", lessonId],
    queryFn: () => fetchLesson(lessonId),
  });

  const markCompleteMutation = useMutation({
    mutationFn: () => updateLessonProgress(lessonId, true),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["course-detail", courseId] });
    },
  });

  const allLessons = useMemo(
    () => courseDetail?.modules.flatMap((m) => m.lessons) ?? [],
    [courseDetail]
  );

  const currentIndex = allLessons.findIndex((l) => l.id === lessonId);
  const previousLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
  const nextLesson =
    currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;

  const currentModule = courseDetail?.modules.find((m) =>
    m.lessons.some((l) => l.id === lessonId)
  );

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;
    sendMessage(chatInput);
    setChatInput("");
  };

  const handleMarkComplete = () => {
    markCompleteMutation.mutate();
  };

  if (courseLoading || lessonLoading) {
    return <LearnSkeleton />;
  }

  if (courseError || lessonError || !courseDetail || !lessonDetail) {
    return (
      <div className="space-y-4">
        <ErrorMessage>
          Failed to load lesson.{" "}
          <Button onClick={() => { refetchCourse(); refetchLesson(); }} variant="secondary" size="sm" className="ml-2">
            Retry
          </Button>
        </ErrorMessage>
      </div>
    );
  }

  const lesson = lessonDetail;
  const contentBody =
    typeof lesson.content === "object" && lesson.content !== null
      ? (lesson.content as Record<string, unknown>)
      : { body: String(lesson.content || "") };

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col gap-4 lg:flex-row">
      {/* Sidebar */}
      <aside className="hidden w-full flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900 lg:flex lg:w-72">
        <div className="border-b border-slate-200 p-4 dark:border-slate-700">
          <Link
            href={`/courses/${courseId}`}
            className="text-sm font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
          >
            ← Back to course
          </Link>
          <h2 className="mt-2 line-clamp-2 text-lg font-bold text-slate-900 dark:text-white">
            {courseDetail.course.title}
          </h2>
          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div
              className="h-full rounded-full bg-blue-600 transition-all"
              style={{ width: `${courseDetail.progress.progress_percent}%` }}
            />
          </div>
          <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">
            {courseDetail.progress.progress_percent}% complete
          </p>
        </div>
        <div className="flex-1 overflow-y-auto p-3">
          {courseDetail.modules.map((module) => (
            <div key={module.id} className="mb-4">
              <h3 className="px-2 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                {module.title}
              </h3>
              <ul className="mt-2 space-y-1">
                {module.lessons.map((l) => {
                  const isCurrent = l.id === lessonId;
                  const isCompleted = l.is_completed;
                  return (
                    <li key={l.id}>
                      <Link
                        href={`/learn/${courseId}/${l.id}`}
                        className={`flex items-start gap-2 rounded-lg px-2 py-2 text-sm transition ${
                          isCurrent
                            ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
                            : "text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800"
                        }`}
                      >
                        {isCompleted ? (
                          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                        ) : (
                          <Circle className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                        )}
                        <span className={isCurrent ? "font-medium" : ""}>{l.title}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900">
        <div className="border-b border-slate-200 p-4 dark:border-slate-700">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                <GraduationCap className="h-4 w-4" />
                <span>{currentModule?.title}</span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {lesson.duration_minutes} min
                </span>
              </div>
              <h1 className="mt-1 text-xl font-bold text-slate-900 dark:text-white">
                {lesson.title}
              </h1>
            </div>
            <div className="flex items-center gap-2 lg:hidden">
              <Button
                variant="secondary"
                onClick={() => setActiveTab(activeTab === "content" ? "mentor" : "content")}
              >
                {activeTab === "content" ? "AI Mentor" : "Content"}
              </Button>
            </div>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {activeTab === "content" ? (
            <div className="flex-1 overflow-y-auto p-4 lg:p-6">
              <LessonContent content={contentBody} />

              <div className="mt-8 flex flex-col gap-4 border-t border-slate-200 pt-6 dark:border-slate-700 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex gap-2">
                  {previousLesson && (
                    <Link
                      href={`/learn/${courseId}/${previousLesson.id}`}
                      className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Link>
                  )}
                  {nextLesson && (
                    <Link
                      href={`/learn/${courseId}/${nextLesson.id}`}
                      className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  )}
                </div>
                <Button
                  onClick={handleMarkComplete}
                  disabled={lesson.is_completed || markCompleteMutation.isPending}
                  className="gap-2"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  {lesson.is_completed
                    ? "Completed"
                    : markCompleteMutation.isPending
                    ? "Saving..."
                    : "Mark as Complete"}
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-4 lg:hidden">
              <AIMentorPanel
                messages={messages}
                isChatting={isChatting}
                chatInput={chatInput}
                setChatInput={setChatInput}
                onSend={handleSendMessage}
              />
            </div>
          )}

          {/* AI Mentor - desktop */}
          <div className="hidden w-80 flex-col border-l border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900 lg:flex">
            <AIMentorPanel
              messages={messages}
              isChatting={isChatting}
              chatInput={chatInput}
              setChatInput={setChatInput}
              onSend={handleSendMessage}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

function AIMentorPanel({
  messages,
  isChatting,
  chatInput,
  setChatInput,
  onSend,
}: {
  messages: Array<{ role: "user" | "assistant"; content: string }>;
  isChatting: boolean;
  chatInput: string;
  setChatInput: (value: string) => void;
  onSend: () => void;
}) {
  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-4 flex items-center gap-2">
        <MessageCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        <h3 className="font-bold text-slate-900 dark:text-white">AI Mentor</h3>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Ask me anything about this lesson, your code, or related concepts.
          </p>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`rounded-lg p-2.5 text-sm ${
              message.role === "user"
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-900 dark:bg-slate-800 dark:text-slate-100"
            }`}
          >
            {message.content}
          </div>
        ))}
        {isChatting && <p className="text-sm text-slate-500">AI is typing...</p>}
      </div>
      <div className="mt-3 flex gap-2">
        <input
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onSend()}
          placeholder="Ask a question..."
          className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-white"
        />
        <Button onClick={onSend} disabled={isChatting} size="sm">
          Send
        </Button>
      </div>
    </div>
  );
}

function LearnSkeleton() {
  return (
    <div className="flex h-[calc(100vh-7rem)] gap-4">
      <div className="hidden w-72 flex-col gap-4 lg:flex">
        <Skeleton className="h-full" />
      </div>
      <div className="flex-1 space-y-4">
        <Skeleton className="h-32" />
        <Skeleton className="h-64" />
      </div>
    </div>
  );
}
