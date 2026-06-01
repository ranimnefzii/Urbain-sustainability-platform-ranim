import { useState, useEffect } from "react";
import { admin } from "../api/endpoints";
import type { AdminDashboard, SystemConfig, SystemHealth, SignalStats } from "../types";

export function useAdminDashboard() {
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    admin.dashboard()
      .then((res) => setDashboard(res.data.data ?? null))
      .catch((err) => setError(err.response?.data?.message || "Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  return { dashboard, loading, error, refetch: () => { setLoading(true); admin.dashboard().then((res) => setDashboard(res.data.data ?? null)).finally(() => setLoading(false)); } };
}

export function useSystemHealth() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([admin.health(), admin.config()])
      .then(([h, c]) => {
        setHealth(h.data.data ?? null);
        setConfig(c.data.data ?? null);
      })
      .finally(() => setLoading(false));
  }, []);

  return { health, config, loading };
}

export function useAdminSignalStats() {
  const [stats, setStats] = useState<SignalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    admin.signalStats()
      .then((res) => setStats(res.data.data ?? null))
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading };
}
