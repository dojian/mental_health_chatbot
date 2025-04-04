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

            const response = await fetch('/api/sessions', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch sessions');
            }

            const { data } = await response.json();
            if (!Array.isArray(data)) {
                throw new Error('Invalid response format');
            }

            const validSessions = data.map((session: any) => ({
                id: session.id,
                name: session.name,
            }));
            setSessions(validSessions);
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to fetch sessions');
            setSessions([]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

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
        <div className="space-y-4">
            <h2 className="text-lg font-semibold mb-4">Chat Sessions</h2>
            <button
                onClick={() => onSessionSelect(null)}
                className={`w-full text-left px-4 py-2 rounded-lg ${!currentSessionId ? 'bg-blue-100' : 'hover:bg-gray-100'}`}
            >
                New Chat
            </button>
            {sessions.map((session) => (
                <button
                    key={session.id}
                    onClick={() => onSessionSelect(session.id)}
                    className={`w-full text-left px-4 py-2 rounded-lg ${currentSessionId === session.id ? 'bg-blue-100' : 'hover:bg-gray-100'}`}
                >
                    {session.name}
                </button>
            ))}
        </div>
    );
} 