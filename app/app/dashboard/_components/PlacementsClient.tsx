"use client";

import React, { useState, useCallback, useTransition, useEffect } from "react";
import {
  Briefcase,
  Search,
  BookmarkPlus,
  ExternalLink,
  MapPin,
  Banknote,
  Wifi,
  Building2,
  SlidersHorizontal,
  X,
  Loader2,
  CheckCircle,
  Star,
  Clock,
  ChevronDown,
  ChevronUp,
  Zap,
} from "lucide-react";
import type { JobMatchResult } from "@/lib/api/api";
import { getJobRecommendations, saveJob } from "@/lib/api/api";

// ── Filter state ──────────────────────────────────────────────────────────────

interface Filters {
  work_type: string;
  salary_min: string;
  experience: string;
  location: string;
  source: string;
}

const EMPTY_FILTERS: Filters = {
  work_type: "",
  salary_min: "",
  experience: "",
  location: "",
  source: "",
};

interface Props {
  userId: string;
  userEmail: string;
  token?: string;
}

// ── Platform metadata ─────────────────────────────────────────────────────────

const PLATFORMS: Record<string, { label: string; color: string; bg: string }> = {
  naukri: {
    label: "Naukri",
    color: "text-[#ff7555]",
    bg: "bg-[#ff7555]/8 border-[#ff7555]/20",
  },
  linkedin: {
    label: "LinkedIn",
    color: "text-[#0077b5]",
    bg: "bg-[#0077b5]/8 border-[#0077b5]/20",
  },
  wellfound: {
    label: "Wellfound",
    color: "text-[#ef4444]",
    bg: "bg-[#ef4444]/8 border-[#ef4444]/20",
  },
  internshala: {
    label: "Internshala",
    color: "text-[#007bff]",
    bg: "bg-[#007bff]/8 border-[#007bff]/20",
  },
};

function platformMeta(src: string) {
  return (
    PLATFORMS[src.toLowerCase()] ?? {
      label: src.toUpperCase(),
      color: "text-gray-500",
      bg: "bg-gray-100/50 border-gray-200 dark:bg-white/5 dark:border-white/10",
    }
  );
}

function SourceBadge({ source }: { source: string }) {
  const { label, color, bg } = platformMeta(source);
  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 border font-mono text-[9px] font-bold tracking-wide ${color} ${bg}`}
    >
      {label}
    </span>
  );
}

function FilterPill({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="flex items-center gap-1 px-2 py-0.5 bg-[#F97316]/10 border border-[#F97316]/20 font-mono text-[11px] text-[#F97316]">
      {label}
      <button type="button" onClick={onRemove} className="hover:text-red-500">
        <X size={10} />
      </button>
    </span>
  );
}

// ── Score badge ───────────────────────────────────────────────────────────────

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 85
      ? "bg-emerald-500/15 text-emerald-500 border-emerald-500/20"
      : score >= 70
      ? "bg-blue-500/15 text-blue-500 border-blue-500/20"
      : "bg-gray-500/10 text-gray-400 border-gray-500/20";
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 border font-mono text-[11px] font-bold ${color}`}
    >
      <Star size={9} />
      {score}% match
    </span>
  );
}

// ── Work-type badge ───────────────────────────────────────────────────────────

function WorkTypeBadge({ type }: { type: string | null }) {
  const t = (type || "onsite").toLowerCase();
  const map: Record<string, { icon: React.ReactNode; cls: string }> = {
    remote: {
      icon: <Wifi size={10} />,
      cls: "bg-violet-500/10 text-violet-400 border-violet-500/20",
    },
    hybrid: {
      icon: <Zap size={10} />,
      cls: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    },
    onsite: {
      icon: <Building2 size={10} />,
      cls: "bg-sky-500/10 text-sky-400 border-sky-500/20",
    },
  };
  const { icon, cls } = map[t] ?? map["onsite"];
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 border font-mono text-[10px] capitalize ${cls}`}
    >
      {icon}
      {t}
    </span>
  );
}

// ── Salary display ────────────────────────────────────────────────────────────

function salaryLabel(job: JobMatchResult["opportunity"]): string {
  if (job.salary_lpa) return `₹${job.salary_lpa} LPA`;
  const mn = job.amount_min ? Math.round(job.amount_min / 1000) : null;
  const mx = job.amount_max ? Math.round(job.amount_max / 1000) : null;
  if (mn && mx) return `₹${mn}k–₹${mx}k/mo`;
  if (mx) return `Up to ₹${mx}k/mo`;
  return "Negotiable";
}

// ── Job card ──────────────────────────────────────────────────────────────────

function JobCard({
  match,
  onSave,
  saved,
  saving,
}: {
  match: JobMatchResult;
  onSave: () => void;
  saved: boolean;
  saving: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const job = match.opportunity;

  return (
    <div className="group relative border border-black/8 dark:border-white/8 bg-white dark:bg-[#0F1117] hover:border-[#F97316]/30 transition-all duration-300 hover:shadow-lg hover:shadow-[#F97316]/5">
      {/* top stripe */}
      <div className="h-0.5 bg-gradient-to-r from-transparent via-[#F97316]/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="p-5">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-1.5 mb-1.5">
              <SourceBadge source={job.source} />
              <WorkTypeBadge type={job.work_type} />
              <ScoreBadge score={match.match_score} />
            </div>
            <h3 className="font-mono font-bold text-sm text-gray-900 dark:text-[#F0F4FF] leading-snug line-clamp-2">
              {job.title}
            </h3>
            {job.company && (
              <p className="font-mono text-[11px] text-[#F97316] mt-0.5 flex items-center gap-1">
                <Building2 size={10} />
                {job.company}
              </p>
            )}
          </div>
          <div className="flex flex-col gap-1.5 shrink-0">
            <button
              onClick={onSave}
              disabled={saved || saving}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 font-mono text-[11px] border transition-all duration-200 ${
                saved
                  ? "border-emerald-500/30 text-emerald-500 bg-emerald-500/8 cursor-default"
                  : "border-[#F97316]/30 text-[#F97316] hover:bg-[#F97316]/8 cursor-pointer"
              }`}
              title={saved ? "Saved" : "Save job"}
            >
              {saving ? (
                <Loader2 size={11} className="animate-spin" />
              ) : saved ? (
                <CheckCircle size={11} />
              ) : (
                <BookmarkPlus size={11} />
              )}
              {saved ? "Saved" : "Save"}
            </button>
            {job.application_url && (
              <a
                href={job.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-2.5 py-1.5 font-mono text-[11px] border border-gray-200 dark:border-white/10 text-gray-600 dark:text-gray-400 hover:border-[#F97316]/30 hover:text-[#F97316] transition-all duration-200"
              >
                <ExternalLink size={11} />
                Apply
              </a>
            )}
          </div>
        </div>

        {/* Meta row */}
        <div className="flex flex-wrap gap-3 mb-3 font-mono text-[11px] text-gray-500 dark:text-[#6B7280]">
          {job.location && (
            <span className="flex items-center gap-1">
              <MapPin size={10} />
              {job.location}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Banknote size={10} />
            {salaryLabel(job)}
          </span>
          {job.experience && (
            <span className="flex items-center gap-1">
              <Clock size={10} />
              {job.experience}
            </span>
          )}
          {job.deadline && (
            <span className="flex items-center gap-1 text-amber-500/80">
              <Clock size={10} />
              Apply by {new Date(job.deadline).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}
            </span>
          )}
        </div>

        {/* Tags */}
        {job.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {job.tags.slice(0, 6).map((t) => (
              <span
                key={t}
                className="px-1.5 py-0.5 bg-gray-100 dark:bg-white/5 border border-black/8 dark:border-white/8 font-mono text-[10px] text-gray-600 dark:text-gray-400"
              >
                {t}
              </span>
            ))}
          </div>
        )}

        {/* Description toggle */}
        {job.description && (
          <>
            <button
              className="flex items-center gap-1 font-mono text-[11px] text-gray-400 hover:text-[#F97316] transition-colors"
              onClick={() => setExpanded((e) => !e)}
            >
              {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {expanded ? "Hide" : "About this role"}
            </button>
            {expanded && (
              <p className="mt-2 font-mono text-[11px] text-gray-500 dark:text-[#6B7280] leading-relaxed border-t border-black/5 dark:border-white/5 pt-2">
                {job.description}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function PlacementsClient({ userId, userEmail, token }: Props) {
  const [matches, setMatches] = useState<JobMatchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [savingId, setSavingId] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  const load = useCallback(
    async (q: string, f: Filters) => {
      setLoading(true);
      setError(null);
      try {
        const res = await getJobRecommendations(
          userId,
          userEmail,
          {
            query: q || undefined,
            location: f.location || undefined,
            work_type: f.work_type || undefined,
            salary_min: f.salary_min ? parseFloat(f.salary_min) : undefined,
            experience: f.experience || undefined,
            source: f.source || undefined,
            limit: 30,
          },
          token,
        );
        setMatches(res.matches ?? []);
        setTotal(res.total ?? 0);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [userId, userEmail, token],
  );

  useEffect(() => {
    load("", EMPTY_FILTERS);
  }, [load]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    startTransition(() => load(query, filters));
  };

  const handleFilter = (key: keyof Filters, val: string) => {
    const next = { ...filters, [key]: val };
    setFilters(next);
    startTransition(() => load(query, next));
  };

  const clearFilter = (key: keyof Filters) => handleFilter(key, "");
  const clearAll = () => {
    setFilters(EMPTY_FILTERS);
    setQuery("");
    startTransition(() => load("", EMPTY_FILTERS));
  };

  const handleSave = async (id: string) => {
    setSavingId(id);
    try {
      await saveJob(userId, id, userEmail, token);
      setSavedIds((prev) => new Set(prev).add(id));
    } catch {
      /* ignore */
    } finally {
      setSavingId(null);
    }
  };

  const activePills = Object.entries(filters).filter(([, v]) => v);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="font-mono font-bold text-xl text-gray-900 dark:text-[#F0F4FF] flex items-center gap-2">
            <Briefcase size={20} className="text-[#F97316]" />
            Placement Jobs
          </h1>
          <p className="font-mono text-[12px] text-gray-500 dark:text-[#6B7280] mt-0.5">
            Full-time roles matched to your profile across Naukri, LinkedIn &amp; Wellfound
          </p>
        </div>
        <div className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
          {!loading && <span>{total} jobs found</span>}
        </div>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search jobs — 'React developer remote', 'ML engineer'…"
            className="w-full pl-8 pr-3 py-2.5 font-mono text-sm bg-transparent border border-black/10 dark:border-white/10 text-gray-900 dark:text-[#F0F4FF] placeholder-gray-400 focus:outline-none focus:border-[#F97316]/50 transition-colors"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2.5 bg-[#F97316] text-white font-mono text-sm hover:bg-[#ea6c0a] transition-colors"
        >
          Search
        </button>
        <button
          type="button"
          onClick={() => setShowFilters((s) => !s)}
          className={`px-3 py-2.5 border font-mono text-sm transition-colors ${
            showFilters
              ? "border-[#F97316] text-[#F97316] bg-[#F97316]/8"
              : "border-black/10 dark:border-white/10 text-gray-500 dark:text-gray-400 hover:border-[#F97316]/30"
          }`}
        >
          <SlidersHorizontal size={14} />
        </button>
      </form>

      {/* Filter panel */}
      {showFilters && (
        <div className="border border-black/8 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          <div>
            <label className="block font-mono text-[10px] text-gray-400 mb-1 uppercase tracking-wider">
              Work Type
            </label>
            <select
              value={filters.work_type}
              onChange={(e) => handleFilter("work_type", e.target.value)}
              className="w-full font-mono text-xs py-1.5 px-2 border border-black/10 dark:border-white/10 bg-white dark:bg-[#08090E] text-gray-700 dark:text-gray-300 focus:outline-none focus:border-[#F97316]/50"
            >
              <option value="">Any</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite</option>
            </select>
          </div>
          <div>
            <label className="block font-mono text-[10px] text-gray-400 mb-1 uppercase tracking-wider">
              Min CTC (LPA)
            </label>
            <select
              value={filters.salary_min}
              onChange={(e) => handleFilter("salary_min", e.target.value)}
              className="w-full font-mono text-xs py-1.5 px-2 border border-black/10 dark:border-white/10 bg-white dark:bg-[#08090E] text-gray-700 dark:text-gray-300 focus:outline-none focus:border-[#F97316]/50"
            >
              <option value="">Any</option>
              <option value="4">4+ LPA</option>
              <option value="6">6+ LPA</option>
              <option value="8">8+ LPA</option>
              <option value="10">10+ LPA</option>
              <option value="15">15+ LPA</option>
            </select>
          </div>
          <div>
            <label className="block font-mono text-[10px] text-gray-400 mb-1 uppercase tracking-wider">
              Experience
            </label>
            <select
              value={filters.experience}
              onChange={(e) => handleFilter("experience", e.target.value)}
              className="w-full font-mono text-xs py-1.5 px-2 border border-black/10 dark:border-white/10 bg-white dark:bg-[#08090E] text-gray-700 dark:text-gray-300 focus:outline-none focus:border-[#F97316]/50"
            >
              <option value="">Any</option>
              <option value="fresher">Fresher</option>
              <option value="0-1">0–1 yr</option>
              <option value="1-3">1–3 yr</option>
              <option value="3+">3+ yr</option>
            </select>
          </div>
          <div>
            <label className="block font-mono text-[10px] text-gray-400 mb-1 uppercase tracking-wider">
              Location
            </label>
            <input
              type="text"
              placeholder="e.g. Bangalore"
              value={filters.location}
              onChange={(e) => handleFilter("location", e.target.value)}
              className="w-full font-mono text-xs py-1.5 px-2 border border-black/10 dark:border-white/10 bg-white dark:bg-[#08090E] text-gray-700 dark:text-gray-300 focus:outline-none focus:border-[#F97316]/50"
            />
          </div>
          <div>
            <label className="block font-mono text-[10px] text-gray-400 mb-1 uppercase tracking-wider">
              Platform
            </label>
            <select
              value={filters.source}
              onChange={(e) => handleFilter("source", e.target.value)}
              className="w-full font-mono text-xs py-1.5 px-2 border border-black/10 dark:border-white/10 bg-white dark:bg-[#08090E] text-gray-700 dark:text-gray-300 focus:outline-none focus:border-[#F97316]/50"
            >
              <option value="">All</option>
              <option value="naukri">Naukri</option>
              <option value="linkedin">LinkedIn</option>
              <option value="wellfound">Wellfound</option>
            </select>
          </div>
        </div>
      )}

      {/* Active filter pills */}
      {activePills.length > 0 && (
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="font-mono text-[11px] text-gray-400">Active:</span>
          {activePills.map(([key, val]) => (
            <FilterPill
              key={key}
              label={`${key.replace("_", " ")}: ${val}`}
              onRemove={() => clearFilter(key as keyof Filters)}
            />
          ))}
          <button
            onClick={clearAll}
            className="font-mono text-[11px] text-gray-400 hover:text-red-400 underline transition-colors"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center py-20 gap-3">
          <Loader2 size={18} className="animate-spin text-[#F97316]" />
          <span className="font-mono text-sm text-gray-400">Loading jobs…</span>
        </div>
      ) : error ? (
        <div className="border border-red-500/20 bg-red-500/5 p-6 text-center font-mono text-sm text-red-400">
          {error}
        </div>
      ) : matches.length === 0 ? (
        <div className="border border-black/8 dark:border-white/8 p-12 text-center">
          <Briefcase size={28} className="mx-auto mb-3 text-gray-300 dark:text-gray-600" />
          <p className="font-mono text-sm text-gray-400">
            No jobs found. Try adjusting your filters or run the connectors from Admin.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {matches.map((m) => (
            <JobCard
              key={m.opportunity.id}
              match={m}
              onSave={() => handleSave(m.opportunity.id)}
              saved={savedIds.has(m.opportunity.id)}
              saving={savingId === m.opportunity.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
