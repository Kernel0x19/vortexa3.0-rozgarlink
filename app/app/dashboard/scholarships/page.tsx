export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import ScholarshipsClient from "../_components/ScholarshipsClient";

export default async function ScholarshipsPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  return (
    <ScholarshipsClient
      userId={session.user.id}
      userEmail={session.user.email ?? ""}
      token={session.access_token}
    />
  );
}