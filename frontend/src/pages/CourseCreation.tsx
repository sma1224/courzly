import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import toast from 'react-hot-toast';
import { BookOpen, Users, Clock, Target, CheckCircle } from 'lucide-react';

import { createCourse } from '../services/api';
import { CourseCreationRequest } from '../types';

const steps = [
  { id: 1, name: 'Requirements', icon: Target },
  { id: 2, name: 'Outline Review', icon: BookOpen },
  { id: 3, name: 'Content Review', icon: Users },
  { id: 4, name: 'Publishing', icon: CheckCircle },
];

export default function CourseCreation() {
  const [currentStep, setCurrentStep] = useState(1);
  const [courseData, setCourseData] = useState<Partial<CourseCreationRequest>>({});
  const [executionId, setExecutionId] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<CourseCreationRequest>();

  const createCourseMutation = useMutation(createCourse, {
    onSuccess: (data) => {
      setExecutionId(data.execution_id);
      toast.success('Course creation started!');
      setCurrentStep(2);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start course creation');
    },
  });

  const onSubmit = (data: CourseCreationRequest) => {
    setCourseData(data);
    createCourseMutation.mutate(data);
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Course</h1>
        <p className="text-gray-600">
          Use our AI-powered course creation wizard to build comprehensive educational content
        </p>
      </div>

      <div className="bg-white shadow-lg rounded-lg p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Course Title
              </label>
              <input
                {...register('title', { required: 'Title is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter course title"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Audience
              </label>
              <input
                {...register('target_audience', { required: 'Target audience is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Beginner developers"
              />
              {errors.target_audience && (
                <p className="mt-1 text-sm text-red-600">{errors.target_audience.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Course Description
            </label>
            <textarea
              {...register('description', { required: 'Description is required' })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe what students will learn"
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration
              </label>
              <input
                {...register('duration', { required: 'Duration is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 8 weeks"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level
              </label>
              <select
                {...register('difficulty_level', { required: 'Difficulty level is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Assessment Type
              </label>
              <input
                {...register('assessment_type', { required: 'Assessment type is required' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Projects, Quizzes"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={createCourseMutation.isLoading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {createCourseMutation.isLoading ? 'Creating Course...' : 'Start Course Creation'}
          </button>
        </form>
      </div>
    </div>
  );
}