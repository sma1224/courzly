import React, { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { PaperAirplaneIcon, UserIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import { chatApi } from '../../services/api';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useAuth } from '../../hooks/useAuth';
import { ChatMessage } from '../../types';
import { formatDistanceToNow } from 'date-fns';

interface ChatInterfaceProps {
  workflowId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ workflowId }) => {
  const { user } = useAuth();
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);

  const { data: chatHistory } = useQuery({
    queryKey: ['chat', workflowId],
    queryFn: () => chatApi.getHistory(workflowId),
    enabled: !!workflowId
  });

  const { sendMessage, sendTyping } = useWebSocket({
    workflowId,
    onMessage: (newMessage) => {
      setLocalMessages(prev => [...prev, newMessage]);
    }
  });

  const allMessages = [...(chatHistory?.messages || []), ...localMessages];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [allMessages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const messageText = message;
    setMessage('');

    try {
      await chatApi.sendMessage(workflowId, {
        message: messageText,
        message_type: 'user_query'
      });
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleTyping = (typing: boolean) => {
    if (typing !== isTyping) {
      setIsTyping(typing);
      sendTyping(typing);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg border">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {allMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.is_ai ? 'justify-start' : 'justify-end'}`}
          >
            <div className={`flex max-w-xs lg:max-w-md ${msg.is_ai ? 'flex-row' : 'flex-row-reverse'}`}>
              <div className={`flex-shrink-0 ${msg.is_ai ? 'mr-3' : 'ml-3'}`}>
                {msg.is_ai ? (
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <CpuChipIcon className="w-5 h-5 text-blue-600" />
                  </div>
                ) : (
                  <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                    <UserIcon className="w-5 h-5 text-gray-600" />
                  </div>
                )}
              </div>
              
              <div className={`px-4 py-2 rounded-lg ${
                msg.is_ai 
                  ? 'bg-gray-100 text-gray-900' 
                  : 'bg-primary-600 text-white'
              }`}>
                <p className="text-sm">{msg.message}</p>
                <p className={`text-xs mt-1 ${
                  msg.is_ai ? 'text-gray-500' : 'text-primary-100'
                }`}>
                  {formatDistanceToNow(new Date(msg.created_at), { addSuffix: true })}
                </p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => {
              setMessage(e.target.value);
              handleTyping(e.target.value.length > 0);
            }}
            onBlur={() => handleTyping(false)}
            placeholder="Ask about the course content, get suggestions..."
            className="flex-1 input-field"
          />
          <button
            type="submit"
            disabled={!message.trim()}
            className="btn-primary px-3 py-2 disabled:opacity-50"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </form>
        
        <div className="mt-2 text-xs text-gray-500">
          💡 Try asking: "Review the outline", "Suggest improvements", "Add more examples"
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;