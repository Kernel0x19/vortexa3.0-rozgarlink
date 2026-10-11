export const runtime = "edge";
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import ProfileFormWrapper from "../_components/ProfileFormWrapper";

export default async function ProfilePage() {
  const supabase = await createClient();

  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();
  if (!user || error) redirect("/auth/login");

  const {
    data: { session },
  } = await supabase.auth.getSession();
  const token = session?.access_token ?? "";

  return (
    <ProfileFormWrapper
      userId={user.id}
      userEmail={user.email ?? ""}
      token={token}
    />
  );
}
