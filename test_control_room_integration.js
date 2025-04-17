import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import ControlRoom from './promethiosfrontend/src/ControlRoom';

// Mock the components that are used in ControlRoom
jest.mock('./promethiosfrontend/src/AgentSidebar', () => () => <div data-testid="agent-sidebar">Sidebar</div>);
jest.mock('./promethiosfrontend/src/AgentOutputCard', () => ({ title, content }) => (
  <div data-testid="agent-output-card">{title}: {content}</div>
));
jest.mock('./promethiosfrontend/src/CriticOutputCard', () => ({ score, feedback }) => (
  <div data-testid="critic-output-card">Score: {score}, Feedback: {feedback}</div>
));
jest.mock('./promethiosfrontend/src/AgentChatPanel', () => () => <div data-testid="agent-chat-panel">Chat Panel</div>);
jest.mock('./promethiosfrontend/src/AgentInputBar', () => () => <div data-testid="agent-input-bar">Input Bar</div>);
jest.mock('./promethiosfrontend/src/TerminalDrawer', () => () => <div data-testid="terminal-drawer">Terminal</div>);
jest.mock('./promethiosfrontend/src/ThemeToggle', () => () => <div data-testid="theme-toggle">Theme Toggle</div>);
jest.mock('./promethiosfrontend/src/SystemStatusPanel', () => ({ projectId }) => (
  <div data-testid="system-status-panel">Status Panel for {projectId}</div>
));
jest.mock('./promethiosfrontend/src/SystemSummaryPanel', () => ({ projectId }) => (
  <div data-testid="system-summary-panel">Summary Panel for {projectId}</div>
));

// Mock fetch
global.fetch = jest.fn();

describe('ControlRoom', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    fetch.mockClear();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders loading state initially', () => {
    render(<ControlRoom />);
    expect(screen.getByText('Loading agent thread...')).toBeInTheDocument();
  });

  it('renders all components after loading', async () => {
    render(<ControlRoom />);
    
    // Fast-forward timers to trigger the setTimeout in useEffect
    jest.advanceTimersByTime(1000);
    
    await waitFor(() => {
      // Check for header
      expect(screen.getByText('🧠 Promethios Control Room')).toBeInTheDocument();
      
      // Check for system panels
      expect(screen.getByTestId('system-status-panel')).toBeInTheDocument();
      expect(screen.getByTestId('system-summary-panel')).toBeInTheDocument();
      
      // Check for agent output cards
      expect(screen.getByTestId('agent-output-card')).toBeInTheDocument();
      expect(screen.getByTestId('critic-output-card')).toBeInTheDocument();
      
      // Check for chat panel and input bar
      expect(screen.getByTestId('agent-chat-panel')).toBeInTheDocument();
      expect(screen.getByTestId('agent-input-bar')).toBeInTheDocument();
      
      // Check for sidebar and other UI elements
      expect(screen.getByTestId('agent-sidebar')).toBeInTheDocument();
      expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
      expect(screen.getByTestId('terminal-drawer')).toBeInTheDocument();
    });
  });

  it('passes the correct project ID to system panels', async () => {
    render(<ControlRoom />);
    
    // Fast-forward timers to trigger the setTimeout in useEffect
    jest.advanceTimersByTime(1000);
    
    await waitFor(() => {
      expect(screen.getByText('Status Panel for founder-stack')).toBeInTheDocument();
      expect(screen.getByText('Summary Panel for founder-stack')).toBeInTheDocument();
    });
  });
});
