import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import DelegationLogPanel from './promethiosfrontend/src/DelegationLogPanel';

// Mock axios
const mockAxios = new MockAdapter(axios);

// Sample log data
const mockLogs = [
  {
    timestamp: 1713369600,
    formatted_time: '2025-04-17 14:00:00',
    agent: 'HAL',
    event: 'Starting execution with task: Create project structure',
    project_id: 'test-project'
  },
  {
    timestamp: 1713369660,
    formatted_time: '2025-04-17 14:01:00',
    agent: 'NOVA',
    event: 'Analyzing HAL output for UI components',
    project_id: 'test-project'
  },
  {
    timestamp: 1713369720,
    formatted_time: '2025-04-17 14:02:00',
    agent: 'CRITIC',
    event: 'Reviewing project structure and components',
    project_id: 'test-project'
  }
];

describe('DelegationLogPanel Component', () => {
  beforeEach(() => {
    mockAxios.reset();
    // Mock successful response
    mockAxios.onGet('/api/system/log?project_id=test-project').reply(200, {
      status: 'success',
      logs: mockLogs,
      count: mockLogs.length
    });
  });

  test('renders delegation log panel with logs', async () => {
    render(<DelegationLogPanel projectId="test-project" />);
    
    // Check loading state
    expect(screen.getByText(/Loading logs/i)).toBeInTheDocument();
    
    // Wait for logs to load
    await waitFor(() => {
      expect(screen.getByText('HAL')).toBeInTheDocument();
      expect(screen.getByText('NOVA')).toBeInTheDocument();
      expect(screen.getByText('CRITIC')).toBeInTheDocument();
    });
    
    // Check log content
    expect(screen.getByText('Starting execution with task: Create project structure')).toBeInTheDocument();
    expect(screen.getByText('Analyzing HAL output for UI components')).toBeInTheDocument();
    expect(screen.getByText('Reviewing project structure and components')).toBeInTheDocument();
  });

  test('handles error state', async () => {
    mockAxios.onGet('/api/system/log?project_id=error-test').reply(500, {
      status: 'error',
      message: 'Internal server error'
    });
    
    render(<DelegationLogPanel projectId="error-test" />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading logs/i)).toBeInTheDocument();
    });
  });

  test('handles empty logs', async () => {
    mockAxios.onGet('/api/system/log?project_id=empty-test').reply(200, {
      status: 'success',
      logs: [],
      count: 0
    });
    
    render(<DelegationLogPanel projectId="empty-test" />);
    
    await waitFor(() => {
      expect(screen.getByText(/No delegation logs available/i)).toBeInTheDocument();
    });
  });

  test('applies agent-specific styling', async () => {
    render(<DelegationLogPanel projectId="test-project" />);
    
    await waitFor(() => {
      const halElement = screen.getByText('HAL');
      const novaElement = screen.getByText('NOVA');
      const criticElement = screen.getByText('CRITIC');
      
      expect(halElement.classList.contains('agent-hal')).toBe(true);
      expect(novaElement.classList.contains('agent-nova')).toBe(true);
      expect(criticElement.classList.contains('agent-critic')).toBe(true);
    });
  });
});
