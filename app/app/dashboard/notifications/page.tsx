export const runtime = "edge";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { getNotifications } from "@/lib/api/api";
import { Bell } from "lucide-react";
import NotificationPrefs from "../_components/NotificationPrefs";

export default async function NotificationsPage() {
  const supabase = await createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  const { user } = session;
  const token = session.access_token;

  let notifications: Awaited<ReturnType<typeof getNotifications>> = [];
  try {
    notifications = await getNotifications(user.id, user.email ?? "", token);
  } catch {
    notifications = [];
  }

  return (
    <div className="flex flex-col gap-8 max-w-2xl">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="font-syne text-xl font-bold">Notifications</h1>
          <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
            Deadline reminders and application updates
          </p>
        </div>

        {notifications.length === 0 ? (
          <div className="flex flex-col items-center py-16 gap-3 border border-black/10 dark:border-white/8">
            <Bell size={24} className="text-gray-300" />
            <p className="font-mono text-[12px] text-gray-400">
              No notifications yet
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`border border-black/10 dark:border-white/8 p-4 ${!n.read ? "bg-[#F97316]/5 border-[#F97316]/20" : "bg-gray-50 dark:bg-[#0F1117]"}`}
              >
                <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
                  {n.title}
                </p>
                <p className="font-mono text-[12px] text-gray-500 mt-1">
                  {n.body}
                </p>
                <p className="font-mono text-[10px] text-gray-400 mt-2">
                  {new Date(n.created_at).toLocaleString()} · {n.channel}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-black/10 dark:border-white/8 pt-6">
        <NotificationPrefs
          userId={user.id}
          userEmail={user.email ?? ""}
          token={token}
        />
      </div>
    </div>
  );
}
