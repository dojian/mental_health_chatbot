'use client';

import { useState, useRef, useEffect } from 'react';
import { ChatMessage, ChatState, SessionMetadata } from '@/types/chat';
import { sendChatMessage } from '@/utils/api';

export default function ChatPage() {
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || chatState.isLoading) return;

    const userMessage: ChatMessage = {
      query: inputMessage,
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

    try {
      const sessionMetadata: SessionMetadata = {
        emotional_history: [],
        topic_engagement: {},
        suggestion_enabled: true,
        last_memory_access: new Date().toISOString(),
        memory_context: [],
      };

      const response = await sendChatMessage({
        query: inputMessage,
        session_id: chatState.sessionId,
        session_metadata: sessionMetadata,
      });

      const botMessage: ChatMessage = {
        query: response.query,
        response: response.response,
        timestamp: new Date(),
        isUser: false,
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, botMessage],
        sessionId: response.session_id,
        isLoading: false,
      }));
    } catch (error) {
      setChatState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      }));
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
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