"use client";
import { useState } from "react";
import {
  ShieldCheck,
  Languages,
  ListOrdered,
  MessageSquare,
  Map,
  RefreshCw,
  CheckCircle,
} from "lucide-react";

type Feature = {
  id: string;
  icon: React.ReactNode;
  label: string;
  tag: string;
  heading: string;
  description: string;
  points: string[];
  terminal: {
    prompt: string;
    type: "command" | "success" | "muted" | "error";
  }[];
};

const FEATURES: Feature[] = [
  {
    id: "eligibility",
    icon: <ShieldCheck size={18} />,
    label: "Eligibility rules",
    tag: "Rule-based",
    heading: "Only the roles you can formally take",
    description:
      "Each opportunity states its own mandatory criteria, such as qualification and residence. The engine checks those first and sets aside anything you don't meet, however well your skills fit.",
    points: [
      "Criteria come from the opportunity, never from AI",
      "Ineligible roles never appear as eligible matches",
      "Every failed condition is named",
    ],
    terminal: [
      { prompt: "Opportunity: Solar Technician Trainee", type: "command" },
      { prompt: "Checking qualification · residence", type: "command" },
      { prompt: "✓ Residence: Maharashtra — met", type: "success" },
      {
        prompt: "✗ Qualification: Diploma/ITI (Electrical) — not met",
        type: "error",
      },
      { prompt: "Not eligible · excluded from ranking", type: "muted" },
    ],
  },
  {
    id: "skills",
    icon: <Languages size={18} />,
    label: "Skill matching",
    tag: "AI-assisted",
    heading: "Same skill, different words",
    description:
      "Listings and profiles rarely use the same wording. AI extracts skills and judges how closely they correspond, so a good fit isn't hidden by a keyword mismatch. This informs ranking only.",
    points: [
      "'Wireman' and 'electrical wiring' recognised as close",
      "Extracts skills from free-text descriptions",
      "Never used to decide eligibility",
    ],
    terminal: [
      {
        prompt: "Reading profile: 'house wiring, fan repair'",
        type: "command",
      },
      { prompt: "Matching against listed required skills...", type: "command" },
      {
        prompt: "✓ 'house wiring' ≈ 'electrical installation' (close)",
        type: "success",
      },
      {
        prompt: "✓ 'fan repair' ≈ 'appliance servicing' (partial)",
        type: "success",
      },
      { prompt: "Used for ranking only, not eligibility", type: "muted" },
    ],
  },
  {
    id: "ranking",
    icon: <ListOrdered size={18} />,
    label: "Preference ranking",
    tag: "Eligible only",
    heading: "Preferences sort the list. They never filter it.",
    description:
      "Commute, pay and other preferences only change the order of opportunities you are already eligible for. A missed preference lowers a rank; it never hides a role.",
    points: [
      "Ranks only eligible opportunities",
      "Combines skill fit with your preferences",
      "A missed preference lowers rank, never removes the role",
    ],
    terminal: [
      { prompt: "Ranking 9 eligible opportunities", type: "command" },
      { prompt: "Weighing skill fit · commute · pay", type: "command" },
      {
        prompt: "✓ #1 Electrical Apprentice — strong fit, 6 km",
        type: "success",
      },
      {
        prompt: "✓ #2 Solar Helper — good fit, pay below preference",
        type: "success",
      },
      { prompt: "Missed preferences lower rank, never hide", type: "muted" },
    ],
  },
  {
    id: "explain",
    icon: <MessageSquare size={18} />,
    label: "Plain-language reasons",
    tag: "Explained",
    heading: "Every result says why",
    description:
      "For an eligible match, see why it ranks where it does. For anything else, see the specific condition you don't meet. No black-box scores.",
    points: [
      "Reasons for every eligible match's rank",
      "The exact failed condition for every ineligible role",
      "Written in plain language, not scores",
    ],
    terminal: [
      { prompt: "Why is 'Electrical Apprentice' ranked #1?", type: "command" },
      { prompt: "Building explanation...", type: "command" },
      { prompt: "✓ Meets all 3 eligibility conditions", type: "success" },
      { prompt: "✓ 4 of 5 required skills match", type: "success" },
      {
        prompt: "✗ Other role: needs 12th pass — not on profile",
        type: "error",
      },
    ],
  },
  {
    id: "gaps",
    icon: <Map size={18} />,
    label: "Skill gaps & pathways",
    tag: "Catalogue-based",
    heading: "See what's missing and how to close it",
    description:
      "Pick an opportunity you're interested in. RozgarLink compares its required skills with yours and suggests learning pathways from the catalogue supplied with the platform. No live course provider is needed.",
    points: [
      "Gap list for each opportunity you choose",
      "Pathways drawn from a supplied catalogue",
      "No dependence on live course sites",
    ],
    terminal: [
      { prompt: "Interested in: Solar Technician Trainee", type: "command" },
      { prompt: "Comparing required skills with profile...", type: "command" },
      { prompt: "✓ 3 of 4 required skills covered", type: "success" },
      { prompt: "⚠ Gap: PV panel installation", type: "muted" },
      {
        prompt: "✓ Catalogue pathway: Solar PV Basics",
        type: "success",
      },
    ],
  },
  {
    id: "live",
    icon: <RefreshCw size={18} />,
    label: "Live updates",
    tag: "Instant",
    heading: "Change your profile, watch results change",
    description:
      "Update a qualification or your location and eligibility is re-checked straight away. Rankings reorder in front of you. Results are decision support; the opportunity's stated criteria always apply.",
    points: [
      "Qualification or location edits re-check eligibility",
      "Rankings reorder visibly",
      "Criteria used are always those stated by the opportunity",
    ],
    terminal: [
      {
        prompt: "Qualification updated: 12th → Diploma (Electrical)",
        type: "command",
      },
      { prompt: "Re-checking eligibility...", type: "command" },
      { prompt: "✓ 4 more opportunities now eligible", type: "success" },
      { prompt: "✓ Rankings reordered", type: "success" },
      { prompt: "Decision support only", type: "muted" },
    ],
  },
];

const termColor = (type: string) => {
  if (type === "error") return "text-red-500 dark:text-red-400";
  if (type === "success") return "text-green-500 dark:text-green-400";
  if (type === "muted") return "text-yellow-600 dark:text-yellow-400";
  return "text-blue-600 dark:text-[#a8c7fa]";
};

export default function FeaturesSection() {
  const [active, setActive] = useState(FEATURES[0].id);
  const feature = FEATURES.find((f) => f.id === active)!;

  return (
    <section
      id="features"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10 py-16 sm:py-20 lg:py-24 transition-all duration-500"
    >
      <div className="mb-8 sm:mb-12">
        <div className="inline-flex items-center gap-2 bg-[#0C65D2]/10 border border-[#0C65D2]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#0C65D2] dark:text-[#6fa8f5] mb-4 tracking-widest transition-all duration-500">
          <span className="w-1.5 h-1.5 rounded-full bg-[#0C65D2]" />
          WHAT ROZGARLINK DOES
        </div>
        <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] tracking-tight transition-all duration-500">
          Six capabilities. One engine.
        </h2>
        <p className="mt-3 text-gray-500 dark:text-[#6B7280] font-mono text-sm max-w-lg transition-all duration-500">
          Eligibility is decided by rules. AI only helps with skills and
          ranking. Together they show what you can take, and why.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] xl:grid-cols-[280px_1fr] gap-4 sm:gap-6">
        <div className="flex flex-row lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0 scrollbar-hide">
          {FEATURES.map((f) => (
            <button
              key={f.id}
              onClick={() => setActive(f.id)}
              className={`flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2.5 sm:py-3 text-left transition-all duration-200 cursor-pointer border-b-2 lg:border-b-0 lg:border-l-2 shrink-0 lg:shrink ${
                active === f.id
                  ? "border-[#0C65D2] bg-[#0C65D2]/8 dark:bg-[#0C65D2]/10 text-[#0C65D2]"
                  : "border-transparent text-gray-500 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] hover:bg-gray-50 dark:hover:bg-white/4 transition-all duration-500"
              }`}
            >
              <span
                className={`shrink-0 ${active === f.id ? "text-[#0C65D2]" : ""}`}
              >
                {f.icon}
              </span>
              <span className="font-mono text-xs sm:text-sm whitespace-nowrap lg:whitespace-normal">
                {f.label}
              </span>
            </button>
          ))}
        </div>

        <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] overflow-hidden transition-all duration-500">
          <div className="bg-white dark:bg-[#161822] border-b border-black/10 dark:border-white/8 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-3 transition-all duration-500">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <div className="w-7 h-7 sm:w-8 sm:h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0">
                {feature.icon}
              </div>
              <div className="min-w-0">
                <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-xs sm:text-sm leading-tight">
                  {feature.heading}
                </p>
              </div>
            </div>
            <span className="font-mono text-[10px] bg-[#0C65D2]/10 text-[#0C65D2] dark:text-[#6fa8f5] border border-[#0C65D2]/20 px-2 sm:px-2.5 py-1 tracking-widest shrink-0 transition-all duration-500">
              {feature.tag}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-0">
            <div className="p-4 sm:p-6 md:border-r border-b md:border-b-0 border-black/10 dark:border-white/8 transition-all duration-500">
              <p className="text-gray-600 dark:text-[#6B7280] text-xs sm:text-sm leading-relaxed mb-4 sm:mb-6 transition-all duration-500">
                {feature.description}
              </p>
              <ul className="flex flex-col gap-2.5 sm:gap-3">
                {feature.points.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 sm:gap-2.5">
                    <span className="text-[#0C65D2] mt-0.5 shrink-0">
                      <CheckCircle size={14} />
                    </span>
                    <span className="font-mono text-[11px] sm:text-[12px] text-gray-700 dark:text-[#a8c7fa] transition-all duration-500">
                      {pt}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 sm:p-6">
              <div className="border border-black/10 dark:border-white/8 overflow-hidden h-full transition-all duration-500">
                <div className="bg-gray-100 dark:bg-[#161822] px-3 sm:px-4 py-2 flex items-center gap-2 border-b border-black/10 dark:border-white/8 transition-all duration-500">
                  <span className="w-2 h-2 rounded-full bg-[#ff5f57]" />
                  <span className="w-2 h-2 rounded-full bg-[#febc2e]" />
                  <span className="w-2 h-2 rounded-full bg-[#28c840]" />
                  <span className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] ml-auto transition-all duration-500">
                    engine output
                  </span>
                </div>
                <div className="p-3 sm:p-4 font-mono text-[11px] sm:text-[12px] leading-loose overflow-x-auto">
                  {feature.terminal.map((line, i) => (
                    <div key={i} className="flex items-baseline gap-2">
                      <span className="text-[#0C65D2] select-none shrink-0">
                        ›
                      </span>
                      <span
                        className={`${termColor(line.type)} whitespace-nowrap sm:whitespace-normal`}
                      >
                        {line.prompt}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
