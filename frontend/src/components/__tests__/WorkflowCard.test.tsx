import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import WorkflowCard from '../workflow/WorkflowCard';
import { Workflow } from '../../types';

const mockWorkflow: Workflow = {
  id: 'test-workflow-id',
  title: 'Test Course',
  description: 'Test course description',
  status: 'running',
  current_stage: 'content_generation',
  created_at: '2024-01-01T00:00:00Z',
  config: {
    target_audience: 'Developers'
  }
};

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('WorkflowCard', () => {
  it('renders workflow information correctly', () => {
    renderWithProviders(<WorkflowCard workflow={mockWorkflow} />);
    
    expect(screen.getByText('Test Course')).toBeInTheDocument();
    expect(screen.getByText('Test course description')).toBeInTheDocument();
    expect(screen.getByText('running')).toBeInTheDocument();
    expect(screen.getByText('Developers')).toBeInTheDocument();
  });

  it('displays correct status color for running workflow', () => {
    renderWithProviders(<WorkflowCard workflow={mockWorkflow} />);
    
    const statusBadge = screen.getByText('running');
    expect(statusBadge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('shows correct progress for current stage', () => {
    renderWithProviders(<WorkflowCard workflow={mockWorkflow} />);
    
    // content_generation is stage 2 of 5, so 40% progress
    const progressBar = document.querySelector('.bg-primary-600');
    expect(progressBar).toHaveStyle('width: 40%');
  });

  it('displays stage information', () => {
    renderWithProviders(<WorkflowCard workflow={mockWorkflow} />);
    
    expect(screen.getByText('Stage:')).toBeInTheDocument();
    expect(screen.getByText('content generation')).toBeInTheDocument();
  });

  it('renders as a clickable link', () => {
    renderWithProviders(<WorkflowCard workflow={mockWorkflow} />);
    
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/workflow/test-workflow-id');
  });

  it('handles workflow without description', () => {
    const workflowWithoutDesc = { ...mockWorkflow, description: undefined };
    renderWithProviders(<WorkflowCard workflow={workflowWithoutDesc} />);
    
    expect(screen.getByText('Test Course')).toBeInTheDocument();
    expect(screen.queryByText('Test course description')).not.toBeInTheDocument();
  });

  it('displays different status colors correctly', () => {
    const completedWorkflow = { ...mockWorkflow, status: 'completed' as const };
    renderWithProviders(<WorkflowCard workflow={completedWorkflow} />);
    
    const statusBadge = screen.getByText('completed');
    expect(statusBadge).toHaveClass('bg-green-100', 'text-green-800');
  });
});