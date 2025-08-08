import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '../useAuth';
import * as api from '../../services/api';

// Mock the API
jest.mock('../../services/api');
const mockedApi = api as jest.Mocked<typeof api>;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
};

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('initializes with no user when no token exists', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper()
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });

  it('loads user data when token exists in localStorage', async () => {
    const mockUser = {
      id: 'user-1',
      email: 'test@example.com',
      username: 'testuser',
      full_name: 'Test User',
      role: 'editor' as const,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z'
    };

    localStorage.setItem('token', 'test-token');
    mockedApi.authApi.getMe.mockResolvedValue(mockUser);

    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper: createWrapper()
    });

    await waitForNextUpdate();

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe('test-token');
  });

  it('handles login successfully', async () => {
    const mockTokenResponse = {
      access_token: 'new-token',
      token_type: 'bearer',
      expires_in: 3600
    };

    const mockUser = {
      id: 'user-1',
      email: 'test@example.com',
      username: 'testuser',
      full_name: 'Test User',
      role: 'editor' as const,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z'
    };

    mockedApi.authApi.login.mockResolvedValue(mockTokenResponse);
    mockedApi.authApi.getMe.mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper()
    });

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe('new-token');
    expect(localStorage.getItem('token')).toBe('new-token');
  });

  it('handles login failure', async () => {
    mockedApi.authApi.login.mockRejectedValue(new Error('Invalid credentials'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper()
    });

    await expect(
      result.current.login('test@example.com', 'wrong-password')
    ).rejects.toThrow('Invalid credentials');

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
  });

  it('handles logout correctly', async () => {
    localStorage.setItem('token', 'test-token');
    
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper()
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('clears token when getMe fails', async () => {
    localStorage.setItem('token', 'invalid-token');
    mockedApi.authApi.getMe.mockRejectedValue(new Error('Unauthorized'));

    const { result, waitForNextUpdate } = renderHook(() => useAuth(), {
      wrapper: createWrapper()
    });

    await waitForNextUpdate();

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});