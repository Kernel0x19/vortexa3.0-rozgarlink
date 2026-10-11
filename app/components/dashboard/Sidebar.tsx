"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import {
  LayoutDashboard,
  Briefcase,
  BookOpen,
  ClipboardList,
  Search,
  Bell,
  User,
  LogOut,
  BarChart3,
  Trophy,
  FlaskConical,
  MessageSquare,
} from "lucide-react";
import { useEffect, useState } from "react";

const NAV = [
  {
    href: "/dashboard",
    icon: <LayoutDashboard size={17} />,
    label: "Dashboard",
  },
  {
    href: "/dashboard/search",
    icon: <Search size={17} />,
    label: "Opportunities",
  },
  {
    href: "/dashboard/internships",
    icon: <Briefcase size={17} />,
    label: "Internships",
  },
  {
    href: "/dashboard/hackathons",
    icon: <Trophy size={17} />,
    label: "Hackathons",
  },
  {
    href: "/dashboard/chat",
    icon: <MessageSquare size={17} />,
    label: "Chat",
  },
  {
    href: "/dashboard/matches",
    icon: <Briefcase size={17} />,
    label: "My Matches",
  },
  {
    href: "/dashboard/applications",
    icon: <ClipboardList size={17} />,
    label: "Applications",
  },
  {
    href: "/dashboard/skill-gaps",
    icon: <BookOpen size={17} />,
    label: "Skill Gaps",
  },
  {
    href: "/dashboard/profile",
    icon: <User size={17} />,
    label: "My Profile",
  },
  {
    href: "/dashboard/notifications",
    icon: <Bell size={17} />,
    label: "Notifications",
  },
  { href: "/dashboard/admin", icon: <BarChart3 size={17} />, label: "Admin" },
  {
    href: "/dashboard/eval",
    icon: <FlaskConical size={17} />,
    label: "AI Quality",
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      if (!session?.user?.id) {
        setLoading(false);
        return;
      }
      const { data } = await supabase
        .from("profiles")
        .select("is_admin")
        .eq("id", session.user.id)
        .single();
      setIsAdmin(data?.is_admin === true);
      setLoading(false);
    });
  }, []);

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    window.location.href = "/auth/login";
  };

  return (
    <aside className="hidden lg:flex flex-col w-60 shrink-0 border-r border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] min-h-screen fixed top-0 left-0 bottom-0 transition-all duration-500">
      <div className="px-6 py-5 border-b border-black/10 dark:border-white/8 transition-all duration-500">
        <div
          className="flex items-center gap-2 hover:cursor-pointer"
          onClick={() => redirect("/")}
        >
          <Image
            className="transition-all duration-500"
            src={"/LogoDark-t.png"}
            width={50}
            height={50}
            loading="eager"
            alt="RozgarLink Logo"
          />
          <span className="font-syne text-xl sm:text-2xl font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
            Rozgar<span className="text-[#F97316]">Link</span>
          </span>
        </div>
      </div>
      <nav className="flex flex-col gap-1 px-3 py-4 flex-1">
        {NAV.map((item) => {
          const isAdminRoute =
            item.href.includes("/admin") || item.href.includes("/eval");
          if (isAdminRoute && (loading || !isAdmin)) return null;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 font-mono text-sm transition-all duration-500 border-l-2 ${
                isActive
                  ? "border-[#F97316] bg-[#F97316]/8 dark:bg-[#F97316]/10 text-[#F97316]"
                  : "border-transparent text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] hover:bg-gray-100 dark:hover:bg-white/4"
              }`}
            >
              {item.icon}
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="px-3 py-4 border-t border-black/10 dark:border-white/8 transition-all duration-500">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/8 border-l-2 border-transparent transition-all duration-500 cursor-pointer"
        >
          <LogOut size={17} />
          Log out
        </button>
      </div>
    </aside>
  );
}
