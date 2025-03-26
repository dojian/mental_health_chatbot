import { ChatRequest, ChatResponse } from '@/types/chat';
import { env } from './env';
import Cookies from 'js-cookie';

const API_BASE_URL = 'http://localhost:8001/v1';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = Cookies.get(env.jwtStorageKey);
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await fetch(`${API_BASE_URL}/agent-chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
} 