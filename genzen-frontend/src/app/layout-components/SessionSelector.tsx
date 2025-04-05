import { useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import { Session } from '@/types/chat';

interface SessionSelectorProps {
    onSessionSelect: (sessionId: string | null) => void;
    currentSessionId: string | null;
}

export default function SessionSelector({ onSessionSelect, currentSessionId }: SessionSelectorProps) {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchSessions = async () => {
        try {
            const token = Cookies.get('token');
            if (!token) {
                throw new Error('No authentication token found');
            }

            // console.log('Fetching sessions with token:', token ? 'token exists' : 'no token');
            
            const response = await fetch('/api/v1/chat/recent-sessions?limit=2', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            // console.log('Response status:', response.status);
            // console.log('Response headers:', Object.fromEntries(response.headers.entries()));
            
            const responseText = await response.text();
            // console.log('Raw response text:', responseText);
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                // console.log('Parsed response data:', responseData);
            } catch (e) {
                console.error('Failed to parse response as JSON:', e);
                throw new Error('Invalid JSON response');
            }

            if (!response.ok) {
                throw new Error(`Failed to fetch sessions: ${response.status} ${response.statusText}`);
            }

            if (!responseData || !Array.isArray(responseData)) {
                console.error('Invalid response format:', responseData);
                throw new Error('Invalid response format');
            }

            const validSessions = responseData.map((session: any) => ({
                id: session.session_id,
                name: session.session_name,
            }));
            // console.log('Valid sessions:', validSessions);
            setSessions(validSessions);
        } catch (error) {
            console.error('Error in fetchSessions:', error);
            setError(error instanceof Error ? error.message : 'Failed to fetch sessions');
            setSessions([]);
        } finally {
            setIsLoading(false);
        }
    };

    // useEffect(() => {
    //     fetchSessions();
    // }, []);

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

    if (error) {
        return (
            <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-4">
                <p>Error loading sessions: {error}</p>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div role="status" className="flex justify-center items-center p-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">

            {/* Button to create a new chat */}
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-800">Chat Sessions</h2>
                <button
                onClick={handleNewChat}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                 New Chat
                </button>
            </div>

            {/* List of chat sessions */}
            <div className="space-y-2">
                {sessions.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No chat sessions found</p>
                ) : (
                sessions.map((session) => (
                    <button
                        key={session.id}
                        onClick={() => onSessionSelect(session.id)}
                        className={`w-full text-left p-3 rounded-lg transition-colors ${
                            currentSessionId === session.id
                            ? 'bg-blue-100 text-blue-800'
                            : 'hover:bg-gray-100 text-gray-800'
                        }`}
                    >
                    <div className="font-medium">{session.name}</div>
                    </button>
                ))
                )}
            </div>
        </div>
    );
} 