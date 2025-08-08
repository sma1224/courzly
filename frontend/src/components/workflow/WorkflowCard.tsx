import React from 'react';
import { Link } from 'react-router-dom';
import { 
  PlayIcon, 
  PauseIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';
import { Workflow } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface WorkflowCardProps {
  workflow: Workflow;
}

const WorkflowCard: React.FC<WorkflowCardProps> = ({ workflow }) => {
  const getStatusIcon = () => {
    switch (workflow.status) {
      case 'running':
        return <PlayIcon className="h-5 w-5 text-blue-600" />;
      case 'paused':
      case 'waiting_approval':
        return <PauseIcon className="h-5 w-5 text-yellow-600" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = () => {
    switch (workflow.status) {
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'paused':
      case 'waiting_approval':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStageProgress = () => {
    const stages = ['outline', 'content_generation', 'review', 'final_assembly', 'export'];
    const currentIndex = stages.indexOf(workflow.current_stage);
    return ((currentIndex + 1) / stages.length) * 100;
  };

  return (
    <Link to={`/workflow/${workflow.id}`} className="block">
      <div className="card hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor()}`}>
              {workflow.status.replace('_', ' ')}
            </span>
          </div>
          <span className="text-xs text-gray-500">
            {formatDistanceToNow(new Date(workflow.created_at), { addSuffix: true })}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {workflow.title}
        </h3>

        {workflow.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-3">
            {workflow.description}
          </p>
        )}

        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
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

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            Stage: <span className="font-medium">{workflow.current_stage.replace('_', ' ')}</span>
          </span>
          
          {workflow.config?.target_audience && (
            <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
              {workflow.config.target_audience}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default WorkflowCard;