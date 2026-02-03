import axios from 'axios';
import {
  CreateSessionRequest,
  Session,
  AnswerRequest,
  AnswerResponse,
  ProgressData,
  BeliefState,
  Topic,
  KnowledgeGraphResponse,
  DefaultConfig,
  AvailableModel,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sessions API
export const sessionApi = {
  create: async (data: CreateSessionRequest): Promise<Session> => {
    const response = await api.post<Session>('/sessions/create', data);
    return response.data;
  },

  get: async (sessionId: string): Promise<Session> => {
    const response = await api.get<Session>(`/sessions/${sessionId}`);
    return response.data;
  },

  submitAnswer: async (
    sessionId: string,
    data: AnswerRequest
  ): Promise<AnswerResponse> => {
    const response = await api.post<AnswerResponse>(
      `/sessions/${sessionId}/answer`,
      data
    );
    return response.data;
  },

  getProgress: async (sessionId: string): Promise<ProgressData> => {
    const response = await api.get<ProgressData>(`/sessions/${sessionId}/progress`);
    return response.data;
  },

  getBelief: async (sessionId: string): Promise<BeliefState> => {
    const response = await api.get<BeliefState>(`/sessions/${sessionId}/belief`);
    return response.data;
  },

  getLesson: async (sessionId: string): Promise<{ topic: any; lesson_content: string; mode: string }> => {
    const response = await api.get(`/sessions/${sessionId}/lesson`);
    return response.data;
  },

  reset: async (sessionId: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>(`/sessions/${sessionId}/reset`);
    return response.data;
  },

  delete: async (sessionId: string): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/sessions/${sessionId}`);
    return response.data;
  },
};

// Topics API
export const topicApi = {
  list: async (level?: number): Promise<Topic[]> => {
    const response = await api.get<Topic[]>('/topics/list', {
      params: level !== undefined ? { level } : undefined,
    });
    return response.data;
  },

  get: async (topicId: string): Promise<Topic> => {
    const response = await api.get<Topic>(`/topics/${topicId}`);
    return response.data;
  },

  getGraph: async (): Promise<KnowledgeGraphResponse> => {
    const response = await api.get<KnowledgeGraphResponse>('/topics/graph/visualization');
    return response.data;
  },
};

// Config API
export const configApi = {
  getDefaults: async (): Promise<DefaultConfig> => {
    const response = await api.get<DefaultConfig>('/config/defaults');
    return response.data;
  },

  getModels: async (): Promise<{ models: AvailableModel[] }> => {
    const response = await api.get<{ models: AvailableModel[] }>('/config/models');
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const response = await axios.get<{ status: string }>(`${API_BASE_URL}/health`);
    return response.data;
  },
};

export default api;
