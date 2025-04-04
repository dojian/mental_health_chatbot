import { ChatRequest, ChatResponse } from '@/types/chat';
import { env } from './env';
import Cookies from 'js-cookie';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  console.log('Preparing chat message request:', JSON.stringify(request, null, 2));
  
  const token = Cookies.get(env.jwtStorageKey);
  console.log('Auth token present:', !!token);
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  console.log('Sending request to:', `/api/agent-chat`);
  
  const response = await fetch(`/api/agent-chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  });

  console.log('Response status:', response.status);
  
  if (!response.ok) {
    const errorData = await response.json();
    console.error('Error response:', errorData);
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log('Success response:', JSON.stringify(data, null, 2));
  
  return data;
} 