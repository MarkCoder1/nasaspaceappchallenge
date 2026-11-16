"use client";

import { useEffect, useState } from "react";
import { checkBackendHealth } from "@/lib/api";

export default function BackendStatus() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    checkBackendHealth().then((healthy) => setStatus(healthy ? "online" : "offline"));
  }, []);

  return <span className="backend-status" aria-live="polite"><span className="status-dot" /> BACKEND {status.toUpperCase()}</span>;
}