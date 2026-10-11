"use client";
import { useSessionExpiry } from "@/src/hooks/useIdleLogout";

export function SessionGaurd() {
  useSessionExpiry();
  return null;
}
