import { getRecommendations, getDashboardStats } from "@/lib/api/api";
import Link from "next/link";
import { GraduationCap, Clock, ChevronRight, Inbox } from "lucide-react";

function EmptyState({
  message,
  action,
}: {
  message: string;
  action?: { label: string; href: string };
}) {
  return (
    <div className="flex flex-col items-center justify-center py-10 px-5 gap-3">
      <Inbox size={22} className="text-gray-300 dark:text-white/20" />
      <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] text-center">
        {message}
      </p>
      {action && (
        <Link
          href={action.href}
          className="font-mono text-[12px] text-[#F97316] hover:underline"
        >
          {action.label} →
        </Link>
      )}
    </div>
  );
}

function daysLeft(deadline: string) {
  return Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000);
}

interface Match {
  opportunity: {
    id: string;
    title: string;
    amount_max: number | null;
    deadline: string | null;
  };
  match_score: number;
}

export default async function ScholarshipsAndDeadlines({
  userId,
  email,
  token,
}: {
  userId: string;
  email: string;
  token: string;
}) {
  const [recData, stats] = await Promise.all([
    getRecommendations(userId, email, undefined, token).catch(() => ({
      matches: [],
      total: 0,
      readiness_score: 0,
    })),
    getDashboardStats(userId, email, token).catch(() => ({
      readiness_score: 0,
      scholarships_matched: 0,
      internships_available: 0,
      documents_uploaded: 0,
      applications_tracked: 0,
    })),
  ]);

  const scholarships = recData.matches.slice(0, 5).map((m: Match) => ({
    id: m.opportunity.id,
    title: m.opportunity.title,
    amount: m.opportunity.amount_max
      ? `Up to ₹${m.opportunity.amount_max.toLocaleString()}`
      : "—",
    deadline: m.opportunity.deadline ?? "TBD",
    match: m.match_score,
  }));

  const deadlines = recData.matches
    .filter((m: Match) => m.opportunity.deadline)
    .slice(0, 5)
    .map((m: Match) => ({
      id: m.opportunity.id,
      title: m.opportunity.title,
      date: m.opportunity.deadline!,
      daysLeft: daysLeft(m.opportunity.deadline!),
      type: "scholarship",
    }))
    .sort((a, b) => a.daysLeft - b.daysLeft);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
      <div className="lg:col-span-2 border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Matched Scholarships
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Ranked by eligibility fit · Readiness {stats.readiness_score}%
            </p>
          </div>
          <Link
            href="/dashboard/scholarships"
            className="font-mono text-[11px] text-[#F97316] hover:underline flex items-center gap-1"
          >
            View all <ChevronRight size={12} />
          </Link>
        </div>
        {scholarships.length === 0 ? (
          <EmptyState
            message="No scholarships matched yet. Complete your profile so the AI can find relevant scholarships for you."
            action={{ label: "Complete profile", href: "/dashboard/profile" }}
          />
        ) : (
          <div className="flex flex-col transition-all duration-500">
            {scholarships.map((s, i) => (
              <Link
                key={s.id}
                href="/dashboard/scholarships"
                className={`flex items-center justify-between gap-4 px-5 py-4 ${i !== scholarships.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 bg-[#F97316]/10 border border-[#F97316]/20 flex items-center justify-center text-[#F97316] shrink-0">
                    <GraduationCap size={14} />
                  </div>
                  <div className="min-w-0">
                    <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] truncate">
                      {s.title}
                    </p>
                    <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                      {s.amount} · Deadline {s.deadline}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <div className="text-right">
                    <p className="font-mono text-[12px] text-[#F97316] font-bold">
                      {s.match}%
                    </p>
                    <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
                      match
                    </p>
                  </div>
                  <ChevronRight
                    size={14}
                    className="text-gray-300 dark:text-white/20 group-hover:text-[#F97316] transition-colors duration-500"
                  />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Upcoming Deadlines
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Don&apos;t miss these
            </p>
          </div>
          <Clock size={14} className="text-gray-400 dark:text-[#6B7280]" />
        </div>
        {deadlines.length === 0 ? (
          <EmptyState message="No upcoming deadlines. Save scholarships or internships to track their deadlines here." />
        ) : (
          <div className="flex flex-col">
            {deadlines.map((d, i) => (
              <div
                key={d.id}
                className={`flex items-center justify-between gap-3 px-5 py-3.5 transition-all duration-500 ${i !== deadlines.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""}`}
              >
                <div className="min-w-0">
                  <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] truncate">
                    {d.title}
                  </p>
                  <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
                    {d.date}
                  </p>
                </div>
                <span
                  className={`font-mono text-[10px] px-2 py-0.5 border shrink-0 ${
                    d.daysLeft <= 14
                      ? "border-red-500/30 bg-red-500/10 text-red-500"
                      : d.daysLeft <= 30
                        ? "border-yellow-500/30 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400"
                        : "border-black/10 dark:border-white/8 text-gray-400 dark:text-[#6B7280]"
                  }`}
                >
                  {d.daysLeft}d left
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
