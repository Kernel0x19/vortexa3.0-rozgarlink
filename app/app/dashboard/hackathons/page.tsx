export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import HackathonsClient from "../_components/HackathonsClient";

export const dynamic = "force-dynamic";

export default async function HackathonsPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  return (
    <HackathonsClient
      userId={session.user.id}
      userEmail={session.user.email ?? ""}
      token={session.access_token}
    />
  );
}