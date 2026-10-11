export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import InternshipsClient from "../_components/InternshipsClient";

export const dynamic = "force-dynamic";

export default async function InternshipsPage() {
  const supabase = await createClient();

  const { data: { user }, error } = await supabase.auth.getUser();
  if (!user || error) redirect("/auth/login");

  const { data: { session } } = await supabase.auth.getSession();
  const token = session?.access_token ?? "";

  return (
    <InternshipsClient
      userId={user.id}
      userEmail={user.email ?? ""}
      token={token}
    />
  );
}