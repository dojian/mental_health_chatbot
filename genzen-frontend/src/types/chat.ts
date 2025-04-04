export interface ChatMessage {
  query: string;
  response: string;
  timestamp: Date;
  isUser: boolean;
}

export interface SessionMetadata {
  emotional_history: string[];
  topic_engagement: Record<string, number>;
  suggestion_enabled: boolean;
  last_memory_access?: string;
  memory_context?: any[];
}

export interface ChatRequest {
  query: string;
  session_id?: string | null;
  session_name?: string;
  session_metadata: SessionMetadata;
}

export interface ChatResponse {
  session_id: string;
  query: string;
  response: string;
}

export interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface Session {
    id: string;
    name: string;
} 