import { useCallback } from 'react';
import { useStore } from '@/store';
import { sessionApi } from '@/api/client';

export function useSession() {
  const { 
    session, 
    setSession, 
    setIsLoading, 
    setError,
    setLastAnswer,
    setProgress,
  } = useStore();

  const refreshSession = useCallback(async () => {
    if (!session?.session_id) return;
    
    setIsLoading(true);
    try {
      const updatedSession = await sessionApi.get(session.session_id);
      setSession(updatedSession);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh session');
    } finally {
      setIsLoading(false);
    }
  }, [session?.session_id, setSession, setIsLoading, setError]);

  const submitAnswer = useCallback(async (answer: string, useLlm: boolean = false) => {
    if (!session?.session_id) return null;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await sessionApi.submitAnswer(session.session_id, {
        answer,
        use_llm: useLlm,
      });
      
      setLastAnswer(response);
      
      if (response.next_topic) {
        setSession({
          ...session,
          current_topic: response.next_topic,
          belief: response.updated_belief,
          total_answered: response.total_answered,
          correct_count: response.correct_count,
          accuracy: response.accuracy,
        });
      } else {
        setSession({
          ...session,
          belief: response.updated_belief,
          total_answered: response.total_answered,
          correct_count: response.correct_count,
          accuracy: response.accuracy,
        });
      }
      
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [session, setSession, setIsLoading, setError, setLastAnswer]);

  const loadProgress = useCallback(async () => {
    if (!session?.session_id) return null;
    
    setIsLoading(true);
    try {
      const progress = await sessionApi.getProgress(session.session_id);
      setProgress(progress);
      return progress;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load progress');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [session?.session_id, setProgress, setIsLoading, setError]);

  const resetSession = useCallback(async () => {
    if (!session?.session_id) return;
    
    setIsLoading(true);
    try {
      await sessionApi.reset(session.session_id);
      await refreshSession();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset session');
    } finally {
      setIsLoading(false);
    }
  }, [session?.session_id, refreshSession, setIsLoading, setError]);

  return {
    session,
    refreshSession,
    submitAnswer,
    loadProgress,
    resetSession,
  };
}
