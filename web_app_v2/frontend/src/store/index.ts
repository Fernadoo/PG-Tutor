import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  Session,
  Topic,
  BeliefState,
  AnswerResponse,
  ProgressData,
  APIConfig,
} from '@/types';

interface AppState {
  // Session
  session: Session | null;
  setSession: (session: Session | null) => void;
  
  // Current answer
  currentAnswer: string;
  setCurrentAnswer: (answer: string) => void;
  
  // Loading states
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  // Error
  error: string | null;
  setError: (error: string | null) => void;
  
  // Answer result
  lastAnswer: AnswerResponse | null;
  setLastAnswer: (answer: AnswerResponse | null) => void;
  clearLastAnswer: () => void;
  
  // Progress
  progress: ProgressData | null;
  setProgress: (progress: ProgressData | null) => void;
  
  // Config
  apiConfig: APIConfig | null;
  setApiConfig: (config: APIConfig | null) => void;
  
  // Mode
  mode: 'llm' | 'simple';
  setMode: (mode: 'llm' | 'simple') => void;
  
  // Reset all
  reset: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      session: null,
      setSession: (session) => set({ session }),
      
      currentAnswer: '',
      setCurrentAnswer: (answer) => set({ currentAnswer: answer }),
      
      isLoading: false,
      setIsLoading: (isLoading) => set({ isLoading }),
      
      error: null,
      setError: (error) => set({ error }),
      
      lastAnswer: null,
      setLastAnswer: (lastAnswer) => set({ lastAnswer }),
      clearLastAnswer: () => set({ lastAnswer: null, currentAnswer: '' }),
      
      progress: null,
      setProgress: (progress) => set({ progress }),
      
      apiConfig: null,
      setApiConfig: (apiConfig) => set({ apiConfig }),
      
      mode: 'simple',
      setMode: (mode) => set({ mode }),
      
      reset: () => set({
        session: null,
        currentAnswer: '',
        isLoading: false,
        error: null,
        lastAnswer: null,
        progress: null,
        apiConfig: null,
        mode: 'simple',
      }),
    }),
    {
      name: 'ai-tutor-storage',
      partialize: (state) => ({
        session: state.session,
        mode: state.mode,
      }),
    }
  )
);
