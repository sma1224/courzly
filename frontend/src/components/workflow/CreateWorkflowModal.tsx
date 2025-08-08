import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { workflowsApi } from '../../services/api';

const workflowSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  target_audience: z.string().min(1, 'Target audience is required'),
  level: z.enum(['beginner', 'intermediate', 'advanced']),
  duration: z.string().min(1, 'Duration is required'),
  num_modules: z.string().min(1, 'Number of modules is required'),
  include_exercises: z.boolean(),
  include_quizzes: z.boolean(),
});

type WorkflowForm = z.infer<typeof workflowSchema>;

interface CreateWorkflowModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const CreateWorkflowModal: React.FC<CreateWorkflowModalProps> = ({ onClose, onSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<WorkflowForm>({
    resolver: zodResolver(workflowSchema),
    defaultValues: {
      level: 'intermediate',
      include_exercises: true,
      include_quizzes: true,
    },
  });

  const onSubmit = async (data: WorkflowForm) => {
    setIsLoading(true);
    try {
      await workflowsApi.create({
        title: data.title,
        description: data.description,
        config: {
          target_audience: data.target_audience,
          level: data.level,
          duration: data.duration,
          num_modules: data.num_modules,
          include_exercises: data.include_exercises,
          include_quizzes: data.include_quizzes,
        },
      });
      
      toast.success('Course workflow created successfully!');
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create workflow');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Create New Course</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Course Title *
              </label>
              <input
                {...register('title')}
                className="input-field"
                placeholder="e.g., Introduction to Machine Learning"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                {...register('description')}
                rows={3}
                className="input-field"
                placeholder="Brief description of the course content and objectives"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Audience *
              </label>
              <input
                {...register('target_audience')}
                className="input-field"
                placeholder="e.g., Software developers, Students"
              />
              {errors.target_audience && (
                <p className="mt-1 text-sm text-red-600">{errors.target_audience.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Course Level *
              </label>
              <select {...register('level')} className="input-field">
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Estimated Duration *
              </label>
              <input
                {...register('duration')}
                className="input-field"
                placeholder="e.g., 4-6 hours, 2 weeks"
              />
              {errors.duration && (
                <p className="mt-1 text-sm text-red-600">{errors.duration.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Modules *
              </label>
              <input
                {...register('num_modules')}
                className="input-field"
                placeholder="e.g., 4-6 modules"
              />
              {errors.num_modules && (
                <p className="mt-1 text-sm text-red-600">{errors.num_modules.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Content Options</h3>
            
            <div className="flex items-center">
              <input
                {...register('include_exercises')}
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Include practical exercises and activities
              </label>
            </div>

            <div className="flex items-center">
              <input
                {...register('include_quizzes')}
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Include quizzes and assessments
              </label>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
            >
              {isLoading ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateWorkflowModal;