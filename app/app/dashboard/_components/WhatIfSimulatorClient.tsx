"use client";

import React, { useState, useEffect, useCallback, useTransition } from "react";
import {
  Sparkles,
  Zap,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Plus,
  X,
  Building2,
  Briefcase,
  Layers,
  ArrowRight,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  Check,
  MapPin,
  ExternalLink,
  BookOpen,
  Award,
  Lock,
  Unlock,
  HelpCircle,
  Save,
  Loader2,
} from "lucide-react";
import type {
  WhatIfSimulationResponse,
  OpportunityEvaluation,
  WhatIfRequest,
} from "@/lib/api/api";
import { runWhatIfSimulation, applySimulatedProfileChanges } from "@/lib/api/api";

const SUGGESTED_SKILLS = [
  "Docker",
  "SQL",
  "AWS",
  "React",
  "FastAPI",
  "Python",
  "Kubernetes",
  "Node.js",
  "Machine Learning",
  "PostgreSQL",
  "Redis",
  "Linux",
  "PowerBI",
  "Next.js",
  "TypeScript",
  "CI/CD",
];

const PREFERRED_CITIES = [
  "Bengaluru",
  "Pune",
  "Hyderabad",
  "Delhi NCR",
  "Mumbai",
  "Chennai",
  "Remote",
];

const WORK_MODES = ["Remote", "Hybrid", "Onsite"];

interface Props {
  userId: string;
  userEmail: string;
  token?: string;
}

export default function WhatIfSimulatorClient({
  userId,
  userEmail,
  token,
}: Props) {
  const [data, setData] = useState<WhatIfSimulationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [isPending, startTransition] = useTransition();

  // ── Simulator Input Controls State ──
  const [skills, setSkills] = useState<string[]>([]);
  const [proficiencies, setProficiencies] = useState<Record<string, string>>({});
  const [newSkillInput, setNewSkillInput] = useState("");
  const [completedCourses, setCompletedCourses] = useState<string[]>([]);
  const [preferredCities, setPreferredCities] = useState<string[]>([]);
  const [preferredWorkModes, setPreferredWorkModes] = useState<string[]>([]);
  const [hypoCgpa, setHypoCgpa] = useState<number>(7.2);
  const [minStipend, setMinStipend] = useState<number>(0);

  // ── UI View Controls ──
  const [activeTab, setActiveTab] = useState<
    "all" | "unlocked" | "boosted" | "ineligible"
  >("all");
  const [expandedOppId, setExpandedOppId] = useState<string | null>(null);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyLoading, setApplyLoading] = useState(false);
  const [applySuccessMessage, setApplySuccessMessage] = useState<string | null>(
    null,
  );

  // Initial load
  const loadInitialSimulation = useCallback(async () => {
    setLoading(true);
    try {
      const res = await runWhatIfSimulation(
        {
          user_id: userId,
          skills: [],
          completed_courses: [],
          preferred_cities: [],
          preferred_work_modes: [],
        },
        userId,
        userEmail,
        token,
      );
      setData(res);
      // Sync controls with baseline snapshot
      const snap = res.active_profile_snapshot || {};
      setSkills(snap.skills || ["Python", "JavaScript"]);
      setProficiencies(snap.skill_proficiencies || {});
      setPreferredCities(snap.preferred_cities || ["Bengaluru"]);
      setPreferredWorkModes(snap.preferred_work_modes || ["Remote"]);
      setHypoCgpa(snap.cgpa || 7.2);
      setMinStipend(snap.min_stipend || 0);
    } catch (err) {
      console.error("Failed to load initial simulation:", err);
    } finally {
      setLoading(false);
    }
  }, [userId, userEmail, token]);

  useEffect(() => {
    loadInitialSimulation();
  }, [loadInitialSimulation]);

  // Recalculate simulation with current controls
  const recalculateSimulation = useCallback(
    async (
      customSkills?: string[],
      customCourses?: string[],
      customCgpa?: number,
      customCities?: string[],
      customModes?: string[],
    ) => {
      setSimulating(true);
      try {
        const payload: WhatIfRequest = {
          user_id: userId,
          skills: customSkills ?? skills,
          skill_proficiencies: proficiencies,
          completed_courses: customCourses ?? completedCourses,
          preferred_cities: customCities ?? preferredCities,
          preferred_work_modes: customModes ?? preferredWorkModes,
          hypothetical_cgpa: customCgpa ?? hypoCgpa,
          min_stipend: minStipend,
        };
        const res = await runWhatIfSimulation(payload, userId, userEmail, token);
        setData(res);
      } catch (err) {
        console.error("Recalculation failed:", err);
      } finally {
        setSimulating(false);
      }
    },
    [
      userId,
      userEmail,
      token,
      skills,
      proficiencies,
      completedCourses,
      preferredCities,
      preferredWorkModes,
      hypoCgpa,
      minStipend,
    ],
  );

  // Handle adding skill
  const handleAddSkill = (skillToAdd: string) => {
    const trimmed = skillToAdd.trim();
    if (!trimmed) return;
    if (skills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) return;
    const updated = [...skills, trimmed];
    setSkills(updated);
    setNewSkillInput("");
    recalculateSimulation(updated);
  };

  // Handle removing skill
  const handleRemoveSkill = (skillToRemove: string) => {
    const updated = skills.filter(
      (s) => s.toLowerCase() !== skillToRemove.toLowerCase(),
    );
    setSkills(updated);
    recalculateSimulation(updated);
  };

  // Handle proficiency change
  const handleProficiencyChange = (skill: string, level: string) => {
    const updated = { ...proficiencies, [skill]: level };
    setProficiencies(updated);
    recalculateSimulation(undefined, undefined, undefined, undefined, undefined);
  };

  // Handle Course toggle
  const handleToggleCourse = (courseKey: string) => {
    const updated = completedCourses.includes(courseKey)
      ? completedCourses.filter((k) => k !== courseKey)
      : [...completedCourses, courseKey];
    setCompletedCourses(updated);
    recalculateSimulation(undefined, updated);
  };

  // Handle City toggle
  const handleToggleCity = (city: string) => {
    const updated = preferredCities.includes(city)
      ? preferredCities.filter((c) => c !== city)
      : [...preferredCities, city];
    setPreferredCities(updated);
    recalculateSimulation(undefined, undefined, undefined, updated);
  };

  // Handle Work Mode toggle
  const handleToggleWorkMode = (mode: string) => {
    const updated = preferredWorkModes.includes(mode)
      ? preferredWorkModes.filter((m) => m !== mode)
      : [...preferredWorkModes, mode];
    setPreferredWorkModes(updated);
    recalculateSimulation(undefined, undefined, undefined, undefined, updated);
  };

  // Reset to original active profile snapshot
  const handleResetSimulation = () => {
    if (!data) return;
    const snap = data.active_profile_snapshot || {};
    const origSkills = snap.skills || ["Python", "JavaScript"];
    const origCourses: string[] = [];
    const origCities = snap.preferred_cities || ["Bengaluru"];
    const origModes = snap.preferred_work_modes || ["Remote"];
    const origCgpa = snap.cgpa || 7.2;

    setSkills(origSkills);
    setCompletedCourses(origCourses);
    setPreferredCities(origCities);
    setPreferredWorkModes(origModes);
    setHypoCgpa(origCgpa);
    setProficiencies(snap.skill_proficiencies || {});

    recalculateSimulation(
      origSkills,
      origCourses,
      origCgpa,
      origCities,
      origModes,
    );
  };

  // Load Scenario from 3-scenario matrix
  const handleLoadScenario = (scenarioSkills: string[]) => {
    const merged = Array.from(new Set([...skills, ...scenarioSkills]));
    setSkills(merged);
    recalculateSimulation(merged);
  };

  // Explicit confirmation to apply changes to real profile
  const handleApplyToProfile = async () => {
    setApplyLoading(true);
    try {
      const res = await applySimulatedProfileChanges(
        {
          user_id: userId,
          skills,
          skill_proficiencies: proficiencies,
          preferred_cities: preferredCities,
          preferred_work_modes: preferredWorkModes,
          confirmed: true,
        },
        userEmail,
        token,
      );
      setApplySuccessMessage(res.message);
      setShowApplyModal(false);
      setTimeout(() => setApplySuccessMessage(null), 6000);
    } catch (err) {
      console.error("Failed to apply profile changes:", err);
      alert("Error saving simulated profile to database.");
    } finally {
      setApplyLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <Loader2 size={32} className="animate-spin text-[#F97316]" />
        <p className="font-mono text-sm text-gray-400 dark:text-[#6B7280]">
          Initializing Career Impact Lab &amp; calculating counterfactual job models...
        </p>
      </div>
    );
  }

  // Filtered opportunities list based on active tab
  const filteredOpportunities = (data?.opportunities || []).filter((opp) => {
    if (activeTab === "unlocked") return opp.status_change === "NEWLY_ELIGIBLE";
    if (activeTab === "boosted") return opp.status_change === "BOOSTED";
    if (activeTab === "ineligible") return !opp.simulated_eligible;
    return true;
  });

  return (
    <div className="flex flex-col gap-6 transition-all duration-500">
      {/* ── Banner: Simulation Mode Active ──────────────────────────────────── */}
      <div className="border border-amber-500/30 bg-amber-500/8 dark:bg-amber-500/10 px-5 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 transition-all duration-500">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-500 shrink-0">
            <Sparkles size={16} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-syne font-bold text-sm text-amber-600 dark:text-amber-400">
                Career Impact Lab — Counterfactual What-If Simulator
              </span>
              <span className="font-mono text-[10px] px-2 py-0.5 border border-amber-500/30 bg-amber-500/15 text-amber-500 font-bold uppercase tracking-wider">
                Hypothetical Sandbox
              </span>
            </div>
            <p className="font-mono text-[12px] text-gray-500 dark:text-gray-400 mt-0.5">
              Simulate skills, certifications, and preferences to see live eligibility shifts across {data?.total_evaluated_opportunities || 0} real opportunities. Your active profile is untouched until explicit confirmation.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleResetSimulation}
            disabled={simulating}
            className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-white/10 font-mono text-[11px] text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 cursor-pointer transition-colors"
          >
            <RotateCcw size={12} />
            Reset to Profile
          </button>
          <button
            onClick={() => setShowApplyModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F97316] text-white font-mono text-[11px] font-bold hover:bg-[#ea580c] cursor-pointer shadow-sm transition-colors"
          >
            <Save size={12} />
            Apply Changes to Profile
          </button>
        </div>
      </div>

      {applySuccessMessage && (
        <div className="px-5 py-3 border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono text-sm flex items-center gap-2">
          <CheckCircle2 size={16} />
          {applySuccessMessage}
        </div>
      )}

      {/* ── KPI Summary Cards ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Newly Unlocked */}
        <div className="border border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-500/8 p-4 transition-all">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] text-emerald-600 dark:text-emerald-400 font-bold uppercase">
              Newly Unlocked
            </span>
            <Unlock size={15} className="text-emerald-500" />
          </div>
          <p className="font-syne text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
            +{data?.newly_unlocked_count ?? 0}
          </p>
          <p className="font-mono text-[11px] text-gray-500 dark:text-[#6B7280] mt-0.5">
            Roles previously locked by mandatory gates
          </p>
        </div>

        {/* Avg Match Score Boost */}
        <div className="border border-[#F97316]/30 bg-[#F97316]/5 dark:bg-[#F97316]/8 p-4 transition-all">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] text-[#F97316] font-bold uppercase">
              Avg Score Delta
            </span>
            <TrendingUp size={15} className="text-[#F97316]" />
          </div>
          <p className="font-syne text-2xl font-black text-[#F97316] mt-1">
            {(data?.avg_score_boost ?? 0) >= 0 ? "+" : ""}
            {data?.avg_score_boost ?? 0}%
          </p>
          <p className="font-mono text-[11px] text-gray-500 dark:text-[#6B7280] mt-0.5">
            Baseline {data?.baseline_avg_score}% → Simulated {data?.simulated_avg_score}%
          </p>
        </div>

        {/* Total Eligible Catalog */}
        <div className="border border-blue-500/30 bg-blue-500/5 dark:bg-blue-500/8 p-4 transition-all">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] text-blue-600 dark:text-blue-400 font-bold uppercase">
              Eligible Clearance
            </span>
            <ShieldCheck size={15} className="text-blue-500" />
          </div>
          <p className="font-syne text-2xl font-black text-blue-600 dark:text-blue-400 mt-1">
            {data?.simulated_eligible_count ?? 0}{" "}
            <span className="text-sm font-normal text-gray-400">
              / {data?.total_evaluated_opportunities ?? 0}
            </span>
          </p>
          <p className="font-mono text-[11px] text-gray-500 dark:text-[#6B7280] mt-0.5">
            {Math.round(
              ((data?.simulated_eligible_count ?? 0) /
                Math.max(data?.total_evaluated_opportunities ?? 1, 1)) *
                100,
            )}
            % of placement &amp; internship market
          </p>
        </div>

        {/* Remaining Critical Gaps */}
        <div className="border border-purple-500/30 bg-purple-500/5 dark:bg-purple-500/8 p-4 transition-all">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] text-purple-600 dark:text-purple-400 font-bold uppercase">
              Critical Skill Gaps
            </span>
            <AlertTriangle size={15} className="text-purple-500" />
          </div>
          <p className="font-syne text-2xl font-black text-purple-600 dark:text-purple-400 mt-1">
            {data?.remaining_critical_gaps_count ?? 0}
          </p>
          <p className="font-mono text-[11px] text-gray-500 dark:text-[#6B7280] mt-0.5">
            Unmet prerequisites across remaining roles
          </p>
        </div>
      </div>

      {/* ── Main Interactive Simulator Controls Grid ────────────────────────── */}
      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 transition-all">
        <div className="flex items-center justify-between border-b border-black/10 dark:border-white/8 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <SlidersHorizontal size={16} className="text-[#F97316]" />
            <h3 className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-base">
              Hypothetical Simulation Controls
            </h3>
          </div>
          {simulating && (
            <span className="flex items-center gap-1.5 font-mono text-[11px] text-[#F97316] animate-pulse">
              <Loader2 size={12} className="animate-spin" /> Recalculating live models...
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Skills Management (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-4">
            <div>
              <label className="font-mono text-xs text-gray-600 dark:text-gray-300 font-bold block mb-1.5">
                Simulated Technical Skills ({skills.length})
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type a skill (e.g. Docker, SQL, FastAPI, AWS)..."
                  value={newSkillInput}
                  onChange={(e) => setNewSkillInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddSkill(newSkillInput);
                    }
                  }}
                  className="flex-1 bg-white dark:bg-[#161822] border border-black/10 dark:border-white/10 px-3 py-1.5 font-mono text-xs text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:border-[#F97316]"
                />
                <button
                  type="button"
                  onClick={() => handleAddSkill(newSkillInput)}
                  className="px-3 py-1.5 bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-mono text-xs font-bold hover:bg-[#F97316] dark:hover:bg-[#F97316] dark:hover:text-white transition-colors"
                >
                  <Plus size={14} className="inline mr-1" /> Add
                </button>
              </div>

              {/* Quick Suggestion Pills */}
              <div className="flex flex-wrap items-center gap-1.5 mt-2">
                <span className="font-mono text-[10px] text-gray-400 dark:text-gray-500">
                  Quick Add:
                </span>
                {SUGGESTED_SKILLS.filter(
                  (s) => !skills.some((sk) => sk.toLowerCase() === s.toLowerCase()),
                )
                  .slice(0, 8)
                  .map((s) => (
                    <button
                      key={s}
                      onClick={() => handleAddSkill(s)}
                      className="px-2 py-0.5 border border-dashed border-gray-300 dark:border-white/15 bg-white dark:bg-[#161822] text-gray-600 dark:text-gray-400 font-mono text-[10px] hover:border-[#F97316] hover:text-[#F97316] transition-colors cursor-pointer"
                    >
                      + {s}
                    </button>
                  ))}
              </div>
            </div>

            {/* Active Skills Chips with Proficiency Selection */}
            <div className="border border-black/5 dark:border-white/5 bg-white dark:bg-[#161822] p-3 max-h-48 overflow-y-auto flex flex-wrap gap-2">
              {skills.map((s) => {
                const prof = proficiencies[s] || "Intermediate";
                return (
                  <div
                    key={s}
                    className="flex items-center gap-1 px-2.5 py-1 bg-gray-100 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-sm font-mono text-xs text-gray-800 dark:text-gray-200"
                  >
                    <span className="font-medium">{s}</span>
                    <select
                      value={prof}
                      onChange={(e) => handleProficiencyChange(s, e.target.value)}
                      className="bg-transparent border-0 text-[10px] text-[#F97316] font-bold focus:outline-none cursor-pointer pr-1"
                    >
                      <option value="Beginner">Beg</option>
                      <option value="Intermediate">Int</option>
                      <option value="Advanced">Adv</option>
                    </select>
                    <button
                      onClick={() => handleRemoveSkill(s)}
                      className="text-gray-400 hover:text-red-500 cursor-pointer ml-1"
                    >
                      <X size={12} />
                    </button>
                  </div>
                );
              })}
            </div>

            {/* Simulated Course / Certification Presets */}
            <div>
              <label className="font-mono text-xs text-gray-600 dark:text-gray-300 font-bold block mb-1.5 flex items-center gap-1.5">
                <Award size={14} className="text-[#F97316]" />
                Simulate Course &amp; Credential Completion
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {(data?.available_courses || []).map((c) => {
                  const isCompleted = completedCourses.includes(c.key);
                  return (
                    <button
                      key={c.key}
                      onClick={() => handleToggleCourse(c.key)}
                      className={`text-left p-2.5 border transition-all cursor-pointer ${
                        isCompleted
                          ? "border-[#F97316] bg-[#F97316]/8 dark:bg-[#F97316]/10 text-gray-900 dark:text-white"
                          : "border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] text-gray-600 dark:text-gray-400 hover:border-black/20"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold truncate">
                          {c.title}
                        </span>
                        {isCompleted && (
                          <CheckCircle2 size={13} className="text-[#F97316] shrink-0" />
                        )}
                      </div>
                      <div className="font-mono text-[10px] text-gray-400 mt-1 flex items-center justify-between">
                        <span>{c.provider} · {c.duration}</span>
                        <span className="text-[#F97316]">+{c.skills.length} skills</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Criteria, City & Preferences (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-4">
            {/* Hypothetical CGPA slider */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="font-mono text-xs text-gray-600 dark:text-gray-300 font-bold">
                  Hypothetical CGPA
                </label>
                <span className="font-mono text-xs text-[#F97316] font-bold">
                  {hypoCgpa.toFixed(1)} / 10.0
                </span>
              </div>
              <input
                type="range"
                min="5.0"
                max="10.0"
                step="0.1"
                value={hypoCgpa}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  setHypoCgpa(val);
                  recalculateSimulation(undefined, undefined, val);
                }}
                className="w-full accent-[#F97316] cursor-pointer"
              />
              <p className="font-mono text-[10px] text-gray-400 mt-0.5">
                Test if raising your semester CGPA unlocks strict academic cutoffs.
              </p>
            </div>

            {/* Preferred Work Modes */}
            <div>
              <label className="font-mono text-xs text-gray-600 dark:text-gray-300 font-bold block mb-1.5">
                Work Mode Preference
              </label>
              <div className="flex gap-2">
                {WORK_MODES.map((mode) => {
                  const active = preferredWorkModes.includes(mode);
                  return (
                    <button
                      key={mode}
                      onClick={() => handleToggleWorkMode(mode)}
                      className={`flex-1 py-1.5 font-mono text-xs text-center border transition-all cursor-pointer ${
                        active
                          ? "border-[#F97316] bg-[#F97316]/10 text-[#F97316] font-bold"
                          : "border-black/10 dark:border-white/10 bg-white dark:bg-[#161822] text-gray-500"
                      }`}
                    >
                      {mode}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Preferred Cities */}
            <div>
              <label className="font-mono text-xs text-gray-600 dark:text-gray-300 font-bold block mb-1.5">
                Target Cities
              </label>
              <div className="flex flex-wrap gap-1.5">
                {PREFERRED_CITIES.map((city) => {
                  const active = preferredCities.includes(city);
                  return (
                    <button
                      key={city}
                      onClick={() => handleToggleCity(city)}
                      className={`px-2.5 py-1 border font-mono text-[11px] transition-colors cursor-pointer ${
                        active
                          ? "border-blue-500 bg-blue-500/10 text-blue-600 dark:text-blue-400 font-bold"
                          : "border-black/10 dark:border-white/10 bg-white dark:bg-[#161822] text-gray-500"
                      }`}
                    >
                      {city}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Quick Summary Box */}
            <div className="border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] p-3 text-xs font-mono text-gray-600 dark:text-gray-400">
              <div className="font-bold text-gray-900 dark:text-white mb-1 flex items-center gap-1.5">
                <HelpCircle size={13} className="text-[#F97316]" />
                How Strict Eligibility Works:
              </div>
              Mandatory criteria (CGPA threshold, degree, and required core skills) act as hard gates. Opportunities with failed mandatory criteria are strictly marked Ineligible, regardless of match score.
            </div>
          </div>
        </div>
      </div>

      {/* ── 3-Scenario Comparison Matrix ───────────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-base">
              Three-Scenario Career Pathway Comparison
            </h3>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Compare alternative skill acquisition paths based on actual market demand
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(data?.scenarios || []).map((scen, idx) => (
            <div
              key={scen.scenario_id}
              className="border border-black/10 dark:border-white/8 bg-white dark:bg-[#0F1117] p-4 flex flex-col justify-between transition-all hover:border-[#F97316]/50"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-[10px] px-2 py-0.5 border border-[#F97316]/30 bg-[#F97316]/10 text-[#F97316] font-bold">
                    Scenario {String.fromCharCode(65 + idx)}
                  </span>
                  <span className="font-mono text-[11px] font-bold text-emerald-500">
                    +{scen.newly_unlocked_count} Unlocked
                  </span>
                </div>
                <h4 className="font-syne font-bold text-sm text-gray-900 dark:text-[#F0F4FF]">
                  {scen.title}
                </h4>
                <p className="font-mono text-[11px] text-gray-500 dark:text-gray-400 mt-1">
                  {scen.description}
                </p>

                <div className="mt-3 pt-3 border-t border-black/5 dark:border-white/5 space-y-1.5 font-mono text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Skills Added:</span>
                    <span className="font-bold text-gray-800 dark:text-gray-200 truncate max-w-[150px]">
                      {scen.added_skills.join(", ")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Eligible:</span>
                    <span className="font-bold text-blue-500">
                      {scen.eligible_count} Roles
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Avg Match Score:</span>
                    <span className="font-bold text-[#F97316]">
                      {scen.avg_match_score}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Remaining Gaps:</span>
                    <span className="font-bold text-purple-500">
                      {scen.remaining_mandatory_gaps_count}
                    </span>
                  </div>
                </div>

                {scen.top_unlocks.length > 0 && (
                  <div className="mt-3">
                    <span className="font-mono text-[10px] text-gray-400 block mb-1">
                      Top Unlocked Roles:
                    </span>
                    <ul className="space-y-0.5">
                      {scen.top_unlocks.map((t, i) => (
                        <li
                          key={i}
                          className="font-mono text-[10px] text-emerald-600 dark:text-emerald-400 truncate"
                        >
                          ✓ {t}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <button
                onClick={() => handleLoadScenario(scen.added_skills)}
                className="mt-4 w-full py-1.5 border border-black/10 dark:border-white/10 font-mono text-[11px] text-gray-800 dark:text-gray-200 hover:bg-[#F97316] hover:text-white dark:hover:bg-[#F97316] dark:hover:text-white transition-colors cursor-pointer"
              >
                Load Pathway into Simulator →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* ── Skill Impact Analysis Leaderboard ─────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-base">
              Market Skill Impact Leaderboard
            </h3>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Skills ranked by unlock power and ranking improvements across real database listings
            </p>
          </div>
        </div>

        <div className="border border-black/10 dark:border-white/8 bg-white dark:bg-[#0F1117] overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-black/10 dark:border-white/8 bg-gray-50 dark:bg-white/4 text-gray-500 dark:text-gray-400">
                <th className="py-2.5 px-4 font-bold">Skill</th>
                <th className="py-2.5 px-4 font-bold">Unlock Power</th>
                <th className="py-2.5 px-4 font-bold">Mandatory In</th>
                <th className="py-2.5 px-4 font-bold">Preferred In</th>
                <th className="py-2.5 px-4 font-bold">Avg Fit Boost</th>
                <th className="py-2.5 px-4 font-bold">Sample Unlocked Roles</th>
                <th className="py-2.5 px-4 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/5 dark:divide-white/5">
              {(data?.skill_impact_leaderboard || []).map((item) => (
                <tr
                  key={item.skill}
                  className="hover:bg-gray-50 dark:hover:bg-white/2 transition-colors"
                >
                  <td className="py-3 px-4 font-bold text-gray-900 dark:text-white">
                    <span className="flex items-center gap-1.5">
                      {item.skill}
                      <span
                        className={`text-[9px] px-1 py-0.2 border ${
                          item.impact_tier === "HIGH"
                            ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-500"
                            : item.impact_tier === "MEDIUM"
                              ? "border-blue-500/30 bg-blue-500/10 text-blue-500"
                              : "border-gray-400/30 text-gray-400"
                        }`}
                      >
                        {item.impact_tier}
                      </span>
                    </span>
                  </td>
                  <td className="py-3 px-4 font-bold text-emerald-500">
                    +{item.roles_unlocked_count} Roles
                  </td>
                  <td className="py-3 px-4 text-purple-600 dark:text-purple-400">
                    {item.mandatory_in_roles_count} listings
                  </td>
                  <td className="py-3 px-4 text-gray-500">
                    {item.preferred_in_roles_count} listings
                  </td>
                  <td className="py-3 px-4 text-[#F97316] font-bold">
                    +{item.average_score_boost}%
                  </td>
                  <td className="py-3 px-4 text-gray-500 dark:text-gray-400 text-[11px] max-w-[200px] truncate">
                    {item.sample_roles.join(", ") || "—"}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleAddSkill(item.skill)}
                      className="px-2.5 py-1 bg-gray-100 dark:bg-white/10 hover:bg-[#F97316] hover:text-white text-gray-800 dark:text-gray-200 transition-colors text-[10px] font-bold cursor-pointer"
                    >
                      + Simulate Skill
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Opportunity Comparison Table with Tabs ─────────────────────────── */}
      <div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-3">
          <div>
            <h3 className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-base">
              Opportunity Eligibility &amp; Ranking Impact
            </h3>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
              Real-time counterfactual status for every placement &amp; internship
            </p>
          </div>

          <div className="flex items-center gap-1 border border-black/10 dark:border-white/10 p-0.5 bg-gray-50 dark:bg-[#161822]">
            <button
              onClick={() => setActiveTab("all")}
              className={`px-3 py-1 font-mono text-xs transition-colors cursor-pointer ${
                activeTab === "all"
                  ? "bg-[#F97316] text-white font-bold"
                  : "text-gray-500 hover:text-gray-900 dark:hover:text-white"
              }`}
            >
              All ({data?.opportunities.length || 0})
            </button>
            <button
              onClick={() => setActiveTab("unlocked")}
              className={`px-3 py-1 font-mono text-xs transition-colors cursor-pointer ${
                activeTab === "unlocked"
                  ? "bg-emerald-600 text-white font-bold"
                  : "text-emerald-500 hover:text-emerald-600"
              }`}
            >
              Newly Unlocked (+{data?.newly_unlocked_count || 0})
            </button>
            <button
              onClick={() => setActiveTab("boosted")}
              className={`px-3 py-1 font-mono text-xs transition-colors cursor-pointer ${
                activeTab === "boosted"
                  ? "bg-[#F97316] text-white font-bold"
                  : "text-orange-500 hover:text-orange-600"
              }`}
            >
              Boosted (+{data?.boosted_count || 0})
            </button>
            <button
              onClick={() => setActiveTab("ineligible")}
              className={`px-3 py-1 font-mono text-xs transition-colors cursor-pointer ${
                activeTab === "ineligible"
                  ? "bg-red-600 text-white font-bold"
                  : "text-red-500 hover:text-red-600"
              }`}
            >
              Ineligible ({data?.opportunities.filter((o) => !o.simulated_eligible).length || 0})
            </button>
          </div>
        </div>

        {filteredOpportunities.length === 0 ? (
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] py-12 text-center font-mono text-xs text-gray-400">
            No opportunities in this category under current simulation parameters.
          </div>
        ) : (
          <div className="space-y-2">
            {filteredOpportunities.map((opp) => {
              const isExpanded = expandedOppId === opp.id;
              return (
                <div
                  key={opp.id}
                  className={`border transition-all bg-white dark:bg-[#0F1117] ${
                    opp.status_change === "NEWLY_ELIGIBLE"
                      ? "border-emerald-500/50 shadow-sm"
                      : opp.status_change === "BOOSTED"
                        ? "border-[#F97316]/50"
                        : "border-black/10 dark:border-white/8"
                  }`}
                >
                  {/* Card Header Row */}
                  <div
                    onClick={() =>
                      setExpandedOppId(isExpanded ? null : opp.id)
                    }
                    className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-white/2"
                  >
                    <div className="flex items-start sm:items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-sm bg-gray-100 dark:bg-white/5 border border-black/10 dark:border-white/10 flex items-center justify-center shrink-0 text-[#F97316]">
                        {opp.category === "placement" ? (
                          <Building2 size={15} />
                        ) : (
                          <Briefcase size={15} />
                        )}
                      </div>

                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="font-syne font-bold text-sm text-gray-900 dark:text-[#F0F4FF] truncate">
                            {opp.title}
                          </p>
                          <span
                            className={`font-mono text-[9px] px-1.5 py-0.5 border uppercase font-bold ${
                              opp.category === "placement"
                                ? "border-blue-500/30 bg-blue-500/10 text-blue-500"
                                : "border-emerald-500/30 bg-emerald-500/10 text-emerald-500"
                            }`}
                          >
                            {opp.category}
                          </span>
                          <span className="font-mono text-[10px] text-gray-400">
                            via {opp.source}
                          </span>
                        </div>
                        <p className="font-mono text-xs text-gray-500 dark:text-[#6B7280] mt-0.5">
                          {opp.company} · {opp.location} · {opp.work_type}
                        </p>
                      </div>
                    </div>

                    {/* Status & Score Delta Badges */}
                    <div className="flex items-center gap-3 shrink-0">
                      {/* Status pill */}
                      {opp.status_change === "NEWLY_ELIGIBLE" ? (
                        <span className="flex items-center gap-1 px-2 py-0.5 border border-emerald-500/40 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 font-mono text-[10px] font-bold">
                          <Unlock size={11} /> Unlocked
                        </span>
                      ) : opp.status_change === "BOOSTED" ? (
                        <span className="flex items-center gap-1 px-2 py-0.5 border border-[#F97316]/40 bg-[#F97316]/15 text-[#F97316] font-mono text-[10px] font-bold">
                          <TrendingUp size={11} /> +{opp.score_delta}% Boost
                        </span>
                      ) : opp.simulated_eligible ? (
                        <span className="flex items-center gap-1 px-2 py-0.5 border border-green-500/30 bg-green-500/10 text-green-500 font-mono text-[10px]">
                          <ShieldCheck size={11} /> Eligible
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2 py-0.5 border border-red-500/30 bg-red-500/10 text-red-500 font-mono text-[10px]">
                          <Lock size={11} /> Ineligible
                        </span>
                      )}

                      {/* Score Comparison */}
                      <div className="text-right font-mono">
                        <div className="text-sm font-bold text-gray-900 dark:text-white">
                          {opp.simulated_score}%
                        </div>
                        <div className="text-[10px] text-gray-400">
                          base: {opp.baseline_score}%
                        </div>
                      </div>

                      <div className="text-gray-400">
                        {isExpanded ? (
                          <ChevronUp size={16} />
                        ) : (
                          <ChevronDown size={16} />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Expanded Explainability Drawer */}
                  {isExpanded && (
                    <div className="border-t border-black/5 dark:border-white/5 bg-gray-50 dark:bg-black/20 p-4 font-mono text-xs space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Mandatory Requirements Status */}
                        <div>
                          <span className="font-bold text-gray-800 dark:text-gray-200 block mb-1">
                            Mandatory Cutoffs &amp; Prerequisites:
                          </span>
                          <ul className="space-y-1">
                            {opp.mandatory_passed.map((p, i) => (
                              <li
                                key={i}
                                className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1"
                              >
                                <Check size={12} /> {p}
                              </li>
                            ))}
                            {opp.mandatory_failed.map((f, i) => (
                              <li
                                key={i}
                                className="text-red-500 flex items-center gap-1 font-bold"
                              >
                                <X size={12} /> {f}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Skills Analysis */}
                        <div>
                          <span className="font-bold text-gray-800 dark:text-gray-200 block mb-1">
                            Skill Matching Diagnostics:
                          </span>
                          <div className="space-y-1">
                            <p className="text-gray-600 dark:text-gray-300">
                              <span className="text-emerald-500 font-bold">Matched:</span>{" "}
                              {opp.matched_skills.join(", ") || "None"}
                            </p>
                            {opp.mandatory_skill_gaps.length > 0 && (
                              <p className="text-red-500 font-bold">
                                <span>Mandatory Gaps (Blocking):</span>{" "}
                                {opp.mandatory_skill_gaps.join(", ")}
                              </p>
                            )}
                            {opp.optional_skill_gaps.length > 0 && (
                              <p className="text-amber-500">
                                <span>Preferred Gaps (Optional):</span>{" "}
                                {opp.optional_skill_gaps.slice(0, 4).join(", ")}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Action Plan */}
                      <div className="p-2.5 border border-black/10 dark:border-white/10 bg-white dark:bg-[#161822] flex items-center justify-between gap-3">
                        <div>
                          <span className="text-[10px] text-gray-400 uppercase font-bold block">
                            Explainable Recommendation:
                          </span>
                          <p className="text-gray-800 dark:text-gray-200 font-medium">
                            {opp.action_plan}
                          </p>
                        </div>
                        {opp.application_url && (
                          <a
                            href={opp.application_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1 bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-bold shrink-0 hover:bg-[#F97316] dark:hover:bg-[#F97316] dark:hover:text-white transition-colors flex items-center gap-1"
                          >
                            View Role <ExternalLink size={11} />
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ── Confirmation Modal: Apply to Real Profile ───────────────────────── */}
      {showApplyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-[#0F1117] border border-black/10 dark:border-white/15 max-w-md w-full p-6 shadow-2xl transition-all">
            <div className="flex items-center gap-3 text-[#F97316] mb-3">
              <AlertTriangle size={24} />
              <h3 className="font-syne font-bold text-lg text-gray-900 dark:text-white">
                Confirm Profile Update
              </h3>
            </div>

            <p className="font-mono text-xs text-gray-600 dark:text-gray-300 mb-4">
              You are about to permanently apply your simulated changes to your live RozgarLink profile:
            </p>

            <div className="border border-black/10 dark:border-white/10 bg-gray-50 dark:bg-[#161822] p-3 font-mono text-xs space-y-1.5 mb-5">
              <p>
                <span className="text-gray-400">Skills ({skills.length}):</span>{" "}
                <span className="font-bold text-gray-900 dark:text-white">
                  {skills.join(", ")}
                </span>
              </p>
              <p>
                <span className="text-gray-400">Work Mode:</span>{" "}
                <span className="font-bold text-gray-900 dark:text-white">
                  {preferredWorkModes.join(", ") || "Any"}
                </span>
              </p>
              <p>
                <span className="text-gray-400">Locations:</span>{" "}
                <span className="font-bold text-gray-900 dark:text-white">
                  {preferredCities.join(", ") || "Any"}
                </span>
              </p>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowApplyModal(false)}
                disabled={applyLoading}
                className="px-4 py-2 border border-black/10 dark:border-white/10 font-mono text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleApplyToProfile}
                disabled={applyLoading}
                className="px-4 py-2 bg-[#F97316] text-white font-mono text-xs font-bold hover:bg-[#ea580c] cursor-pointer flex items-center gap-1.5"
              >
                {applyLoading ? (
                  <>
                    <Loader2 size={13} className="animate-spin" /> Saving...
                  </>
                ) : (
                  <>
                    <Check size={13} /> Yes, Apply Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
