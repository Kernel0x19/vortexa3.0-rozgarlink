"use client";
import { useState } from "react";
import {
  User,
  Mail,
  Phone,
  GraduationCap,
  BookOpen,
  Calendar,
  TrendingUp,
  Shield,
  FileText,
  CheckCircle,
  Edit3,
  Save,
  X,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

const STREAMS = [
  "Computer Science (AI)",
  "Computer Science",
  "Information Technology",
  "Electronics & TC",
  "Data Science",
  "Mechanical",
  "Civil",
  "Chemical",
  "Commerce",
  "Arts",
  "Science",
  "Other",
];
const YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Postgraduate"];
const CATEGORIES = ["General", "OBC", "SC", "ST", "EWS", "Other"];

type Profile = {
  full_name: string;
  email: string;
  phone: string;
  college: string;
  stream: string;
  year_of_study: string;
  cgpa: string;
  is_admin: boolean;
};

type Props = {
  userId: string;
  initialProfile: Profile;
  documentCount: number;
};

const COMPLETION_FIELDS = [
  { key: "full_name", label: "Full name", weight: 15 },
  { key: "email", label: "Email", weight: 15 },
  { key: "phone", label: "Phone number", weight: 10 },
  { key: "college", label: "College", weight: 20 },
  { key: "stream", label: "Stream", weight: 15 },
  { key: "year_of_study", label: "Year of study", weight: 15 },
  { key: "cgpa", label: "CGPA", weight: 10 },
];

export default function ProfileClient({
  userId,
  initialProfile,
  documentCount,
}: Props) {
  const [profile, setProfile] = useState<Profile>(initialProfile);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Profile>(initialProfile);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const update = (k: keyof Profile, v: string) =>
    setForm((p) => ({ ...p, [k]: v }));
  const completionPct = COMPLETION_FIELDS.reduce((acc, f) => {
    const val = profile[f.key as keyof Profile];
    return acc + (val && String(val).trim() !== "" ? f.weight : 0);
  }, 0);

  const incompleteFields = COMPLETION_FIELDS.filter((f) => {
    const val = profile[f.key as keyof Profile];
    return !val || String(val).trim() === "";
  });

  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    const supabase = createClient();

    const { error } = await supabase
      .from("profiles")
      .update({
        full_name: form.full_name,
        phone: form.phone,
        college: form.college,
        stream: form.stream,
        year_of_study: form.year_of_study,
        cgpa: form.cgpa ? parseFloat(String(form.cgpa)) : null,
        updated_at: new Date().toISOString(),
      })
      .eq("id", userId);

    if (error) {
      setSaveError(error.message);
    } else {
      setProfile(form);
      setEditing(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    }
    setSaving(false);
  };

  const handleCancel = () => {
    setForm(profile);
    setEditing(false);
    setSaveError(null);
  };

  const initials = profile.full_name
    ? profile.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "EP";

  return (
    <div className="flex flex-col gap-6 max-w-225 transition-all duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-syne text-2xl font-extrabold text-gray-900 dark:text-[#F0F4FF]">
            My Profile
          </h1>
          <p className="font-mono text-[14px] text-gray-400 dark:text-[#6B7280] mt-1">
            Manage your personal and academic information
          </p>
        </div>
        {!editing ? (
          <button
            onClick={() => setEditing(true)}
            className="flex items-center gap-2 px-4 py-2.5 border border-black/10 dark:border-white/8 font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:border-[#F97316]/40 hover:text-[#F97316] transition-all duration-200 cursor-pointer"
          >
            <Edit3 size={14} />
            Edit profile
          </button>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={handleCancel}
              className="flex items-center gap-2 px-4 py-2.5 border border-black/10 dark:border-white/8 font-mono text-sm text-gray-500 dark:text-[#6B7280] hover:border-red-500/30 hover:text-red-500 transition-all duration-200 cursor-pointer"
            >
              <X size={14} />
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2.5 bg-[#F97316] text-white font-mono text-sm hover:bg-[fdba74] transition-colors duration-200 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
            >
              {saving ? (
                <svg
                  className="animate-spin h-3.5 w-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8z"
                  />
                </svg>
              ) : (
                <Save size={14} />
              )}
              Save changes
            </button>
          </div>
        )}
      </div>
      {saveSuccess && (
        <div className="flex items-center gap-3 px-5 py-3 border border-green-500/30 bg-green-500/8 dark:bg-green-500/10">
          <CheckCircle size={15} className="text-green-500 shrink-0" />
          <p className="font-mono text-sm text-green-600 dark:text-green-400">
            Profile updated successfully.
          </p>
        </div>
      )}
      {saveError && (
        <div className="flex items-center gap-3 px-5 py-3 border border-red-500/30 bg-red-500/10">
          <X size={15} className="text-red-500 shrink-0" />
          <p className="font-mono text-sm text-red-500">{saveError}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="flex flex-col gap-8">
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-6 flex flex-col items-center gap-4">
            <div className="w-20 h-20 bg-[#F97316] flex items-center justify-center font-syne text-3xl font-extrabold text-white rounded-full">
              {initials}
            </div>
            <div className="text-center">
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-base">
                {profile.full_name || "—"}
              </p>
              <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280] mt-0.5">
                {profile.email}
              </p>
              {profile.is_admin && (
                <span className="inline-flex items-center gap-1 mt-2 font-mono text-[12px] text-[#F97316] border border-[#F97316]/30 bg-[#F97316]/8 px-2 py-0.5">
                  <Shield size={10} /> Admin
                </span>
              )}
            </div>
          </div>
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117]">
            <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Profile Completion
              </p>
              <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280]">
                {completionPct}% complete
              </p>
            </div>
            <div className="px-5 py-4 flex flex-col gap-3">
              <div className="w-full h-1.5 bg-black/8 dark:bg-white/8 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    completionPct === 100 ? "bg-green-500" : "bg-[#F97316]"
                  }`}
                  style={{ width: `${completionPct}%` }}
                />
              </div>
              {incompleteFields.length === 0 ? (
                <div className="flex items-center gap-2 font-mono text-[14px] text-green-500">
                  <CheckCircle size={13} />
                  All fields complete
                </div>
              ) : (
                <div className="flex flex-col gap-1.5">
                  <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] tracking-widest">
                    MISSING
                  </p>
                  {incompleteFields.map((f) => (
                    <div
                      key={f.key}
                      className="flex items-center gap-2 font-mono text-[13px] text-gray-500 dark:text-[#6B7280]"
                    >
                      <span className="w-1 h-1 rounded-full bg-yellow-500 shrink-0" />
                      {f.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117]">
            <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Overview
              </p>
            </div>
            <div className="flex flex-col">
              {[
                {
                  icon: <FileText size={13} />,
                  label: "Documents",
                  value: String(documentCount),
                  href: "/dashboard/documents",
                },
                {
                  icon: <GraduationCap size={13} />,
                  label: "Scholarships",
                  value: "—",
                  href: "/dashboard/scholarships",
                },
                {
                  icon: <TrendingUp size={13} />,
                  label: "Applications",
                  value: "0",
                  href: "/dashboard/scholarships",
                },
              ].map((item, i, arr) => (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center justify-between px-5 py-3 hover:bg-white dark:hover:bg-[#161822] transition-colors duration-200 group ${i !== arr.length - 1 ? "border-b border-black/10 dark:border-white/8" : ""}`}
                >
                  <div className="flex items-center gap-2 font-mono text-[14px] text-gray-500 dark:text-[#6B7280] group-hover:text-[#F97316] transition-colors duration-200">
                    <span className="text-[#F97316]">{item.icon}</span>
                    {item.label}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono text-[14px] font-bold text-gray-900 dark:text-[#F0F4FF]">
                      {item.value}
                    </span>
                    <ChevronRight
                      size={12}
                      className="text-gray-300 dark:text-white/20 group-hover:text-[#F97316] transition-colors duration-200"
                    />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117]">
            <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Personal Information
              </p>
              <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280]">
                Your basic contact details
              </p>
            </div>
            <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
              <Field
                label="FULL NAME"
                icon={<User size={13} />}
                editing={editing}
                value={form.full_name}
                display={profile.full_name}
                placeholder="Prathamesh Mangnale"
                onChange={(v) => update("full_name", v)}
              />
              <Field
                label="EMAIL"
                icon={<Mail size={13} />}
                editing={false}
                value={profile.email}
                display={profile.email}
                placeholder="you@college.edu"
                onChange={() => {}}
                disabled
                hint="Email cannot be changed"
              />
              <Field
                label="PHONE NUMBER"
                icon={<Phone size={13} />}
                editing={editing}
                value={form.phone}
                display={profile.phone}
                placeholder="+91 98765 43210"
                onChange={(v) => update("phone", v)}
              />
            </div>
          </div>
          <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117]">
            <div className="px-5 py-4 border-b border-black/10 dark:border-white/8">
              <p className="font-syne font-bold text-gray-900 dark:text-[#F0F4FF] text-sm">
                Academic Information
              </p>
              <p className="font-mono text-[13px] text-gray-400 dark:text-[#6B7280]">
                Used for scholarship matching
              </p>
            </div>
            <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
              <div className="sm:col-span-2">
                <Field
                  label="COLLEGE / INSTITUTION"
                  icon={<GraduationCap size={13} />}
                  editing={editing}
                  value={form.college}
                  display={profile.college}
                  placeholder="Vishwakarma Institute of Technology, Pune"
                  onChange={(v) => update("college", v)}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] tracking-widest flex items-center gap-1.5">
                  <BookOpen size={13} className="text-[#F97316]" />
                  STREAM
                </label>
                {editing ? (
                  <select
                    value={form.stream}
                    onChange={(e) => update("stream", e.target.value)}
                    className="px-3.5 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] text-gray-900 dark:text-[#F0F4FF] font-mono text-sm focus:outline-none focus:border-[#F97316] transition-colors duration-200 appearance-none cursor-pointer"
                  >
                    <option value="">Select stream</option>
                    {STREAMS.map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>
                ) : (
                  <DisplayValue value={profile.stream} />
                )}
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] tracking-widest flex items-center gap-1.5">
                  <Calendar size={13} className="text-[#F97316]" />
                  YEAR OF STUDY
                </label>
                {editing ? (
                  <select
                    value={form.year_of_study}
                    onChange={(e) => update("year_of_study", e.target.value)}
                    className="px-3.5 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] text-gray-900 dark:text-[#F0F4FF] font-mono text-sm focus:outline-none focus:border-[#F97316] transition-colors duration-200 appearance-none cursor-pointer"
                  >
                    <option value="">Select year</option>
                    {YEARS.map((y) => (
                      <option key={y}>{y}</option>
                    ))}
                  </select>
                ) : (
                  <DisplayValue value={profile.year_of_study} />
                )}
              </div>
              <Field
                label="CGPA"
                icon={<TrendingUp size={13} />}
                editing={editing}
                value={String(form.cgpa)}
                display={profile.cgpa ? String(profile.cgpa) : ""}
                placeholder="8.4"
                type="number"
                onChange={(v) => update("cgpa", v)}
                hint="Out of 10"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  icon,
  editing,
  value,
  display,
  placeholder,
  onChange,
  disabled,
  hint,
  type = "text",
}: {
  label: string;
  icon: React.ReactNode;
  editing: boolean;
  value: string;
  display: string;
  placeholder: string;
  onChange: (v: string) => void;
  disabled?: boolean;
  hint?: string;
  type?: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] tracking-widest flex items-center gap-1.5">
        <span className="text-[#F97316]">{icon}</span>
        {label}
      </label>
      {editing && !disabled ? (
        <div className="flex flex-col gap-1">
          <input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            step={type === "number" ? "0.01" : undefined}
            min={type === "number" ? "0" : undefined}
            max={type === "number" ? "10" : undefined}
            className="px-3.5 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] text-gray-900 dark:text-[#F0F4FF] font-mono text-sm placeholder:text-gray-300 dark:placeholder:text-white/20 focus:outline-none focus:border-[#F97316] transition-colors duration-200"
          />
          {hint && (
            <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280]">
              {hint}
            </p>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-0.5">
          <DisplayValue value={display} disabled={disabled} />
          {hint && disabled && (
            <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280]">
              {hint}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function DisplayValue({
  value,
  disabled,
}: {
  value: string;
  disabled?: boolean;
}) {
  return (
    <div
      className={`px-3.5 py-2.5 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] ${disabled ? "opacity-60" : ""}`}
    >
      <p
        className={`font-mono text-sm ${
          value
            ? "text-gray-900 dark:text-[#F0F4FF]"
            : "text-gray-300 dark:text-white/20 italic"
        }`}
      >
        {value || "Not set"}
      </p>
    </div>
  );
}
