export const runtime = "edge";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import AdminDashboard from "../_components/AdminDashboard";

export default async function AdminPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  const { user } = session;
  const token = session.access_token;

  const { data: profile } = await supabase
    .from("profiles")
    .select("is_admin")
    .eq("id", user.id)
    .single();

  if (!profile?.is_admin) {
    return (
      <div className="flex flex-col items-center py-20 gap-3">
        <p className="font-mono text-[14px] text-red-500 font-bold">Access Denied</p>
        <p className="font-mono text-[12px] text-gray-400">
          Admin privileges required to access this page.
        </p>
      </div>
    );
  }

  return <AdminDashboard userId={user.id} userEmail={user.email ?? ""} token={token} />;
}