import { getApplications } from "@/lib/api/api";
import Link from "next/link";
import {
  Briefcase,
  BookmarkCheck,
  BookOpen,
  ChevronRight,
  Inbox,
} from "lucide-react";

function EmptyState({
  message,
  action,
}: {
  message: string;
  action?: { label: string; href: string };
}) {
  return (
    <div className="flex flex-col items-center justify-center py-10 px-5 gap-3 transition-all duration-500">
      <Inbox
        size={22}
        className="text-gray-300 dark:text-white/20 transition-all duration-500"
      />
      <p className="font-mono text-[14px] text-gray-400 dark:text-[#6B7280] text-center transition-all duration-500">
        {message}
      </p>
      {action && (
        <Link
          href={action.href}
          className="font-mono text-[14px] text-[#F97316] hover:underline"
        >
          {action.label} →
        </Link>
      )}
    </div>
  );
}

interface AppData {
  id: string;
  opportunity?: { title: string; employer?: string };
  state: string;
  progress_pct: number;
  saved: boolean;
  created_at: string;
  skill_gaps?: { skill: string; pathway?: string }[];
}

export default async function ApplicationsAndSaved({
  userId,
  email,
  token,
}: {
  userId: string;
  email: string;
  token: string;
}) {
  const appsData = await getApplications(userId, email, token).catch(
    () => [] as AppData[],
  );

  const applications = appsData.slice(0, 5).map((a: AppData) => ({
    id: a.id,
    title: a.opportunity?.title ?? "Application",
    employer: a.opportunity?.employer ?? null,
    status: a.state.replace(/_/g, " "),
    pct: a.progress_pct,
  }));

  const saved = appsData
    .filter((a: AppData) => a.saved)
    .slice(0, 4)
    .map((a: AppData) => ({
      id: a.id,
      title: a.opportunity?.title ?? "Saved",
      saved: new Date(a.created_at).toLocaleDateString(),
    }));

  // Skill gaps: pull from applications that have gap data
  const skillGaps = appsData
    .flatMap((a: AppData) => a.skill_gaps ?? [])
    .slice(0, 4);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
      {/* Application Progress */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
          <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
            Application Progress
          </p>
          <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
            Track your active applications
          </p>
        </div>
        {applications.length === 0 ? (
          <EmptyState
            message="No applications tracked yet. Apply to eligible opportunities and track them here."
            action={{
              label: "Find opportunities",
              href: "/dashboard/search",
            }}
          />
        ) : (
          <div className="flex flex-col gap-4 p-5">
            {applications.map((app) => (
              <div key={app.id}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="min-w-0">
                    <p className="font-mono text-[14px] text-gray-900 dark:text-[#F0F4FF] truncate transition-all duration-500">
                      {app.title}
                    </p>
                    {app.employer && (
                      <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280]">
                        {app.employer}
                      </p>
                    )}
                  </div>
                  <span
                    className={`font-mono text-[12px] shrink-0 ml-2 ${
                      app.pct === 100
                        ? "text-green-500"
                        : app.pct < 50
                          ? "text-yellow-500"
                          : "text-[#F97316]"
                    }`}
                  >
                    {app.status}
                  </span>
                </div>
                <div className="w-full h-1.5 bg-black/8 dark:bg-white/8 rounded-full overflow-hidden transition-all duration-500">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${app.pct === 100 ? "bg-green-500" : "bg-[#F97316]"}`}
                    style={{ width: `${app.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Skill Gaps & Learning Pathways — replaces AI Chat panel */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              What-If &amp; Skill Gaps
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
              Career Impact Lab · Counterfactual Simulator
            </p>
          </div>
          <Link
            href="/dashboard/what-if"
            className="font-mono text-[11px] text-[#F97316] hover:underline flex items-center gap-1 transition-all duration-500"
          >
            Launch Lab <ChevronRight size={12} />
          </Link>
        </div>
        {skillGaps.length === 0 ? (
          <EmptyState
            message="No skill gaps yet. Mark opportunities as interested to see what skills you need and suggested learning pathways."
            action={{
              label: "Browse opportunities",
              href: "/dashboard/search",
            }}
          />
        ) : (
          <div className="flex flex-col">
            {skillGaps.map((gap, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 px-5 py-3.5 ${i !== skillGaps.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} transition-all duration-500`}
              >
                <div className="w-7 h-7 flex items-center justify-center shrink-0 bg-purple-500/10 border border-purple-500/20 text-purple-500 mt-0.5">
                  <BookOpen size={12} />
                </div>
                <div className="min-w-0">
                  <p className="font-mono text-[14px] text-gray-900 dark:text-[#F0F4FF]">
                    {gap.skill}
                  </p>
                  {gap.pathway && (
                    <p className="font-mono text-[12px] text-[#fdba74] mt-0.5 truncate">
                      → {gap.pathway}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Saved Opportunities */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Saved Opportunities
            </p>
            <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280] transition-all duration-500">
              Your bookmarked items
            </p>
          </div>
          <BookmarkCheck
            size={14}
            className="text-gray-400 dark:text-[#6B7280]"
          />
        </div>
        {saved.length === 0 ? (
          <EmptyState
            message="No saved opportunities yet. Browse and bookmark roles you want to revisit."
            action={{
              label: "Find opportunities",
              href: "/dashboard/search",
            }}
          />
        ) : (
          <div className="flex flex-col">
            {saved.map((s, i) => (
              <div
                key={s.id}
                className={`flex items-center gap-3 px-5 py-3.5 ${i !== saved.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
              >
                <div className="w-7 h-7 flex items-center justify-center shrink-0 bg-[#F97316]/10 border border-[#F97316]/20 text-[#F97316]">
                  <Briefcase size={13} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-[14px] text-gray-900 dark:text-[#F0F4FF] truncate">
                    {s.title}
                  </p>
                  <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280]">
                    Saved {s.saved}
                  </p>
                </div>
                <ChevronRight
                  size={13}
                  className="text-gray-300 dark:text-white/20 group-hover:text-[#F97316] shrink-0 transition-colors duration-500"
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
