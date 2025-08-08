import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon,
  EyeIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { hitlApi } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import toast from 'react-hot-toast';

interface ApprovalDashboardProps {
  workflowId: string;
}

const ApprovalDashboard: React.FC<ApprovalDashboardProps> = ({ workflowId }) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedApproval, setSelectedApproval] = useState<any>(null);
  const [comments, setComments] = useState('');
  const [showComparison, setShowComparison] = useState(false);

  const { data: pendingApprovals } = useQuery({
    queryKey: ['pending-approvals', workflowId],
    queryFn: () => hitlApi.getPendingApprovals(workflowId),
    refetchInterval: 5000
  });

  const { data: approvalHistory } = useQuery({
    queryKey: ['approval-history', workflowId],
    queryFn: () => hitlApi.getPendingApprovals(workflowId) // This would be approval history endpoint
  });

  const approveMutation = useMutation({
    mutationFn: (data: { status: string; comments?: string }) =>
      hitlApi.approve(workflowId, data),
    onSuccess: () => {
      toast.success('Approval submitted successfully!');
      queryClient.invalidateQueries({ queryKey: ['pending-approvals', workflowId] });
      setSelectedApproval(null);
      setComments('');
    },
    onError: () => {
      toast.error('Failed to submit approval');
    }
  });

  const handleApproval = (status: 'approved' | 'rejected') => {
    if (!selectedApproval) return;

    approveMutation.mutate({
      status,
      comments: comments.trim() || undefined
    });
  };

  const renderApprovalCard = (approval: any) => (
    <div
      key={approval.checkpoint_id}
      className={`border rounded-lg p-4 cursor-pointer transition-colors ${
        selectedApproval?.checkpoint_id === approval.checkpoint_id
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={() => setSelectedApproval(approval)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-5 h-5 text-yellow-500" />
            <h3 className="font-medium">
              {approval.stage.replace('_', ' ').toUpperCase()} Review
            </h3>
          </div>
          
          <p className="text-sm text-gray-600 mt-1">
            Created {new Date(approval.created_at).toLocaleDateString()}
          </p>
          
          {approval.state_data?.title && (
            <p className="text-sm font-medium mt-2">
              {approval.state_data.title}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowComparison(!showComparison);
            }}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            <EyeIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
      {/* Pending Approvals */}
      <div className="lg:col-span-1 space-y-4">
        <h3 className="font-semibold">Pending Approvals</h3>
        
        <div className="space-y-3 overflow-y-auto max-h-[500px]">
          {pendingApprovals?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ClockIcon className="w-8 h-8 mx-auto mb-2" />
              <p>No pending approvals</p>
            </div>
          ) : (
            pendingApprovals?.map(renderApprovalCard)
          )}
        </div>
      </div>

      {/* Approval Details */}
      <div className="lg:col-span-2 border rounded-lg flex flex-col">
        {selectedApproval ? (
          <>
            {/* Header */}
            <div className="border-b p-4">
              <h3 className="font-semibold">
                {selectedApproval.stage.replace('_', ' ').toUpperCase()} Review
              </h3>
              <p className="text-sm text-gray-600">
                Checkpoint ID: {selectedApproval.checkpoint_id}
              </p>
            </div>

            {/* Content Preview */}
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Content to Review:</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    {selectedApproval.state_data?.outline && (
                      <div className="space-y-2">
                        <h5 className="font-medium">Course Outline</h5>
                        {selectedApproval.state_data.outline.modules?.map((module: any, idx: number) => (
                          <div key={idx} className="border-l-2 border-primary-500 pl-3">
                            <p className="font-medium text-sm">{module.title}</p>
                            <p className="text-xs text-gray-600">{module.description}</p>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {selectedApproval.state_data?.modules && (
                      <div className="space-y-2">
                        <h5 className="font-medium">Generated Modules</h5>
                        {selectedApproval.state_data.modules.map((module: any, idx: number) => (
                          <div key={idx} className="border rounded p-2">
                            <p className="font-medium text-sm">{module.title}</p>
                            <p className="text-xs text-gray-600 line-clamp-2">
                              {module.content?.introduction}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Comments */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Review Comments
                  </label>
                  <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    rows={4}
                    className="input-field"
                    placeholder="Add your feedback, suggestions, or concerns..."
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="border-t p-4 flex justify-end space-x-3">
              <button
                onClick={() => handleApproval('rejected')}
                disabled={approveMutation.isPending}
                className="flex items-center space-x-2 px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50"
              >
                <XCircleIcon className="w-5 h-5" />
                <span>Request Changes</span>
              </button>
              
              <button
                onClick={() => handleApproval('approved')}
                disabled={approveMutation.isPending}
                className="flex items-center space-x-2 btn-primary"
              >
                <CheckCircleIcon className="w-5 h-5" />
                <span>Approve</span>
              </button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <ChatBubbleLeftRightIcon className="w-12 h-12 mx-auto mb-4" />
              <p>Select an approval to review</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApprovalDashboard;