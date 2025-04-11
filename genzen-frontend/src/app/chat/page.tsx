'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ChatMessage, ChatState, SessionMetadata, ChatRequest } from '@/types/chat';
import { sendChatMessage } from '@/utils/api';
import { env } from '@/utils/env';
import DisclaimerModal from '../layout-components/DisclaimerModal';
import SessionSelector from '../layout-components/SessionSelector';
import Cookies from 'js-cookie';
import { chatMessageSchema } from '@/lib/validations/chat';
import { ZodError } from 'zod';

export default function ChatPage() {
  const router = useRouter();
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    sessionId: null,
    isLoading: false,
    error: null,
  });
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatState.messages]);

  // Auto-focus input after message is sent
  useEffect(() => {
    if (!chatState.isLoading) {
      inputRef.current?.focus();
    }
  }, [chatState.isLoading]);

  const handleDisclaimerAccept = async () => {
    try {
      // Get the JWT token from cookies
      const token = Cookies.get(env.jwtStorageKey);
      
      // Submit pre-chat survey with disclaimer acceptance
      const response = await fetch(`/api/v1/pre-chat-survey`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          emotional_intensity: 1,
          selected_topics: [],
          suggestions_enabled: true,
          timestamp: new Date().toISOString(),
          user_disclaimer_accepted: true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit pre-chat survey');
      }

      setShowDisclaimer(false);
    } catch (error) {
      console.error('Error submitting pre-chat survey:', error);
      setShowDisclaimer(false);
    }
  };

  const handleSessionSelect = (sessionId: string | null) => {
    console.log('Session selected:', sessionId);
    setChatState(prev => ({
      ...prev,
      sessionId,
      messages: [], // Clear messages when switching sessions
      error: null,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || chatState.isLoading) return;

    try {
      const now = new Date();
      // Format the date as YYYY-MM-DD
      const formattedDate = now.toISOString().split('T')[0];

      const sessionMetadata: SessionMetadata = {
        emotional_history: [],
        topic_engagement: {},
        suggestion_enabled: true,
        last_memory_access: formattedDate,
        memory_context: [],
      };

      // Prepare and validate the request payload
      const requestPayload: ChatRequest = {
        query: inputMessage,
        session_metadata: sessionMetadata,
        session_id: chatState.sessionId,
        ...(chatState.sessionId ? {} : { session_name: inputMessage.slice(0, 100) }),
      };

      // Validate the payload
      const validatedPayload = chatMessageSchema.parse(requestPayload);

      const userMessage: ChatMessage = {
        query: validatedPayload.query,
        response: '',
        timestamp: new Date(),
        isUser: true,
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      setInputMessage('');

      const response = await sendChatMessage(validatedPayload);

      const botMessage: ChatMessage = {
        query: response.query,
        response: response.response,
        timestamp: new Date(),
        isUser: false,
      };

      // Update chat state with new session ID and messages
      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, botMessage],
        sessionId: response.session_id,
        isLoading: false,
      }));

      // Force a refresh of the session list
      const event = new CustomEvent('sessionUpdated', {
        detail: { sessionId: response.session_id }
      });
      window.dispatchEvent(event);
      
      // Also fetch sessions directly after a short delay to ensure backend has processed the update
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('sessionUpdated'));
      }, 1000);
    } catch (err) {
      console.error('Error in handleSubmit:', err);
      let errorMessage = 'An error occurred';
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err instanceof ZodError) {
        errorMessage = err.errors[0]?.message || 'Invalid message format';
      }
      setChatState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  };

  if (showDisclaimer) {
    return <DisclaimerModal isOpen={showDisclaimer} onAccept={handleDisclaimerAccept} />;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <SessionSelector
        onSessionSelect={handleSessionSelect}
        currentSessionId={chatState.sessionId}
      />
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatState.messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.isUser
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.response || message.query}</p>
              <p className="text-xs mt-2 opacity-70">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {chatState.isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-lg p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        {chatState.error && (
          <div className="flex justify-center">
            <div className="bg-red-100 text-red-700 rounded-lg p-4">
              {chatState.error}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex space-x-4">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            disabled={chatState.isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || chatState.isLoading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
} 