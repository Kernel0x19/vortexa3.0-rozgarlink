export const runtime = "edge";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import DocumentUpload from "../_components/DocumentUpload";

export default async function DocumentsPage() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) redirect("/auth/login");

  return (
    <DocumentUpload
      userId={session.user.id}
      userEmail={session.user.email ?? ""}
      token={session.access_token}
    />
  );
}