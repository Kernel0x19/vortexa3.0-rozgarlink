"use client";

import { useState, useEffect } from "react";
import {
  GraduationCap,
  Search,
  BookmarkPlus,
  ExternalLink,
  CheckCircle,
  XCircle,
  Inbox,
  Link as LinkIcon,
} from "lucide-react";
import type { MatchResult } from "@/lib/api/api";
import { saveOpportunity, getRecommendations } from "@/lib/api/api";
import FeedbackWidget from "./FeedbackWidget";

interface Props {
  userId: string;
  userEmail: string;
  token: string;
}

function SkeletonCard() {
  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-3 animate-pulse transition-all duration-500">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-9 h-9 bg-gray-200 dark:bg-white/10 shrink-0 transition-all duration-500" />
          <div className="flex flex-col gap-2 flex-1">
            <div className="w-3/4 h-4 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
            <div className="w-1/2 h-3 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
          </div>
        </div>
        <div className="w-12 h-8 bg-gray-200 dark:bg-white/10 rounded shrink-0 transition-all duration-500" />
      </div>
      <div className="w-full h-3 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
      <div className="w-2/3 h-3 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
      <div className="flex gap-2">
        <div className="w-24 h-7 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
        <div className="w-24 h-7 bg-gray-200 dark:bg-white/10 rounded transition-all duration-500" />
      </div>
    </div>
  );
}

export default function ScholarshipsClient({
  userId,
  userEmail,
  token,
}: Props) {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    getRecommendations(userId, userEmail, undefined, token)
      .then((rec) => setMatches(rec.matches))
      .catch(() => setMatches([]))
      .finally(() => setInitialLoading(false));
  }, [userId, userEmail]);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_API_URL || "http://localhost:8000"}/api/v1/scholarships/recommendations?query=${encodeURIComponent(query)}&limit=20`,
        {
          headers: {
            "X-User-Id": userId,
            "X-User-Email": userEmail,
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        },
      );
      const data = await res.json();
      setMatches(data.matches);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(opportunityId: string) {
    await saveOpportunity(userId, opportunityId, userEmail, token);
  }

  return (
    <div className="flex flex-col gap-6 transition-all duration-500">
      <div>
        <h1 className="font-syne text-xl font-bold">Scholarship Agent</h1>
        <p className="font-mono text-[14px] text-gray-400 dark:text-[#6B7280] mt-1 transition-all duration-500">
          Matched from NSP, MahaDBT & myScheme — ranked by eligibility fit
        </p>
      </div>

      <form
        onSubmit={handleSearch}
        className="flex gap-2 transition-all duration-500"
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Semantic search e.g. engineering girls scholarship Maharashtra"
          className="flex-1 px-4 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[15px] transition-all duration-500"
        />
        <button
          type="submit"
          disabled={loading || initialLoading}
          className="px-4 py-2 bg-[#F97316] text-white font-mono text-[14px] flex items-center gap-2 transition-all duration-500 disabled:opacity-60"
        >
          <Search size={14} /> {loading ? "…" : "Search"}
        </button>
      </form>

      <div className="flex flex-col gap-3 transition-all duration-500">
        {initialLoading ? (
          // Show 4 skeleton cards while loading
          [...Array(4)].map((_, i) => <SkeletonCard key={i} />)
        ) : matches.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <Inbox size={22} className="text-gray-300 dark:text-white/20" />
            <p className="font-mono text-[14px] text-gray-400 text-center">
              No matches. Complete your profile for personalized
              recommendations.
            </p>
          </div>
        ) : (
          matches.map((m) => (
            <ScholarshipCard
              key={m.opportunity.id}
              match={m}
              onSave={() => handleSave(m.opportunity.id)}
              userId={userId}
              userEmail={userEmail}
            />
          ))
        )}
      </div>
    </div>
  );
}

function ScholarshipCard({
  match,
  onSave,
  userId,
  userEmail,
}: {
  match: MatchResult;
  onSave: () => void;
  userId: string;
  userEmail: string;
}) {
  const { opportunity: o, match_score, eligibility, reasons } = match;
  const amount =
    o.amount_min && o.amount_max
      ? `₹${o.amount_min.toLocaleString()} – ₹${o.amount_max.toLocaleString()}`
      : o.amount_max
        ? `Up to ₹${o.amount_max.toLocaleString()}`
        : "Amount varies";

  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-3 transition-all duration-500">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-9 h-9 bg-[#F97316]/10 border border-[#F97316]/20 flex items-center justify-center text-[#F97316] shrink-0">
            <GraduationCap size={16} />
          </div>
          <div className="min-w-0">
            <p className="font-mono text-[16px] font-bold text-gray-900 dark:text-[#F0F4FF]">
              {o.title}
            </p>
            <p className="font-mono text-[13px] text-gray-400 mt-0.5">
              {o.source.toUpperCase()} · {amount}
              {o.deadline && ` · Deadline ${o.deadline}`}
            </p>
          </div>
        </div>
        <div className="text-right shrink-0">
          <p className="font-mono text-lg font-bold text-[#F97316]">
            {match_score}%
          </p>
          <p className="font-mono text-[12px] text-gray-400">match</p>
        </div>
      </div>

      {o.description && (
        <p className="font-mono text-[14px] text-gray-600 dark:text-[#a8c7fa] leading-relaxed">
          {o.description}
        </p>
      )}

      <div className="flex items-center gap-2">
        {eligibility.eligible ? (
          <span className="flex items-center gap-1 font-mono text-[13px] text-green-600">
            <CheckCircle size={12} /> Likely eligible
          </span>
        ) : (
          <span className="flex items-center gap-1 font-mono text-[13px] text-red-500">
            <XCircle size={12} /> May not qualify
          </span>
        )}
      </div>

      <ul className="flex flex-col gap-1">
        {reasons.slice(0, 4).map((r, i) => (
          <li
            key={i}
            className="font-mono text-[13px] text-gray-500 dark:text-[#6B7280]"
          >
            {r}
          </li>
        ))}
      </ul>

      <div className="flex gap-2 pt-1">
        <button
          onClick={onSave}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-[#F97316]/30 text-[#F97316] font-mono text-[13px] hover:bg-[#F97316]/5"
        >
          <BookmarkPlus size={12} /> Save & track
        </button>
        {o.application_url && (
          <a
            href={o.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 border border-black/10 dark:border-white/8 font-mono text-[13px] text-gray-500 hover:text-[#F97316]"
          >
            <ExternalLink size={12} /> Official portal
          </a>
        )}
        <FeedbackWidget
          opportunityId={o.id}
          userId={userId}
          userEmail={userEmail}
        />
      </div>
    </div>
  );
}
