import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Send, Bot, User } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const sendMessage = useMutation({
    mutationFn: async (content: string) => {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/ai/chat`, {
        messages: [
          ...messages,
          { role: 'user', content },
        ],
      });
      return response.data;
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.content },
      ]);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: input }]);
    sendMessage.mutate(input);
    setInput('');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold glow-text">AI Analyst</h1>
        <p className="text-gray-400 mt-2">Chat with AI for threat intelligence analysis</p>
      </div>

      <div className="cyber-card h-[600px] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Bot className="w-12 h-12 mx-auto mb-4 text-cyber-primary" />
              <p>Start a conversation with the AI analyst</p>
              <p className="text-sm mt-2">Ask about threats, IOCs, or request analysis</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-cyber-primary/20 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-cyber-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[70%] p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-cyber-primary/20 text-gray-100'
                      : 'bg-cyber-bg border border-cyber-border'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-cyber-accent/20 flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-cyber-accent" />
                  </div>
                )}
              </div>
            ))
          )}
          {sendMessage.isPending && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-cyber-primary/20 flex items-center justify-center">
                <Bot className="w-5 h-5 text-cyber-primary animate-pulse" />
              </div>
              <div className="bg-cyber-bg border border-cyber-border p-4 rounded-lg">
                <p className="text-gray-400">Thinking...</p>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="cyber-input flex-1"
            placeholder="Ask the AI analyst..."
            disabled={sendMessage.isPending}
          />
          <button
            type="submit"
            disabled={sendMessage.isPending || !input.trim()}
            className="cyber-button disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
