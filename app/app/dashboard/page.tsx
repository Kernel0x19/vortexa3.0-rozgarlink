export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import StatsSection from "./_components/StatsSection";
import EligibleMatchesAndDeadlines from "./_components/EligibleMatchesAndDeadlines";
import ApplicationsAndSaved from "./_components/ApplicationsAndSaved";
import QuickActions from "./_components/QuickActions";

function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 animate-pulse transition-all duration-500"
        >
          <div className="w-4 h-4 bg-gray-200 dark:bg-white/10 rounded mb-2 transition-all duration-500" />
          <div className="w-12 h-7 bg-gray-200 dark:bg-white/10 rounded mb-1 transition-all duration-500" />
          <div className="w-24 h-3 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
        </div>
      ))}
    </div>
  );
}

function CardsSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {[...Array(3)].map((_, i) => (
        <div
          key={i}
          className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] h-64 animate-pulse transition-all duration-500"
        />
      ))}
    </div>
  );
}

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  const { user } = session;
  const token = session.access_token;

  return (
    <div className="flex flex-col gap-6 max-w-300 transition-all duration-500">
      <Suspense fallback={<StatsSkeleton />}>
        <StatsSection userId={user.id} email={user.email ?? ""} token={token} />
      </Suspense>

      <QuickActions />

      {/* Eligible matches (hard-filtered) + upcoming deadlines */}
      <Suspense fallback={<CardsSkeleton />}>
        <EligibleMatchesAndDeadlines userId={user.id} email={user.email ?? ""} token={token} />
      </Suspense>

      {/* Application tracker + Skill gaps & pathways + Saved */}
      <Suspense fallback={<CardsSkeleton />}>
        <ApplicationsAndSaved userId={user.id} email={user.email ?? ""} token={token} />
      </Suspense>
    </div>
  );
}
