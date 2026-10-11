"use client";
import { ArrowRight } from "lucide-react";
import { redirect } from "next/navigation";

const PAINS = [
  "Applied for a role, then found it needed a qualification you don't have.",
  "Never saw a job because it said 'electrician' and your profile said 'wireman'.",
  "Were told a role was a match, with no idea why, or why not.",
  "Wanted to qualify for a role but had no idea which skill to learn next.",
];

export default function BenefitsSection() {
  return (
    <section
      id="benefits"
      className="border-t border-black/10 dark:border-white/8 py-16 sm:py-20 lg:py-24 transition-all duration-500"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 sm:gap-12 lg:gap-16 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-[#F97316]/10 border border-[#F97316]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#F97316] dark:text-[#fdba74] mb-5 sm:mb-6 tracking-widest transition-all duration-500">
              <span className="w-1.5 h-1.5 rounded-full bg-[#F97316]" />
              SOUND FAMILIAR?
            </div>

            <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500 tracking-tight leading-[1.1] mb-6 sm:mb-8">
              Every candidate deserves to see the jobs they can take.{" "}
              <span className="text-[#F97316]">Keyword search hides them.</span>
            </h2>

            <div className="flex flex-col gap-3 sm:gap-4 mb-6 sm:mb-8">
              {PAINS.map((pain, i) => (
                <div
                  key={i}
                  className="flex items-start gap-4 border-l-2 border-black/10 dark:border-white/8 pl-4 py-1 hover:border-[#F97316] transition-colors duration-500 group"
                >
                  <p className="font-mono text-xs sm:text-sm text-gray-500 dark:text-[#6B7280] group-hover:text-gray-700 dark:group-hover:text-[#a8c7fa] leading-relaxed transition-all duration-500">
                    &quot;{pain}&quot;
                  </p>
                </div>
              ))}
            </div>

            <p className="font-syne text-base sm:text-lg font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
              RozgarLink fixes this.{" "}
              <span className="text-gray-400 dark:text-[#6B7280] font-mono text-xs sm:text-sm font-normal">
                Transparently.
              </span>
            </p>
          </div>

          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-6 sm:p-8 lg:p-10 flex flex-col gap-6 sm:gap-8 transition-all duration-500">
            <div className="grid grid-cols-2 gap-3 sm:gap-4">
              {[
                { value: "Rules", label: "Decide eligibility" },
                { value: "0", label: "AI calls on eligibility" },
                { value: "100%", label: "Results explained in plain language" },
                { value: "Instant", label: "Re-ranking on profile change" },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="bg-white dark:bg-[#161822] border border-black/10 dark:border-white/8 p-3 sm:p-4 transition-all duration-500"
                >
                  <p className="font-syne text-xl sm:text-2xl font-extrabold text-[#F97316]">
                    {stat.value}
                  </p>
                  <p className="font-mono text-[10px] sm:text-[11px] text-gray-400 dark:text-[#6B7280] mt-1">
                    {stat.label}
                  </p>
                </div>
              ))}
            </div>

            <div>
              <p className="font-syne text-lg sm:text-xl font-bold text-gray-900 dark:text-[#F0F4FF] mb-2 transition-all duration-500">
                Stop missing roles you can take.
              </p>
              <p className="font-mono text-xs sm:text-sm text-gray-500 dark:text-[#6B7280] mb-5 sm:mb-6 leading-relaxed transition-all duration-500">
                Add your skills, qualifications, location and preferences.
                RozgarLink shows what you are eligible for, and why.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  className="flex items-center justify-center gap-2 px-5 sm:px-6 py-3 sm:py-3.5 bg-[#F97316] text-white font-mono text-xs sm:text-sm hover:bg-[fdba74] cursor-pointer group flex-1 transition-all duration-500"
                  onClick={() => redirect("/auth/signup")}
                >
                  Create your profile
                  <ArrowRight
                    size={15}
                    className="group-hover:translate-x-0.5 transition-transform duration-300"
                  />
                </button>
                <button className="flex items-center justify-center gap-2 px-5 sm:px-6 py-3 sm:py-3.5 border border-black/10 dark:border-white/8 text-gray-500 dark:text-[#6B7280] font-mono text-xs sm:text-sm hover:border-black/30 dark:hover:border-white/20 hover:text-gray-900 dark:hover:text-[#F0F4FF] cursor-pointer transition-all duration-500">
                  See how it works
                </button>
              </div>
            </div>

            <p className="font-mono text-[10px] sm:text-[11px] text-gray-400 dark:text-[#6B7280] border-t border-black/10 dark:border-white/8 pt-4 transition-all duration-500">
              Eligibility follows each opportunity's stated criteria · Decision
              support only
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
