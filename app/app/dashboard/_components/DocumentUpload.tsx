"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  FileText,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Clock,
  XCircle,
  Loader2,
  RefreshCw,
  Shield,
  BookOpen,
} from "lucide-react";
import type { DocumentStatus } from "@/lib/api/api";
import { uploadDocument, getConsents, setConsent } from "@/lib/api/api";

const PURPOSE_LABELS: Record<string, string> = {
  aadhaar_verification: "Use my Aadhaar to auto-verify eligibility",
  income_certificate_processing: "Process income certificate in secure enclave",
  eligibility_auto_check: "Run automatic eligibility checks against schemes",
  document_ocr: "Extract data from uploaded documents via OCR",
};

const DOC_TYPES = [
  { value: "aadhaar", label: "Aadhaar Card" },
  { value: "income_certificate", label: "Income Certificate" },
  { value: "caste_certificate", label: "Caste Certificate" },
  { value: "marksheet", label: "Marksheet / Transcript" },
  { value: "bonafide", label: "Bonafide Certificate" },
];

const STATUS_CONFIG: Record<
  string,
  { icon: React.ReactNode; color: string; label: string }
> = {
  auto_approved: {
    icon: <CheckCircle2 size={16} />,
    color: "text-green-500",
    label: "Auto-Approved",
  },
  verified: {
    icon: <CheckCircle2 size={16} />,
    color: "text-green-500",
    label: "Verified",
  },
  needs_review: {
    icon: <AlertTriangle size={16} />,
    color: "text-amber-500",
    label: "Needs Review",
  },
  processing: {
    icon: <Loader2 size={16} className="animate-spin" />,
    color: "text-[#F97316]",
    label: "Processing",
  },
  pending: {
    icon: <Clock size={16} />,
    color: "text-gray-400",
    label: "Pending",
  },
  rejected: {
    icon: <XCircle size={16} />,
    color: "text-red-500",
    label: "Rejected",
  },
};

interface Props {
  userId: string;
  userEmail: string;
  token?: string;
}

interface ConsentManagerProps {
  consents: Record<string, boolean>;
  onToggle: (purpose: string, granted: boolean) => void;
}

function ConsentManager({ consents, onToggle }: ConsentManagerProps) {
  return (
    <div className="flex flex-col gap-4 transition-all duration-500">
      <div>
        <h2 className="font-syne text-lg font-bold flex items-center gap-2 transition-all duration-500">
          <BookOpen size={18} className="text-[#F97316]" />
          Consent Management
        </h2>
        <p className="font-mono text-[12px] text-gray-400 mt-1 transition-all duration-500">
          DPDP Act compliant opt-in per data use case. All access is
          audit-logged.
        </p>
      </div>
      {Object.entries(PURPOSE_LABELS).map(([purpose, label]) => (
        <label
          key={purpose}
          className="flex items-start gap-3 border border-black/10 dark:border-white/8 p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-[#0F1117] transition-all duration-500"
        >
          <input
            type="checkbox"
            checked={consents[purpose] ?? false}
            onChange={(e) => onToggle(purpose, e.target.checked)}
            className="mt-0.5 transition-all duration-500"
          />
          <div>
            <p className="font-mono text-[13px] text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
              {label}
            </p>
            <p className="font-mono text-[10px] text-gray-400 mt-0.5">
              {purpose}
            </p>
          </div>
        </label>
      ))}
    </div>
  );
}

export default function DocumentUpload({ userId, userEmail, token }: Props) {
  const [consents, setConsents] = useState<Record<string, boolean>>({});
  const [consentsLoading, setConsentsLoading] = useState(true);
  const [docType, setDocType] = useState(DOC_TYPES[0].value);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState<DocumentStatus[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getConsents(userId, userEmail, token)
      .then((records) => {
        const map: Record<string, boolean> = {};
        records.forEach((r) => {
          map[r.purpose] = r.granted;
        });
        setConsents(map);
      })
      .finally(() => setConsentsLoading(false));
  }, [userId, userEmail]);

  const allowedDocs = DOC_TYPES.filter((dt) => {
    if (dt.value === "aadhaar")
      return consents["aadhaar_verification"] ?? false;
    if (dt.value === "income_certificate")
      return consents["income_certificate_processing"] ?? false;
    return true;
  });

  useEffect(() => {
    if (!allowedDocs.find((d) => d.value === docType)) {
      setDocType(allowedDocs[0]?.value ?? "");
    }
  }, [consents]);

  const handleToggle = useCallback(
    async (purpose: string, granted: boolean) => {
      setConsents((c) => ({ ...c, [purpose]: granted }));
      await setConsent(userId, purpose, granted, userEmail, token);
    },
    [userId, userEmail],
  );

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const result = await uploadDocument(
        userId,
        docType,
        file,
        undefined,
        token,
      );
      setUploaded((prev) => [result, ...prev]);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [file, docType, userId]);

  return (
    <div className="flex flex-col gap-8 max-w-2xl transition-all duration-500">
      <div>
        <h1 className="font-syne text-xl font-bold flex items-center gap-2 transition-all duration-500">
          <Shield size={20} className="text-[#F97316]" />
          Document Vault
        </h1>
        <p className="font-mono text-[12px] text-gray-400 dark:text-[#6B7280] mt-1">
          Upload and verify documents — AES-256 encrypted, TEE-secured
          processing
        </p>
      </div>

      {consentsLoading ? (
        <p className="font-mono text-[12px] text-gray-400">Loading consents…</p>
      ) : (
        <ConsentManager consents={consents} onToggle={handleToggle} />
      )}

      <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-6 flex flex-col gap-4 transition-all duration-500">
        <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF] transition-all duration-500">
          Upload Document
        </p>

        {allowedDocs.length === 0 ? (
          <p className="font-mono text-[12px] text-amber-500">
            Enable at least one consent above to unlock document upload.
          </p>
        ) : (
          <>
            {/* Document Type Selector */}
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="doc-type-select"
                className="font-mono text-[11px] text-gray-500"
              >
                Document Type
              </label>
              <select
                id="doc-type-select"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="px-3 py-2 border border-black/10 dark:border-white/8 bg-white dark:bg-[#161822] font-mono text-[13px] outline-none focus:border-[#F97316]/40 transition-all duration-500"
              >
                {allowedDocs.map((dt) => (
                  <option key={dt.value} value={dt.value}>
                    {dt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* File Picker */}
            <div className="flex flex-col gap-1.5 transition-all duration-500">
              <label
                htmlFor="doc-file-input"
                className="font-mono text-[11px] text-gray-500"
              >
                File (PDF, PNG, JPG)
              </label>
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-black/10 dark:border-white/8 p-8 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-[#F97316]/30 transition-all duration-500"
              >
                <Upload
                  size={24}
                  className="text-gray-300 dark:text-[#3B3F51]"
                />
                <p className="font-mono text-[12px] text-gray-400">
                  {file ? file.name : "Click to select file"}
                </p>
                {file && (
                  <p className="font-mono text-[10px] text-gray-400">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                )}
              </div>
              <input
                id="doc-file-input"
                ref={fileInputRef}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 text-red-500 font-mono text-[12px]">
                <XCircle size={14} /> {error}
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="flex items-center justify-center gap-2 px-4 py-2.5 bg-[#F97316] hover:bg-[#0B5ABD] disabled:opacity-50 text-white font-mono text-[12px] transition-all duration-500"
            >
              {uploading ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Upload size={14} />
              )}
              {uploading ? "Encrypting & Verifying…" : "Upload & Verify"}
            </button>
          </>
        )}
      </div>

      {uploaded.length > 0 && (
        <div className="flex flex-col gap-3">
          <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF]">
            Verification Results
          </p>
          {uploaded.map((doc) => (
            <DocumentCard key={doc.document_id} doc={doc} />
          ))}
        </div>
      )}
    </div>
  );
}

function DocumentCard({ doc }: { doc: DocumentStatus }) {
  const status =
    STATUS_CONFIG[doc.verification_status] || STATUS_CONFIG.pending;
  const fields = doc.extracted_fields
    ? Object.entries(doc.extracted_fields)
    : [];

  return (
    <div className="border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0F1117] p-5 flex flex-col gap-3 transition-all duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText size={16} className="text-[#F97316]" />
          <div>
            <p className="font-mono text-[13px] font-bold text-gray-900 dark:text-[#F0F4FF] uppercase transition-all duration-500">
              {doc.document_type.replace("_", " ")}
            </p>
            <p className="font-mono text-[10px] text-gray-400">
              {doc.document_id}
            </p>
          </div>
        </div>
        <div className={`flex items-center gap-1.5 ${status.color}`}>
          {status.icon}
          <span className="font-mono text-[11px] font-bold">
            {status.label}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className="font-mono text-[11px] text-gray-500 shrink-0">
          Confidence
        </span>
        <div className="flex-1 h-2 bg-gray-200 dark:bg-[#1C1F2E] rounded-full overflow-hidden transition-all duration-500">
          <div
            className="h-full bg-[#F97316] transition-all duration-700"
            style={{ width: `${Math.round(doc.confidence_score * 100)}%` }}
          />
        </div>
        <span className="font-mono text-[12px] font-bold text-[#F97316] shrink-0">
          {Math.round(doc.confidence_score * 100)}%
        </span>
      </div>

      {fields.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {fields.slice(0, 8).map(([key, value]) => (
            <div
              key={key}
              className="border border-black/5 dark:border-white/5 p-2 transition-all duration-500"
            >
              <p className="font-mono text-[10px] text-gray-400 uppercase">
                {key.replace(/_/g, " ")}
              </p>
              <p className="font-mono text-[12px] text-gray-800 dark:text-[#F0F4FF] truncate transition-all duration-500">
                {String(value)}
              </p>
            </div>
          ))}
        </div>
      )}

      {doc.verification_status === "rejected" && (
        <button className="flex items-center gap-1.5 px-3 py-1.5 border border-red-500/30 text-red-500 font-mono text-[11px] hover:bg-red-500/5 w-fit transition-all">
          <RefreshCw size={12} /> Re-upload Document
        </button>
      )}
    </div>
  );
}
