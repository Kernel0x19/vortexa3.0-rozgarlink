const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type MatchResult = {
  opportunity: {
    id: string;
    source: string;
    category: string;
    title: string;
    description: string | null;
    amount_min: number | null;
    amount_max: number | null;
    deadline: string | null;
    eligibility_rules: Record<string, unknown>;
    documents_required: string[];
    application_url: string | null;
    state_filter: string[];
    tags: string[];
  };
  match_score: number;
  eligibility: {
    eligible: boolean;
    score: number;
    passed: string[];
    failed: string[];
    warnings: string[];
  };
  reasons: string[];
};

export type RecommendationResponse = {
  matches: MatchResult[];
  total: number;
  readiness_score: number;
};

export type DashboardStats = {
  eligible_matches?: number;
  opportunities_available?: number;
  skill_gaps_identified?: number;
  scholarships_matched?: number;
  internships_available?: number;
  documents_uploaded?: number;
  applications_tracked: number;
  readiness_score: number;
};

export type StudentProfile = {
  id?: string;
  user_id?: string;
  full_name?: string | null;
  date_of_birth?: string | null;
  gender?: string | null;
  phone?: string | null;
  state?: string | null;
  district?: string | null;
  category?: string | null;
  income_annual?: number | null;
  college?: string | null;
  university?: string | null;
  stream?: string | null;
  degree?: string | null;
  year_of_study?: number | null;
  cgpa?: number | null;
  percentage_12th?: number | null;
  backlogs?: number | null;
  skills?: string[];
  documents?: { type: string; name: string }[];
  preferences?: {
    work_mode?: string;
    pref_duration?: string;
    availability?: string;
    pref_locations?: string[];
    interests?: string[];
    resume_url?: string;
    portfolio_url?: string;
    cover_letter_url?: string;
    [key: string]: unknown;
  };
  readiness_score?: number;
};

export type Application = {
  id: string;
  opportunity_id: string;
  state: string;
  match_score: number;
  eligibility_result: Record<string, unknown> | null;
  checklist: { document: string; status: string; required: boolean }[];
  progress_pct: number;
  saved: boolean;
  opportunity?: MatchResult["opportunity"];
  created_at: string;
  updated_at: string;
};

export type Notification = {
  id: string;
  title: string;
  body: string;
  channel: string;
  read: boolean;
  created_at: string;
};

async function apiFetch<T>(
  path: string,
  options: RequestInit & {
    userId?: string;
    userEmail?: string;
    token?: string;
    next?: { revalidate: number };
  } = {},
): Promise<T> {
  const { userId, userEmail, token, next, ...fetchOptions } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };
  if (userId) headers["X-User-Id"] = userId;
  if (userEmail) headers["X-User-Email"] = userEmail;
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15_000);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
      cache: next ? undefined : "no-store",
      ...(next ? { next } : {}),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json();
  } catch (err) {
    if ((err as Error).name === "AbortError") {
      throw new Error("Backend unavailable");
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export function getRecommendations(
  userId: string,
  userEmail?: string,
  query?: string,
  token?: string,
) {
  const params = new URLSearchParams();
  if (query) params.set("query", query);
  params.set("limit", "10");
  return apiFetch<RecommendationResponse>(
    `/api/v1/scholarships/recommendations?${params}`,
    { userId, userEmail, token },
  );
}

export type InternshipOpportunity = {
  id: string;
  source: string;
  title: string;
  description: string | null;
  amount_min: number | null;
  amount_max: number | null;
  deadline: string | null;
  eligibility_rules: Record<string, unknown>;
  documents_required: string[];
  application_url: string | null;
  tags: string[];
  raw_data: {
    company?: string | null;
    location?: string | null;
    duration?: string | null;
  } | null;
};

export type InternshipMatchResult = {
  opportunity: InternshipOpportunity;
  match_score: number;
  eligibility: {
    eligible: boolean;
    score: number;
    passed: string[];
    failed: string[];
    warnings: string[];
  };
  reasons: string[];
};

export type InternshipRecommendationResponse = {
  matches: InternshipMatchResult[];
  total: number;
};

export function getInternshipRecommendations(
  userId: string,
  userEmail?: string,
  query?: string,
  token?: string,
) {
  const params = new URLSearchParams();
  if (query) params.set("query", query);
  params.set("limit", "30");
  return apiFetch<InternshipRecommendationResponse>(
    `/api/v1/internships/recommendations?${params}`,
    { userId, userEmail, token },
  );
}

export function saveInternship(
  userId: string,
  opportunityId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<Application>(`/api/v1/internships/applications`, {
    method: "POST",
    body: JSON.stringify({ opportunity_id: opportunityId, saved: true }),
    userId,
    userEmail,
    token,
  });
}

export function getDashboardStats(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<DashboardStats>(`/api/v1/scholarships/dashboard`, {
    userId,
    userEmail,
    token,
  });
}

export function getProfile(userId: string, userEmail?: string, token?: string) {
  return apiFetch<StudentProfile | null>(`/api/v1/profile`, {
    userId,
    userEmail,
    token,
  });
}

export function updateProfile(
  userId: string,
  data: StudentProfile,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<StudentProfile>(`/api/v1/profile`, {
    method: "PUT",
    body: JSON.stringify(data),
    userId,
    userEmail,
    token,
  });
}

export function getApplications(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<Application[]>(`/api/v1/scholarships/applications`, {
    userId,
    userEmail,
    token,
  });
}

export function saveOpportunity(
  userId: string,
  opportunityId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<Application>(`/api/v1/scholarships/applications`, {
    method: "POST",
    body: JSON.stringify({ opportunity_id: opportunityId, saved: true }),
    userId,
    userEmail,
    token,
  });
}

export function getNotifications(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<Notification[]>(`/api/v1/notifications`, {
    userId,
    userEmail,
    token,
  });
}

export function markNotificationRead(
  userId: string,
  id: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<{ ok: boolean }>(`/api/v1/notifications/${id}/read`, {
    method: "POST",
    userId,
    userEmail,
    token,
  });
}

export function getConsents(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<
    { purpose: string; granted: boolean; granted_at: string | null }[]
  >(`/api/v1/consent`, { userId, userEmail, token });
}

export function setConsent(
  userId: string,
  purpose: string,
  granted: boolean,
  userEmail?: string,
  token?: string,
) {
  return apiFetch(`/api/v1/consent`, {
    method: "POST",
    body: JSON.stringify({ purpose, granted }),
    userId,
    userEmail,
    token,
  });
}

export type SemanticSearchResult = {
  opportunity_id: string;
  title: string;
  description: string;
  category: string;
  relevance_score: number;
  deadline: string | null;
  amount: number | null;
  source_url: string | null;
};

export type SemanticSearchResponse = {
  query: string;
  category: string | null;
  results_count: number;
  matches: SemanticSearchResult[];
};

export function searchOpportunitiesSemantic(
  query: string,
  category?: string,
  topK = 20,
  minScore = 0.1,
  token?: string,
) {
  const params = new URLSearchParams({
    q: query,
    top_k: String(topK),
    min_score: String(minScore),
  });
  if (category) params.set("category", category);
  return apiFetch<SemanticSearchResponse>(
    `/api/v1/search/opportunities?${params}`,
    { token },
  );
}

export type DocumentStatus = {
  document_id: string;
  document_type: string;
  verification_status: string;
  extracted_fields: Record<string, unknown> | null;
  confidence_score: number;
  gov_verification_status?: string;
  uploaded_at?: string;
};

export async function uploadDocument(
  userId: string,
  documentType: string,
  file: File,
  applicationId?: string,
  token?: string,
): Promise<DocumentStatus> {
  const form = new FormData();
  form.append("user_id", userId);
  form.append("document_type", documentType);
  form.append("file", file);
  if (applicationId) form.append("application_id", applicationId);

  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/documents/upload`, {
    method: "POST",
    body: form,
    headers,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export function getDocumentStatus(documentId: string, token?: string) {
  return apiFetch<DocumentStatus>(`/api/v1/documents/${documentId}/status`, {
    token,
  });
}

export type FeedbackPayload = {
  opportunity_id: string;
  feedback_type:
    | "relevant"
    | "not_relevant"
    | "ineligible"
    | "applied"
    | "ignored";
  comment?: string;
};

export function submitFeedback(
  userId: string,
  payload: FeedbackPayload,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<{ feedback_type: string; submitted_at: string }>(
    `/api/v1/feedback/`,
    { method: "POST", body: JSON.stringify(payload), userId, userEmail, token },
  );
}

export type NotificationPreferences = {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  voice_enabled: boolean;
  deadline_reminders: boolean;
  new_matches: boolean;
  status_updates: boolean;
};

export function getNotificationPreferences(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<NotificationPreferences>(
    `/api/v1/notifications/preferences`,
    { userId, userEmail, token },
  );
}

export function updateNotificationPreferences(
  userId: string,
  prefs: NotificationPreferences,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<NotificationPreferences>(
    `/api/v1/notifications/preferences`,
    {
      method: "PUT",
      body: JSON.stringify(prefs),
      userId,
      userEmail,
      token,
    },
  );
}

export type PlatformAnalytics = {
  platform_kpis: {
    total_users: number;
    total_opportunities: number;
    total_applications: number;
    total_feedback: number;
    total_audit_events: number;
  };
  conversion: { application_conversion_rate: number };
  timestamp: string;
};

export function getAdminAnalytics(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<PlatformAnalytics>(`/api/v1/admin/analytics`, {
    userId,
    userEmail,
    token,
  });
}

export type ConnectorStatusItem = {
  name: string;
  last_run: string | null;
  last_success: string | null;
  records_processed: number;
  is_stale: boolean;
  last_error: string | null;
};

export function getConnectorStatuses(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<{ connectors: ConnectorStatusItem[]; count: number }>(
    `/api/v1/admin/connectors/status`,
    { userId, userEmail, token },
  );
}

export function triggerConnectorRun(
  userId: string,
  connectorName?: string,
  userEmail?: string,
  token?: string,
) {
  const params = connectorName ? `?connector_name=${connectorName}` : "";
  return apiFetch<{ status: string; results: unknown }>(
    `/api/v1/admin/connectors/trigger${params}`,
    { method: "POST", userId, userEmail, token },
  );
}

export type DataFreshness = {
  aggregate_freshness_score: number;
  total_connectors: number;
  stale_connectors: number;
  connectors: {
    connector_name: string;
    status: string;
    last_poll_at: string | null;
    last_successful_poll: string | null;
    records_ingested: number;
    is_fresh: boolean;
    error_message: string | null;
  }[];
};

export function getDataFreshness(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<DataFreshness>(`/api/v1/admin/data-freshness`, {
    userId,
    userEmail,
    token,
  });
}

export type AccuracyMetrics = {
  precision: number;
  feedback_breakdown: {
    relevant: number;
    not_relevant: number;
    ineligible: number;
    total_evaluated: number;
  };
};

export function getAccuracyMetrics(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<AccuracyMetrics>(`/api/v1/admin/accuracy-metrics`, {
    userId,
    userEmail,
    token,
  });
}

export type HackathonItem = {
  id: string;
  source: string;
  title: string;
  organizer: string | null;
  mode: string;
  location: string | null;
  team_size: string | null;
  prize_pool: number;
  registration_deadline: string | null;
  start_date: string | null;
  end_date: string | null;
  themes: string[];
  apply_link: string | null;
  posted_date: string | null;
};

export type HackathonListResponse = {
  items: HackathonItem[];
  total: number;
};

export function getHackathons(
  userId: string,
  userEmail?: string,
  params?: {
    query?: string;
    mode?: string;
    source?: string;
    theme?: string;
    prize_min?: number;
    location?: string;
    deadline_days?: number;
    limit?: number;
  },
  token?: string,
) {
  const p = new URLSearchParams();
  if (params?.query) p.set("query", params.query);
  if (params?.mode) p.set("mode", params.mode);
  if (params?.source) p.set("source", params.source);
  if (params?.theme) p.set("theme", params.theme);
  if (params?.prize_min) p.set("prize_min", String(params.prize_min));
  if (params?.location) p.set("location", params.location);
  if (params?.deadline_days)
    p.set("deadline_days", String(params.deadline_days));
  p.set("limit", String(params?.limit ?? 60));
  return apiFetch<HackathonListResponse>(`/api/v1/hackathons?${p}`, {
    userId,
    userEmail,
    token,
  });
}

// -- Placements / Jobs --------------------------------------------------------

export type JobOpportunity = {
  id: string;
  source: string;
  title: string;
  description: string | null;
  company: string | null;
  location: string | null;
  work_type: string | null;
  experience: string | null;
  salary_lpa: number | null;
  amount_min: number | null;
  amount_max: number | null;
  deadline: string | null;
  application_url: string | null;
  tags: string[];
  documents_required: string[];
};

export type JobMatchResult = {
  opportunity: JobOpportunity;
  match_score: number;
};

export type JobRecommendationResponse = {
  matches: JobMatchResult[];
  total: number;
  readiness_score: number;
};

export function getJobRecommendations(
  userId: string,
  userEmail?: string,
  params?: {
    query?: string;
    location?: string;
    work_type?: string;
    salary_min?: number;
    experience?: string;
    source?: string;
    limit?: number;
  },
  token?: string,
) {
  const p = new URLSearchParams();
  if (params?.query) p.set("query", params.query);
  if (params?.location) p.set("location", params.location);
  if (params?.work_type) p.set("work_type", params.work_type);
  if (params?.salary_min) p.set("salary_min", String(params.salary_min));
  if (params?.experience) p.set("experience", params.experience);
  if (params?.source) p.set("source", params.source);
  p.set("limit", String(params?.limit ?? 30));
  return apiFetch<JobRecommendationResponse>(`/api/v1/placements/recommendations?${p}`, {
    userId,
    userEmail,
    token,
  });
}

export function saveJob(
  userId: string,
  opportunityId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<Application>(`/api/v1/placements/applications`, {
    method: "POST",
    body: JSON.stringify({ opportunity_id: opportunityId, saved: true }),
    userId,
    userEmail,
    token,
  });
}

export function getJobApplications(
  userId: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<Application[]>(`/api/v1/placements/applications`, {
    userId,
    userEmail,
    token,
  });
}
// ── Career Impact Lab — What-If Simulator ────────────────────────────────────

export type OpportunityEvaluation = {
  id: string;
  title: string;
  category: "placement" | "internship";
  source: string;
  company: string;
  location: string;
  work_type: string;
  deadline: string | null;
  application_url: string | null;
  baseline_eligible: boolean;
  simulated_eligible: boolean;
  status_change:
    | "NEWLY_ELIGIBLE"
    | "BOOSTED"
    | "LOST_ELIGIBILITY"
    | "UNCHANGED_ELIGIBLE"
    | "INELIGIBLE";
  baseline_score: number;
  simulated_score: number;
  score_delta: number;
  mandatory_passed: string[];
  mandatory_failed: string[];
  mandatory_skill_gaps: string[];
  optional_skill_gaps: string[];
  matched_skills: string[];
  action_plan: string;
};

export type SkillImpactItem = {
  skill: string;
  roles_unlocked_count: number;
  mandatory_in_roles_count: number;
  preferred_in_roles_count: number;
  average_score_boost: number;
  impact_tier: "HIGH" | "MEDIUM" | "NICHE";
  sample_roles: string[];
};

export type ScenarioComparisonItem = {
  scenario_id: string;
  title: string;
  description: string;
  added_skills: string[];
  eligible_count: number;
  newly_unlocked_count: number;
  avg_match_score: number;
  remaining_mandatory_gaps_count: number;
  top_unlocks: string[];
};

export type WhatIfSimulationResponse = {
  baseline_eligible_count: number;
  simulated_eligible_count: number;
  newly_unlocked_count: number;
  boosted_count: number;
  lost_eligibility_count: number;
  baseline_avg_score: number;
  simulated_avg_score: number;
  avg_score_boost: number;
  remaining_critical_gaps_count: number;
  total_evaluated_opportunities: number;
  opportunities: OpportunityEvaluation[];
  skill_impact_leaderboard: SkillImpactItem[];
  mandatory_gaps_summary: string[];
  optional_gaps_summary: string[];
  scenarios: ScenarioComparisonItem[];
  active_profile_snapshot: Record<string, any>;
  available_courses: {
    key: string;
    title: string;
    provider: string;
    duration: string;
    category: string;
    skills: string[];
  }[];
};

export type WhatIfRequest = {
  user_id?: string;
  skills: string[];
  skill_proficiencies?: Record<string, string>;
  completed_courses?: string[];
  preferred_cities?: string[];
  preferred_work_modes?: string[];
  min_stipend?: number;
  hypothetical_cgpa?: number;
  hypothetical_stream?: string;
  hypothetical_degree?: string;
  hypothetical_year_of_study?: number;
};

export function runWhatIfSimulation(
  request: WhatIfRequest,
  userId?: string,
  userEmail?: string,
  token?: string,
) {
  return apiFetch<WhatIfSimulationResponse>(`/api/v1/simulation/what-if`, {
    method: "POST",
    body: JSON.stringify(request),
    userId,
    userEmail,
    token,
  });
}

export function applySimulatedProfileChanges(
  params: {
    user_id: string;
    skills: string[];
    skill_proficiencies?: Record<string, string>;
    preferred_cities?: string[];
    preferred_work_modes?: string[];
    confirmed: boolean;
  },
  userEmail?: string,
  token?: string,
) {
  return apiFetch<{ status: string; message: string }>(
    `/api/v1/simulation/apply-to-profile`,
    {
      method: "POST",
      body: JSON.stringify(params),
      userId: params.user_id,
      userEmail,
      token,
    },
  );
}