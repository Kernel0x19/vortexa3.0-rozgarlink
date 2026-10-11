export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import PlacementsClient from "../_components/PlacementsClient";

export const dynamic = "force-dynamic";

export default async function PlacementsPage() {
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
    <PlacementsClient
      userId={user.id}
      userEmail={user.email ?? ""}
      token={token}
    />
  );
}
