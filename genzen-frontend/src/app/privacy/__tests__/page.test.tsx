import { render, screen } from '@testing-library/react';
import PrivacyPage from '../page';

// Mock the fetch function
global.fetch = jest.fn();

describe('PrivacyPage', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should render privacy content', async () => {
    // Mock the YAML content
    const mockContent = {
      title: 'Privacy Policy',
      lastUpdated: '2024-03-20',
      sections: [
        {
          title: 'Introduction',
          content: 'Test introduction content'
        }
      ]
    };

    // Mock the fetch response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(JSON.stringify(mockContent))
    });

    render(<PrivacyPage />);

    // Check for content
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    expect(screen.getByText('Introduction')).toBeInTheDocument();
    expect(screen.getByText('Test introduction content')).toBeInTheDocument();
  });
}); 