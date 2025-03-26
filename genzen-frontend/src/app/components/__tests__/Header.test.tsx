import { render, screen, fireEvent } from '@testing-library/react';
import Header from '../Header';

describe('Header Component', () => {
  it('renders navigation links', () => {
    render(<Header />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Privacy')).toBeInTheDocument();
  });

  it('toggles login/logout state when button is clicked', () => {
    render(<Header />);

    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);
    expect(screen.getByText('Logout')).toBeInTheDocument();

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    expect(screen.getByText('Login')).toBeInTheDocument();
  });
}); 