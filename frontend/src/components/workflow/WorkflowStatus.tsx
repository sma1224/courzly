import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlayIcon, 
  PauseIcon, 
  StopIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { Workflow } from '../../types';
import { workflowsApi } from '../../services/api';
import toast from 'react-hot-toast';

interface WorkflowStatusProps {
  workflow: Workflow;
}

const WorkflowStatus: React.FC<WorkflowStatusProps> = ({ workflow }) => {
  const queryClient = useQueryClient();

  const resumeMutation = useMutation({
    mutationFn: () => workflowsApi.resume(workflow.id),
    onSuccess: () => {
      toast.success('Workflow resumed');
      queryClient.invalidateQueries({ queryKey: ['workflow', workflow.id] });
    },
    onError: () => toast.error('Failed to resume workflow')
  });

  const pauseMutation = useMutation({
    mutationFn: () => workflowsApi.pause(workflow.id),
    onSuccess: () => {
      toast.success('Workflow paused');
      queryClient.invalidateQueries({ queryKey: ['workflow', workflow.id] });
    },
    onError: () => toast.error('Failed to pause workflow')
  });

  const getStatusIcon = () => {
    switch (workflow.status) {
      case 'running':
        return <PlayIcon className="w-5 h-5 text-blue-600" />;
      case 'paused':
      case 'waiting_approval':
        return <PauseIcon className="w-5 h-5 text-yellow-600" />;
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />;
      default:
        return <ArrowPathIcon className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = () => {
    switch (workflow.status) {
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'paused':
      case 'waiting_approval':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStageProgress = () => {
    const stages = ['outline', 'content_generation', 'review', 'final_assembly', 'export'];
    const currentIndex = stages.indexOf(workflow.current_stage);
    return ((currentIndex + 1) / stages.length) * 100;
  };

  const canResume = workflow.status === 'paused' || workflow.status === 'waiting_approval';
  const canPause = workflow.status === 'running';

  return (
    <div className="bg-white border rounded-lg p-4 min-w-[300px]">
      {/* Status Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getStatusColor()}`}>
            {workflow.status.replace('_', ' ')}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {canResume && (
            <button
              onClick={() => resumeMutation.mutate()}
              disabled={resumeMutation.isPending}
              className="p-2 text-green-600 hover:bg-green-50 rounded-lg"
              title="Resume workflow"
            >
              <PlayIcon className="w-5 h-5" />
            </button>
          )}
          
          {canPause && (
            <button
              onClick={() => pauseMutation.mutate()}
              disabled={pauseMutation.isPending}
              className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg"
              title="Pause workflow"
            >
              <PauseIcon className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Progress */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{Math.round(getStageProgress())}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getStageProgress()}%` }}
          />
        </div>
      </div>

      {/* Current Stage */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Current Stage:</span>
          <span className="font-medium capitalize">
            {workflow.current_stage.replace('_', ' ')}
          </span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Created:</span>
          <span>{new Date(workflow.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Stage Timeline */}
      <div className="mt-4 pt-4 border-t">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Workflow Stages</h4>
        <div className="space-y-2">
          {[
            { key: 'outline', label: 'Outline Creation' },
            { key: 'content_generation', label: 'Content Generation' },
            { key: 'review', label: 'Review & Approval' },
            { key: 'final_assembly', label: 'Final Assembly' },
            { key: 'export', label: 'Export & Publish' }
          ].map((stage, index) => {
            const stages = ['outline', 'content_generation', 'review', 'final_assembly', 'export'];
            const currentIndex = stages.indexOf(workflow.current_stage);
            const isCompleted = index < currentIndex;
            const isCurrent = index === currentIndex;
            
            return (
              <div key={stage.key} className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  isCompleted 
                    ? 'bg-green-500' 
                    : isCurrent 
                      ? 'bg-primary-500' 
                      : 'bg-gray-300'
                }`} />
                <span className={`text-sm ${
                  isCurrent ? 'font-medium text-primary-600' : 'text-gray-600'
                }`}>
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default WorkflowStatus;