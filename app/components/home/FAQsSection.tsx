"use client";
import { useState } from "react";
import { Plus, Minus } from "lucide-react";

const FAQS = [
  {
    q: "What is the difference between eligibility and preferences?",
    a: "Eligibility is mandatory: a required qualification or residence that you must meet. Preferences, such as commute or pay, only affect ranking. RozgarLink never treats a preference as a requirement, or a requirement as a preference.",
  },
  {
    q: "Does AI decide whether I am eligible?",
    a: "No. Eligibility is checked only against the criteria stated by the opportunity. AI helps extract skills and judge how closely they correspond, and that only informs ranking. Results are decision support, not a final decision.",
  },
  {
    q: "How are skills described in different words recognised?",
    a: "RozgarLink extracts skills from profiles and listings and judges how closely they correspond, so 'wireman' and 'electrical wiring' can be treated as the same skill. A listing is no longer missed because the wording differs.",
  },
  {
    q: "Why was an opportunity marked as not eligible?",
    a: "Every ineligible result names the specific condition you do not meet, for example a required qualification or a residence rule. A role you are not eligible for never appears as an eligible match, however well your skills fit.",
  },
  {
    q: "How are eligible matches ranked?",
    a: "Only eligible opportunities are ranked. The order comes from how closely your skills fit and how well the role matches your preferences. Each match shows in plain language why it ranks where it does.",
  },
  {
    q: "How do skill gaps and learning pathways work?",
    a: "For an opportunity you are interested in, RozgarLink lists the required skills you are missing and suggests learning pathways from a catalogue supplied with the platform. It does not rely on live access to any course provider.",
  },
  {
    q: "What happens when I change my qualifications or location?",
    a: "Eligibility and rankings update immediately and visibly. Opportunities can become eligible or drop out, and the order of your matches changes to reflect your new profile.",
  },
];

export default function FAQSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section
      id="faq"
      className="border-t border-black/10 dark:border-white/8 py-16 sm:py-20 lg:py-24 transition-all duration-500"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] xl:grid-cols-[320px_1fr] gap-8 sm:gap-12 lg:gap-16">
          <div className="lg:sticky lg:top-28 lg:self-start">
            <div className="inline-flex items-center gap-2 bg-[#F97316]/10 border border-[#F97316]/30 px-3.5 py-1.5 font-mono text-[11px] text-[#F97316] dark:text-[#fdba74] mb-4 tracking-widest transition-all duration-500">
              <span className="w-1.5 h-1.5 rounded-full bg-[#F97316]" />
              FAQ
            </div>
            <h2 className="font-syne text-2xl sm:text-3xl lg:text-4xl font-extrabold text-gray-900 dark:text-[#F0F4FF] tracking-tight leading-[1.1] mb-4 transition-all duration-500">
              Questions candidates actually ask.
            </h2>
            <p className="font-mono text-sm text-gray-500 dark:text-[#6B7280] leading-relaxed transition-all duration-500">
              Not sure why a result looks the way it does? Every result lists
              the exact conditions behind it.
            </p>
          </div>

          <div className="flex flex-col">
            {FAQS.map((faq, i) => (
              <div
                key={i}
                className="border-b border-black/10 dark:border-white/8 first:border-t transition-all duration-500"
              >
                <button
                  onClick={() => setOpen(open === i ? null : i)}
                  className="w-full flex items-start justify-between gap-4 sm:gap-6 py-4 sm:py-5 text-left cursor-pointer group"
                >
                  <span
                    className={`font-syne font-bold text-sm sm:text-base transition-all duration-500 ${
                      open === i
                        ? "text-[#F97316]"
                        : "text-gray-900 dark:text-[#F0F4FF] group-hover:text-[#F97316]"
                    }`}
                  >
                    {faq.q}
                  </span>
                  <span
                    className={`shrink-0 mt-0.5 transition-all duration-500 ${
                      open === i
                        ? "text-[#F97316]"
                        : "text-gray-400 dark:text-[#6B7280]"
                    }`}
                  >
                    {open === i ? <Minus size={16} /> : <Plus size={16} />}
                  </span>
                </button>

                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    open === i ? "max-h-64 pb-4 sm:pb-5" : "max-h-0"
                  }`}
                >
                  <p className="font-mono text-xs sm:text-sm text-gray-500 dark:text-[#6B7280] leading-relaxed transition-all duration-500">
                    {faq.a}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
