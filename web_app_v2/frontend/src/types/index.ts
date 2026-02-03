export interface Topic {
  id: string;
  name: string;
  level: number;
  difficulty: number;
  content: string;
  prerequisites: string[];
}

export interface BeliefState {
  alpha: number;
  beta: number;
  expected_lambda: number;
  variance: number;
  confidence_interval: [number, number];
}

export interface Session {
  session_id: string;
  mode: 'llm' | 'simple';
  current_topic: Topic;
  belief: BeliefState;
  total_answered: number;
  correct_count: number;
  accuracy: number;
  created_at: string;
  updated_at: string;
}

export interface APIConfig {
  api_key: string;
  base_url?: string;
  model: string;
}

export interface CreateSessionRequest {
  mode: 'llm' | 'simple';
  config?: APIConfig;
  target_questions: number;
}

export interface AnswerRequest {
  answer: string;
  use_llm: boolean;
}

export interface AnswerResponse {
  correct: boolean;
  feedback: string;
  llm_evaluation?: Record<string, any>;
  updated_belief: BeliefState;
  next_topic?: Topic;
  total_answered: number;
  correct_count: number;
  accuracy: number;
}

export interface BeliefHistoryItem {
  topic: string;
  correct: boolean;
  belief: BeliefState;
  timestamp: string;
}

export interface TopicHistoryItem {
  topic: string;
  level: number;
  correct: boolean;
  timestamp: string;
}

export interface ProgressData {
  belief_history: BeliefHistoryItem[];
  topic_history: TopicHistoryItem[];
  level_stats: Record<string, { total: number; correct: number }>;
  cumulative_accuracy: number[];
}

export interface KnowledgeGraphNode {
  id: string;
  name: string;
  level: number;
  difficulty: number;
  x: number;
  y: number;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
}

export interface KnowledgeGraphResponse {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

export interface DefaultConfig {
  base_url: string;
  model: string;
}

export interface AvailableModel {
  id: string;
  name: string;
}
