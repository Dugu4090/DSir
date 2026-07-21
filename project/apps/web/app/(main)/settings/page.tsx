"use client";

import { useTheme } from "next-themes";
import { Card, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-slate-600 dark:text-slate-400">Manage your preferences.</p>
      </div>

      <Card>
        <CardTitle>Appearance</CardTitle>
        <p className="mt-2 text-slate-600 dark:text-slate-400">Choose your preferred theme.</p>
        <div className="mt-4 flex gap-2">
          <Button variant={theme === "light" ? "primary" : "secondary"} onClick={() => setTheme("light")}>
            Light
          </Button>
          <Button variant={theme === "dark" ? "primary" : "secondary"} onClick={() => setTheme("dark")}>
            Dark
          </Button>
          <Button variant={theme === "system" ? "primary" : "secondary"} onClick={() => setTheme("system")}>
            System
          </Button>
        </div>
      </Card>

      <Card>
        <CardTitle>Notifications</CardTitle>
        <p className="mt-2 text-slate-600 dark:text-slate-400">Revision reminders and course updates.</p>
        <div className="mt-4 flex items-center gap-3">
          <input
            type="checkbox"
            id="revision-reminders"
            defaultChecked
            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="revision-reminders" className="text-slate-700 dark:text-slate-300">
            Send revision reminders
          </label>
        </div>
      </Card>

      <Card>
        <CardTitle>Account</CardTitle>
        <p className="mt-2 text-slate-600 dark:text-slate-400">Manage your account settings.</p>
        <div className="mt-4 flex gap-2">
          <Button variant="secondary">Change Password</Button>
          <Button variant="danger">Delete Account</Button>
        </div>
      </Card>
    </div>
  );
}
