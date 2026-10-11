export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import ProfileFormWrapper from "../_components/ProfileFormWrapper";

export default async function ProfilePage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  return (
    <ProfileFormWrapper
      userId={session.user.id}
      userEmail={session.user.email ?? ""}
      token={session.access_token}
    />
  );
}