import { useState, useEffect, useCallback, useRef } from "react";
import { signals } from "../api/endpoints";
import type { Signal, SignalFilter, SignalStats } from "../types";

function shallowEqual(a: Record<string, any>, b: Record<string, any>) {
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  for (const k of ka) if (a[k] !== b[k]) return false;
  return true;
}

export function useSignalList(filters: SignalFilter = {}) {
  const [data, setData] = useState<{ items: Signal[]; page: number; pages: number; total: number }>({ items: [], page: 1, pages: 1, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const prevFilters = useRef<SignalFilter | null>(null);

  const fetch = useCallback(async (f: SignalFilter) => {
    setLoading(true);
    setError(null);
    try {
      const res = await signals.list(f);
      setData(res.data.data ?? { items: [], page: 1, pages: 1, total: 0 });
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to load signals");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!prevFilters.current || !shallowEqual(prevFilters.current as Record<string, any>, filters as Record<string, any>)) {
      prevFilters.current = filters;
      fetch(filters);
    }
  }, [fetch, filters]);

  const refetch = useCallback(() => fetch(filters), [fetch, filters]);

  return { ...data, loading, error, refetch };
}

export function useSignal(id: number) {
  const [signal, setSignal] = useState<Signal | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    signals.get(id)
      .then((res) => setSignal(res.data.data ?? null))
      .catch((err) => setError(err.response?.data?.message || "Failed to load signal"))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { load(); }, [load]);

  return { signal, setSignal, loading, error, refetch: load };
}

export function useSignalStats() {
  const [stats, setStats] = useState<SignalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    signals.stats()
      .then((res) => setStats(res.data.data ?? null))
      .finally(() => setLoading(false));
  }, []);

  return { stats, loading };
}

export function useNearbySignals(lat: number, lng: number, radius = 1000) {
  const [data, setData] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!lat || !lng) return;
    setLoading(true);
    signals.nearby(lat, lng, radius)
      .then((res) => setData(res.data.data?.items ?? []))
      .finally(() => setLoading(false));
  }, [lat, lng, radius]);

  return { signals: data, loading };
}
