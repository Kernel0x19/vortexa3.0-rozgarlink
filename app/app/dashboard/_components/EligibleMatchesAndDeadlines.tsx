import { getRecommendations, getDashboardStats } from "@/lib/api/api";
import Link from "next/link";
import { Briefcase, Clock, ChevronRight, Inbox, ShieldCheck } from "lucide-react";

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
    employer: string | null;
    location: string | null;
    deadline: string | null;
  };
  match_score: number;
  eligibility_met: boolean;
  rank_reason: string | null;
}

export default async function EligibleMatchesAndDeadlines({
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
      eligible_matches: 0,
      opportunities_available: 0,
      skill_gaps_identified: 0,
      applications_tracked: 0,
    })),
  ]);

  // Only show eligibility-cleared matches — preference ranking applied on top
  const eligibleMatches = recData.matches
    .filter((m: Match) => m.eligibility_met)
    .slice(0, 5)
    .map((m: Match) => ({
      id: m.opportunity.id,
      title: m.opportunity.title,
      employer: m.opportunity.employer ?? "—",
      location: m.opportunity.location ?? "—",
      deadline: m.opportunity.deadline ?? "TBD",
      match: m.match_score,
      reason: m.rank_reason ?? null,
    }));

  const deadlines = recData.matches
    .filter((m: Match) => m.eligibility_met && m.opportunity.deadline)
    .slice(0, 5)
    .map((m: Match) => ({
      id: m.opportunity.id,
      title: m.opportunity.title,
      date: m.opportunity.deadline!,
      daysLeft: daysLeft(m.opportunity.deadline!),
    }))
    .sort((a, b) => a.daysLeft - b.daysLeft);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
      {/* Eligible Matches — 2/3 width */}
      <div className="lg:col-span-2 border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Eligible Matches
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Eligibility-cleared · Ranked by preference fit · Readiness {stats.readiness_score}%
            </p>
          </div>
          <Link
            href="/dashboard/search"
            className="font-mono text-[11px] text-[#F97316] hover:underline flex items-center gap-1"
          >
            View all <ChevronRight size={12} />
          </Link>
        </div>
        {eligibleMatches.length === 0 ? (
          <EmptyState
            message="No eligible matches yet. Complete your profile so the engine can check eligibility criteria against your qualifications."
            action={{ label: "Complete profile", href: "/dashboard/profile" }}
          />
        ) : (
          <div className="flex flex-col transition-all duration-500">
            {eligibleMatches.map((m, i) => (
              <Link
                key={m.id}
                href="/dashboard/search"
                className={`flex items-center justify-between gap-4 px-5 py-4 ${i !== eligibleMatches.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""} hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 bg-[#F97316]/10 border border-[#F97316]/20 flex items-center justify-center text-[#F97316] shrink-0">
                    <Briefcase size={14} />
                  </div>
                  <div className="min-w-0">
                    <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] truncate">
                      {m.title}
                    </p>
                    <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                      {m.employer} · {m.location}
                    </p>
                    {m.reason && (
                      <p className="font-mono text-[10px] text-[#fdba74] mt-0.5 truncate">
                        {m.reason}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {/* Eligibility badge — hard filter passed */}
                  <div className="flex items-center gap-1 px-1.5 py-0.5 border border-green-500/30 bg-green-500/8 text-green-500">
                    <ShieldCheck size={10} />
                    <span className="font-mono text-[9px]">Eligible</span>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-[12px] text-[#F97316] font-bold">
                      {m.match}%
                    </p>
                    <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
                      fit
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

      {/* Upcoming Deadlines — 1/3 width */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Upcoming Deadlines
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Eligible opportunities only
            </p>
          </div>
          <Clock size={14} className="text-gray-400 dark:text-[#6B7280]" />
        </div>
        {deadlines.length === 0 ? (
          <EmptyState message="No upcoming deadlines. Save opportunities to track their deadlines here." />
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
