import { getDashboardStats, getProfile } from "@/lib/api/api";
import { AlertCircle } from "lucide-react";
import { Briefcase, BookOpen, CheckCircle2, TrendingUp } from "lucide-react";
import Link from "next/link";

export default async function StatsSection({
  userId,
  email,
  token,
}: {
  userId: string;
  email: string;
  token: string;
}) {
  const [statsRaw, profile] = await Promise.all([
    (getDashboardStats(userId, email, token) as Promise<any>).catch(() => null),
    getProfile(userId, email, token).catch(() => null),
  ]);

  const stats = {
    eligible_matches: statsRaw?.eligible_matches ?? 0,
    opportunities_available: statsRaw?.opportunities_available ?? 0,
    skill_gaps_identified: statsRaw?.skill_gaps_identified ?? 0,
    applications_tracked: statsRaw?.applications_tracked ?? 0,
    readiness_score: statsRaw?.readiness_score ?? 0,
  };

  const profileComplete = !!(
    profile?.college &&
    profile?.stream &&
    profile?.year_of_study
  );

  return (
    <>
      {!profileComplete && (
        <div className="flex items-center justify-between gap-4 px-5 py-4 border border-yellow-500/30 bg-yellow-500/8 dark:bg-yellow-500/10 transition-all duration-500">
          <div className="flex items-center gap-3">
            <AlertCircle size={16} className="text-yellow-500 shrink-0" />
            <p className="font-mono text-sm text-yellow-700 dark:text-yellow-400">
              Complete your profile to unlock eligible opportunity matches.
            </p>
          </div>
          <Link
            href="/dashboard/profile"
            className="font-mono text-[14px] text-yellow-600 dark:text-yellow-400 border border-yellow-500/30 px-3 py-1.5 hover:bg-yellow-500/10 shrink-0 transition-all duration-500"
          >
            Complete profile →
          </Link>
        </div>
      )}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 transition-all duration-500">
        {[
          {
            label: "Eligible matches",
            value: String(stats.eligible_matches),
            icon: <CheckCircle2 size={16} />,
            color: "text-[#F97316]",
          },
          {
            label: "Opportunities available",
            value: String(stats.opportunities_available),
            icon: <Briefcase size={16} />,
            color: "text-green-500",
          },
          {
            label: "Skill gaps identified",
            value: String(stats.skill_gaps_identified),
            icon: <BookOpen size={16} />,
            color: "text-purple-500",
          },
          {
            label: "Applications tracked",
            value: String(stats.applications_tracked),
            icon: <TrendingUp size={16} />,
            color: "text-orange-500",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 transition-all duration-500"
          >
            <div className={`mb-2 ${stat.color}`}>{stat.icon}</div>
            <p className={`font-syne text-2xl font-extrabold ${stat.color}`}>
              {stat.value}
            </p>
            <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280] mt-0.5">
              {stat.label}
            </p>
          </div>
        ))}
      </div>
    </>
  );
}
