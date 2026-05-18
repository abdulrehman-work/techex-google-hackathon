import { useState, useEffect, useCallback } from "react";

/**
 * Generic hook to fetch data from the backend API.
 * - Calls `fetchFn` on mount and on every `refreshInterval` ms.
 * - Returns { data, loading, error, refetch }.
 */
export function useApi(fetchFn, deps = [], refreshInterval = 0) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    refetch();
    if (refreshInterval > 0) {
      const id = setInterval(refetch, refreshInterval);
      return () => clearInterval(id);
    }
  }, [refetch, refreshInterval]);

  return { data, loading, error, refetch };
}
