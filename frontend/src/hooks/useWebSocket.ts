import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { ChatMessage } from '../types';

interface UseWebSocketProps {
  workflowId: string;
  onMessage?: (message: ChatMessage) => void;
  onStatusUpdate?: (status: any) => void;
}

export const useWebSocket = ({ workflowId, onMessage, onStatusUpdate }: UseWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token || !workflowId) return;

    // Chat WebSocket
    const chatSocket = io(`${process.env.REACT_APP_WS_URL}/ws/chat/${workflowId}`, {
      auth: { token }
    });

    // Status WebSocket
    const statusSocket = io(`${process.env.REACT_APP_WS_URL}/ws/workflow/${workflowId}/status`, {
      auth: { token }
    });

    chatSocket.on('connect', () => setIsConnected(true));
    chatSocket.on('disconnect', () => setIsConnected(false));

    chatSocket.on('message', (message: ChatMessage) => {
      setMessages(prev => [...prev, message]);
      onMessage?.(message);
    });

    statusSocket.on('status_update', (status: any) => {
      onStatusUpdate?.(status);
    });

    socketRef.current = chatSocket;

    return () => {
      chatSocket.disconnect();
      statusSocket.disconnect();
    };
  }, [workflowId, onMessage, onStatusUpdate]);

  const sendMessage = (message: string, type: string = 'text') => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('message', {
        message,
        message_type: type,
        timestamp: new Date().toISOString()
      });
    }
  };

  const sendTyping = (isTyping: boolean) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('typing', { is_typing: isTyping });
    }
  };

  return {
    isConnected,
    messages,
    sendMessage,
    sendTyping
  };
};