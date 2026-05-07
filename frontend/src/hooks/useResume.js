

import { useState } from 'react';
import toast from 'react-hot-toast';
import api from '../services/api';

export function useResume() {
  const [uploading, setUploading] = useState(false);
  const [matching, setMatching] = useState(false);
  const [resumeId, setResumeId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [error, setError] = useState(null);

  const upload = async (file) => {
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await api.post('/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResumeId(data.resume_id);
      return data.resume_id;
    } catch (err) {
      const detail = err.response?.data?.detail || 'Upload failed.';
      setError(detail);
      throw err;
    } finally {
      setUploading(false);
    }
  };

  const match = async (id) => {
    setMatching(true);
    setError(null);
    try {
      const { data } = await api.post('/resume/match', { resume_id: id });
      setProfile(data.profile);
      setMatches(data.matches);
      toast.success(`Matched ${data.matches.length} jobs!`);
      return data;
    } catch (err) {
      const detail = err.response?.data?.detail || 'Matching failed.';
      setError(detail);
      throw err;
    } finally {
      setMatching(false);
    }
  };

  const reset = () => {
    setResumeId(null);
    setProfile(null);
    setMatches([]);
    setError(null);
    setUploading(false);
    setMatching(false);
  };

  return { upload, match, reset, uploading, matching, resumeId, profile, matches, error };
}