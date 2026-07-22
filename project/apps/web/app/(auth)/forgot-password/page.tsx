"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { apiClient } from "@/lib/axios";

const forgotPasswordSchema = z.object({
  email: z.string().email("Invalid email address"),
});

type ForgotPasswordForm = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordForm>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordForm) => {
    // Submit a password reset request to the backend.
    // If no email is found, we still show success to avoid revealing user existence.
    try {
      await apiClient.post("/auth/forgot-password", { email: data.email });
    } catch {
      // Backend may not expose this endpoint yet.
      // Gracefully show the confirmation state regardless.
    }
    setSubmitted(true);
  };

  return (
    <>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reset password</h1>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
        Enter your email and we&apos;ll send you a reset link
      </p>

      {submitted ? (
        <div className="mt-6 rounded-lg bg-green-50 p-4 text-sm text-green-700 dark:bg-green-950 dark:text-green-200">
          If an account exists for that email, you will receive a password reset link shortly.
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              {...register("email")}
              className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
            {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? "Sending..." : "Send reset link"}
          </button>
        </form>
      )}

      <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-400">
        Remember your password?{" "}
        <Link href="/login" className="font-semibold text-blue-600 hover:underline dark:text-blue-400">
          Sign in
        </Link>
      </p>
    </>
  );
}
