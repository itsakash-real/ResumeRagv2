

import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import api from '../services/api';

export function useMatches() {
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetch = useCallback(async ({ page = 1, limit = 10, min_score = 0, sort = 'score_desc' } = {}) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get('/matches', {
        params: { page, limit, min_score, sort },
      });
      setResults(data.results);
      setTotal(data.total);
      setPage(data.page);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to load history.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = async (matchId) => {
    try {
      await api.delete(`/matches/${matchId}`);
      setResults((prev) => prev.filter((r) => r.id !== matchId));
      setTotal((prev) => prev - 1);
      toast.success('Match deleted.');
    } catch (err) {
      toast.error('Could not delete match.');
    }
  };

  return { results, total, page, loading, error, fetch, remove };
}