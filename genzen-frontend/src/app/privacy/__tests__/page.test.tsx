import { render, screen } from '@testing-library/react';
import Privacy from '../page';
import { getPrivacyContent } from '@/utils/content';

// Mock the content function
jest.mock('@/utils/content', () => ({
  getPrivacyContent: jest.fn(),
}));

describe('PrivacyPage', () => {
  const mockPrivacyContent = {
    title: 'Privacy Policy',
    lastUpdated: '2024-03-20',
    sections: [
      {
        title: 'Section 1',
        content: 'Content 1',
      },
      {
        title: 'Section 2',
        content: 'Content 2',
      },
    ],
  };

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Setup default mock implementation
    (getPrivacyContent as jest.Mock).mockResolvedValue(mockPrivacyContent);
  });

  it('should render privacy content', async () => {
    render(await Privacy());

    // Check for content
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    expect(screen.getByText('Last updated: 2024-03-20')).toBeInTheDocument();
    expect(screen.getByText('Section 1')).toBeInTheDocument();
    expect(screen.getByText('Content 1')).toBeInTheDocument();
    expect(screen.getByText('Section 2')).toBeInTheDocument();
    expect(screen.getByText('Content 2')).toBeInTheDocument();
  });
}); 