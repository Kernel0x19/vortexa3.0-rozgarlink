export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import WhatIfSimulatorClient from "../_components/WhatIfSimulatorClient";

export const dynamic = "force-dynamic";

export default async function WhatIfPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/auth/login");

  let token = "";
  try {
    const originalWarn = console.warn;
    console.warn = (...args: unknown[]) => {
      if (typeof args[0] === "string" && args[0].includes("getSession()")) return;
      originalWarn(...args);
    };
    const {
      data: { session },
    } = await supabase.auth.getSession();
    console.warn = originalWarn;
    token = session?.access_token ?? "";
  } catch {
    token = "";
  }

  return (
    <div className="flex flex-col gap-6 max-w-300 transition-all duration-500">
      <div>
        <h1 className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-xl">
          Career Impact Lab — What-If Simulator
        </h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Counterfactual Skill &amp; Preference Simulator · Live Opportunity Recalculation · Market Impact Pathways
        </p>
      </div>

      <WhatIfSimulatorClient
        userId={user.id}
        userEmail={user.email ?? ""}
        token={token}
      />
    </div>
  );
}
