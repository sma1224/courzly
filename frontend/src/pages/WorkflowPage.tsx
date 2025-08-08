import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { workflowsApi, contentApi } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import WorkflowStatus from '../components/workflow/WorkflowStatus';
import ContentEditor from '../components/editor/ContentEditor';
import ChatInterface from '../components/chat/ChatInterface';
import ApprovalDashboard from '../components/workflow/ApprovalDashboard';

const WorkflowPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'content' | 'chat' | 'approvals'>('content');

  const { data: workflow, refetch: refetchWorkflow } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => workflowsApi.getStatus(id!),
    enabled: !!id,
    refetchInterval: 5000
  });

  const { data: content, refetch: refetchContent } = useQuery({
    queryKey: ['content', id],
    queryFn: () => contentApi.getWorkflowContent(id!),
    enabled: !!id
  });

  useWebSocket({
    workflowId: id!,
    onStatusUpdate: () => {
      refetchWorkflow();
      refetchContent();
    }
  });

  if (!workflow) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{workflow.title}</h1>
          <p className="text-gray-600">{workflow.description}</p>
        </div>
        <WorkflowStatus workflow={workflow} />
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'content', label: 'Content', count: content?.length },
            { key: 'chat', label: 'Chat' },
            { key: 'approvals', label: 'Approvals' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
              {tab.count && (
                <span className="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'content' && (
          <ContentEditor workflowId={id!} content={content || []} />
        )}
        {activeTab === 'chat' && (
          <ChatInterface workflowId={id!} />
        )}
        {activeTab === 'approvals' && (
          <ApprovalDashboard workflowId={id!} />
        )}
      </div>
    </div>
  );
};

export default WorkflowPage;