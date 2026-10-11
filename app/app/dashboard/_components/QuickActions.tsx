import Link from "next/link";
import {
  Search,
  BookOpen,
  User,
  ClipboardList,
  ArrowRight,
  Sparkles,
} from "lucide-react";

const actions = [
  {
    href: "/dashboard/placements",
    label: "Explore placements",
    icon: <Search size={15} />,
  },
  {
    href: "/dashboard/what-if",
    label: "What-If Simulator",
    icon: <Sparkles size={15} />,
  },
  {
    href: "/dashboard/profile",
    label: "Update profile",
    icon: <User size={15} />,
  },
  {
    href: "/dashboard/applications",
    label: "My applications",
    icon: <ClipboardList size={15} />,
  },
];

export default function QuickActions() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 transition-all duration-500">
      {actions.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className="flex items-center justify-between gap-2 px-4 py-3 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] hover:border-[#F97316]/40 hover:bg-[#F97316]/4 dark:hover:bg-[#F97316]/8 transition-all duration-500 group"
        >
          <div className="flex items-center gap-2 font-mono text-[14px] text-gray-600 dark:text-[#6B7280] group-hover:text-[#F97316] transition-all duration-500">
            <span className="text-[#F97316]">{action.icon}</span>
            {action.label}
          </div>
          <ArrowRight
            size={13}
            className="text-gray-300 dark:text-white/20 group-hover:text-[#F97316] transition-colors duration-500"
          />
        </Link>
      ))}
    </div>
  );
}
