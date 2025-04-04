import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SessionSelector from '../SessionSelector';
import Cookies from 'js-cookie';

// Mock js-cookie
jest.mock('js-cookie');

describe('SessionSelector', () => {
    const mockOnSessionSelect = jest.fn();
    const mockSessions = {
        data: [
            { id: '1', name: 'Test Session 1' },
            { id: '2', name: 'Test Session 2' }
        ]
    };

    beforeEach(() => {
        jest.clearAllMocks();
        // Mock the token
        (Cookies.get as jest.Mock).mockReturnValue('test-token');
        // Mock successful API response by default
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: () => Promise.resolve(mockSessions)
        });
    });

    it('shows loading state initially', () => {
        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);
        expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('displays sessions after loading', async () => {
        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

        await waitFor(() => {
            expect(screen.getByText('Test Session 1')).toBeInTheDocument();
            expect(screen.getByText('Test Session 2')).toBeInTheDocument();
        });
    });

    it('handles session selection', async () => {
        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

        await waitFor(() => {
            expect(screen.getByText('Test Session 1')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('Test Session 1'));
        expect(mockOnSessionSelect).toHaveBeenCalledWith('1');
    });

    it('handles new chat button click', async () => {
        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

        await waitFor(() => {
            expect(screen.getByText('New Chat')).toBeInTheDocument();
        });

        fireEvent.click(screen.getByText('New Chat'));
        expect(mockOnSessionSelect).toHaveBeenCalledWith(null);
    });

    it('highlights current session', async () => {
        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId="1" />);

        await waitFor(() => {
            const sessionButton = screen.getByText('Test Session 1').closest('button');
            expect(sessionButton).toHaveClass('bg-blue-100');
        });
    });

    it('handles fetch error gracefully', async () => {
        // Mock a failed API response
        global.fetch = jest.fn().mockRejectedValue(new Error('Failed to fetch'));

        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

        await waitFor(() => {
            expect(screen.getByText(/error loading sessions/i)).toBeInTheDocument();
        });
    });

    it('handles missing token gracefully', async () => {
        // Mock missing token
        (Cookies.get as jest.Mock).mockReturnValue(null);

        render(<SessionSelector onSessionSelect={mockOnSessionSelect} currentSessionId={null} />);

        await waitFor(() => {
            expect(screen.getByText(/no authentication token found/i)).toBeInTheDocument();
        });
    });
}); 