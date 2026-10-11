export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import InternshipsClient from "../_components/InternshipsClient";

export const dynamic = "force-dynamic";

export default async function InternshipsPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  return (
    <InternshipsClient
      userId={session.user.id}
      userEmail={session.user.email ?? ""}
      token={session.access_token}
    />
  );
}