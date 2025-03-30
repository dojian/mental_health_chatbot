import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { env } from '@/utils/env';

interface ChatSession {
  session_id: string;
  session_name: string;
  last_interaction: string;
  created_at: string;
}

interface SessionSelectorProps {
  onSessionSelect: (sessionId: string | null) => void;
  currentSessionId: string | null;
}

export default function SessionSelector({ onSessionSelect, currentSessionId }: SessionSelectorProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Get the token from cookies
      const token = Cookies.get(env.jwtStorageKey);
      console.log('Token present:', !!token);
      
      if (!token) {
        throw new Error('No authentication token found');
      }

      console.log('Fetching recent sessions...');
      const response = await fetch('/api/chat/recent-sessions', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Failed to fetch sessions:', errorData);
        throw new Error(errorData.error || 'Failed to fetch sessions');
      }
      
      const data = await response.json();
      console.log('Raw data from API:', JSON.stringify(data, null, 2));
      
      // Ensure we have an array of sessions
      if (!Array.isArray(data)) {
        console.error('Received non-array data:', data);
        setSessions([]);
        return;
      }

      // Filter and validate sessions
      const validSessions = data.filter(session => {
        const isValid = session && 
          typeof session.session_id === 'string' &&
          typeof session.session_name === 'string' &&
          typeof session.last_interaction === 'string';
        
        if (!isValid) {
          console.warn('Invalid session data:', session);
        }
        
        return isValid;
      });

      // Sort sessions by last interaction, most recent first
      validSessions.sort((a, b) => {
        return new Date(b.last_interaction).getTime() - new Date(a.last_interaction).getTime();
      });

      console.log('Valid sessions:', JSON.stringify(validSessions, null, 2));
      setSessions(validSessions);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch sessions');
      setSessions([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch sessions when component mounts
  useEffect(() => {
    console.log('SessionSelector mounted, fetching sessions...');
    fetchSessions();

    // Listen for session updates
    const handleSessionUpdate = () => {
      console.log('Session update event received, refreshing sessions...');
      fetchSessions();
    };

    window.addEventListener('sessionUpdated', handleSessionUpdate);

    return () => {
      window.removeEventListener('sessionUpdated', handleSessionUpdate);
    };
  }, []);

  const handleNewChat = () => {
    console.log('Starting new chat...');
    onSessionSelect(null);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center p-4">
        <div data-testid="loading-spinner" className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-4">
        <p>Error loading sessions: {error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-800">Chat Sessions</h2>
        <button
          onClick={handleNewChat}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          New Chat
        </button>
      </div>
      <div className="space-y-2">
        {sessions.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No chat sessions found</p>
        ) : (
          sessions.map((session) => (
            <button
              key={session.session_id}
              onClick={() => onSessionSelect(session.session_id)}
              className={`w-full text-left p-3 rounded-lg transition-colors ${
                currentSessionId === session.session_id
                  ? 'bg-blue-100 text-blue-800'
                  : 'hover:bg-gray-100 text-gray-800'
              }`}
            >
              <div className="font-medium">{session.session_name}</div>
              <div className="text-sm text-gray-500">
                {new Date(session.last_interaction).toLocaleString()}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
} 