import Link from "next/link";
import {
  Briefcase,
  Building2,
  Trophy,
  Clock,
  ChevronRight,
  Inbox,
  ShieldCheck,
  Calendar,
} from "lucide-react";
import {
  getJobRecommendations,
  getHackathons,
  getInternshipRecommendations,
} from "@/lib/api/api";

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

function calculateDaysLeft(dateStr: string | null | undefined): number | null {
  if (!dateStr) return null;
  const target = new Date(dateStr);
  if (isNaN(target.getTime())) return null;
  const now = new Date();
  const dTarget = new Date(
    target.getFullYear(),
    target.getMonth(),
    target.getDate(),
  );
  const dNow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.round((dTarget.getTime() - dNow.getTime()) / (1000 * 60 * 60 * 24));
}

interface TopMatchItem {
  id: string;
  title: string;
  employer: string;
  location: string;
  category: "Placement" | "Internship";
  match: number;
  href: string;
}

interface UpcomingDeadlineItem {
  id: string;
  title: string;
  organization: string;
  category: "Placement" | "Hackathon" | "Internship";
  categoryColor: string;
  href: string;
  date: string;
  daysLeft: number;
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
  // Fetch Placements, Hackathons, and Internships in parallel (NO SCHOLARSHIPS)
  const [placementsRes, hackathonsRes, internshipsRes] = await Promise.all([
    getJobRecommendations(userId, email, { limit: 30 }, token).catch(() => ({
      matches: [],
      total: 0,
      readiness_score: 0,
    })),
    getHackathons(userId, email, { limit: 40 }, token).catch(() => ({
      items: [],
      total: 0,
    })),
    getInternshipRecommendations(userId, email, undefined, token).catch(() => ({
      matches: [],
      total: 0,
    })),
  ]);

  // 1. Gather all upcoming deadlines across Placements, Hackathons, and Internships
  const allDeadlines: UpcomingDeadlineItem[] = [];

  // Placements deadlines
  for (const match of placementsRes.matches || []) {
    const opp = match.opportunity;
    if (opp?.deadline) {
      const days = calculateDaysLeft(opp.deadline);
      if (days !== null && days >= 0) {
        allDeadlines.push({
          id: `job-${opp.id}`,
          title: opp.title,
          organization: opp.company ?? "Placement",
          category: "Placement",
          categoryColor:
            "border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400",
          href: "/dashboard/placements",
          date: opp.deadline,
          daysLeft: days,
        });
      }
    }
  }

  // Hackathons deadlines
  for (const h of hackathonsRes.items || []) {
    if (h.registration_deadline) {
      const days = calculateDaysLeft(h.registration_deadline);
      if (days !== null && days >= 0) {
        allDeadlines.push({
          id: `hack-${h.id}`,
          title: h.title,
          organization: h.organizer ?? h.source,
          category: "Hackathon",
          categoryColor:
            "border-purple-500/30 bg-purple-500/10 text-purple-600 dark:text-purple-400",
          href: "/dashboard/hackathons",
          date: h.registration_deadline,
          daysLeft: days,
        });
      }
    }
  }

  // Internships deadlines
  for (const match of internshipsRes.matches || []) {
    const opp = match.opportunity;
    if (opp?.deadline) {
      const days = calculateDaysLeft(opp.deadline);
      if (days !== null && days >= 0) {
        allDeadlines.push({
          id: `intern-${opp.id}`,
          title: opp.title,
          organization: opp.raw_data?.company ?? "Internship",
          category: "Internship",
          categoryColor:
            "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
          href: "/dashboard/internships",
          date: opp.deadline,
          daysLeft: days,
        });
      }
    }
  }

  // Sort upcoming deadlines so soonest deadline comes first
  const sortedDeadlines = allDeadlines
    .sort((a, b) => a.daysLeft - b.daysLeft)
    .slice(0, 6);

  // 2. Gather top eligible matches across Placements and Internships
  const topMatches: TopMatchItem[] = [];

  for (const m of placementsRes.matches || []) {
    topMatches.push({
      id: `p-${m.opportunity.id}`,
      title: m.opportunity.title,
      employer: m.opportunity.company ?? "Company",
      location: m.opportunity.location ?? "India",
      category: "Placement",
      match: Math.round(m.match_score),
      href: "/dashboard/placements",
    });
  }

  for (const m of internshipsRes.matches || []) {
    topMatches.push({
      id: `i-${m.opportunity.id}`,
      title: m.opportunity.title,
      employer: m.opportunity.raw_data?.company ?? "Company",
      location: m.opportunity.raw_data?.location ?? "India",
      category: "Internship",
      match: Math.round(m.match_score),
      href: "/dashboard/internships",
    });
  }

  // Sort top matches by match score descending
  const sortedMatches = topMatches
    .sort((a, b) => b.match - a.match)
    .slice(0, 5);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-500">
      {/* Top Matches — 2/3 width */}
      <div className="lg:col-span-2 border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8 transition-all duration-500">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Eligible Matches
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              AI-scored placement &amp; internship recommendations
            </p>
          </div>
          <Link
            href="/dashboard/placements"
            className="font-mono text-[11px] text-[#F97316] hover:underline flex items-center gap-1"
          >
            Explore all <ChevronRight size={12} />
          </Link>
        </div>

        {sortedMatches.length === 0 ? (
          <EmptyState
            message="No matches found yet. Update your profile skills to view tailored job & internship recommendations."
            action={{ label: "Update profile", href: "/dashboard/profile" }}
          />
        ) : (
          <div className="flex flex-col transition-all duration-500">
            {sortedMatches.map((m, i) => (
              <Link
                key={m.id}
                href={m.href}
                className={`flex items-center justify-between gap-4 px-5 py-4 ${
                  i !== sortedMatches.length - 1
                    ? "border-b border-black/10 dark:border-white/8"
                    : ""
                } hover:bg-white dark:hover:bg-[#161822] transition-colors duration-500 cursor-pointer group`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 bg-[#F97316]/10 border border-[#F97316]/20 flex items-center justify-center text-[#F97316] shrink-0">
                    {m.category === "Placement" ? (
                      <Building2 size={14} />
                    ) : (
                      <Briefcase size={14} />
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] truncate">
                      {m.title}
                    </p>
                    <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                      {m.employer} · {m.location}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {/* Category Pill */}
                  <span
                    className={`font-mono text-[9px] px-1.5 py-0.5 border ${
                      m.category === "Placement"
                        ? "border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400"
                        : "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                    }`}
                  >
                    {m.category}
                  </span>

                  {/* Match Score */}
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

      {/* Upcoming Deadlines — 1/3 width (Placements, Hackathons, Internships ONLY) */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] transition-all duration-500">
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/8">
          <div>
            <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm transition-all duration-500">
              Upcoming Deadlines
            </p>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Placements · Hackathons · Internships
            </p>
          </div>
          <Clock size={14} className="text-gray-400 dark:text-[#6B7280]" />
        </div>

        {sortedDeadlines.length === 0 ? (
          <EmptyState message="No upcoming deadlines found for active placements, hackathons, or internships." />
        ) : (
          <div className="flex flex-col">
            {sortedDeadlines.map((d, i) => (
              <Link
                key={d.id}
                href={d.href}
                className={`flex items-center justify-between gap-3 px-5 py-3.5 transition-all duration-500 hover:bg-white dark:hover:bg-[#161822] ${
                  i !== sortedDeadlines.length - 1
                    ? "border-b border-black/10 dark:border-white/8"
                    : ""
                }`}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span
                      className={`font-mono text-[9px] px-1 py-0.2 border shrink-0 ${d.categoryColor}`}
                    >
                      {d.category}
                    </span>
                    <p className="font-mono text-[12px] text-gray-900 dark:text-[#F0F4FF] truncate font-medium">
                      {d.title}
                    </p>
                  </div>
                  <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] truncate">
                    {d.organization} · {d.date}
                  </p>
                </div>

                <span
                  className={`font-mono text-[10px] px-2 py-0.5 border shrink-0 ml-2 ${
                    d.daysLeft <= 3
                      ? "border-red-500/40 bg-red-500/15 text-red-500 font-bold"
                      : d.daysLeft <= 7
                        ? "border-orange-500/30 bg-orange-500/10 text-orange-500"
                        : d.daysLeft <= 14
                          ? "border-yellow-500/30 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400"
                          : "border-black/10 dark:border-white/8 text-gray-400 dark:text-[#6B7280]"
                  }`}
                >
                  {d.daysLeft === 0
                    ? "Today"
                    : d.daysLeft === 1
                      ? "1d left"
                      : `${d.daysLeft}d left`}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
