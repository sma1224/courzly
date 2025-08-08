import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { PlusIcon, PlayIcon, PauseIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { workflowsApi } from '../services/api';
import { Workflow } from '../types';
import CreateWorkflowModal from '../components/workflow/CreateWorkflowModal';
import WorkflowCard from '../components/workflow/WorkflowCard';

const DashboardPage: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: workflows, isLoading, refetch } = useQuery({
    queryKey: ['workflows'],
    queryFn: async () => {
      // This would be a list endpoint in the real API
      return [] as Workflow[];
    }
  });

  const handleWorkflowCreated = () => {
    setShowCreateModal(false);
    refetch();
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Course Workflows</h1>
          <p className="text-gray-600">Create and manage your AI-powered course creation workflows</p>
        </div>
        
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Course</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <PlayIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active</p>
              <p className="text-2xl font-semibold text-gray-900">3</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <PauseIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Review</p>
              <p className="text-2xl font-semibold text-gray-900">2</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-semibold text-gray-900">8</p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-gray-100 rounded-lg">
              <PlusIcon className="h-6 w-6 text-gray-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-2xl font-semibold text-gray-900">13</p>
            </div>
          </div>
        </div>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows?.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-gray-400 mb-4">
              <PlusIcon className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No workflows yet</h3>
            <p className="text-gray-600 mb-4">Get started by creating your first course workflow</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              Create Your First Course
            </button>
          </div>
        ) : (
          workflows?.map((workflow) => (
            <WorkflowCard key={workflow.id} workflow={workflow} />
          ))
        )}
      </div>

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <CreateWorkflowModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleWorkflowCreated}
        />
      )}
    </div>
  );
};

export default DashboardPage;