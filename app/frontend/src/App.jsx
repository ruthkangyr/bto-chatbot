import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import QuickTopics from './components/QuickTopics';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { Bot, AlertCircle } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState(null);
  const messagesEndRef = useRef(null);

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          setIsHealthy(true);
        } else {
          // Fallback check to /ping
          const fallback = await fetch('/ping');
          setIsHealthy(fallback.ok);
        }
      } catch (err) {
        setIsHealthy(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (text) => {
    const userMsg = { id: Date.now(), role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Send to FastAPI /api/invoke (or /invoke)
      const res = await fetch('/api/invoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ descr: text }),
      });

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }

      const data = await res.json();
      const botReply = data.response || 'No response returned by the assistant.';

      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', content: botReply },
      ]);
    } catch (err) {
      console.error('Error invoking agent:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content:
            '⚠️ **Unable to connect to the assistant.**\n\nPlease ensure that:\n1. Your FastAPI server is running on `http://localhost:8000`.\n2. LM Studio has `qwen2.5-7b-instruct` loaded with the server running on port `1234`.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 antialiased overflow-hidden">
      {/* Top Header */}
      <Header
        isHealthy={isHealthy}
        onClearChat={handleClearChat}
        hasMessages={messages.length > 0}
      />

      {/* Main Chat Area */}
      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
        <div className="max-w-4xl mx-auto h-full flex flex-col justify-between">
          {messages.length === 0 ? (
            <QuickTopics onSelectTopic={handleSendMessage} />
          ) : (
            <div className="py-2">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {/* Bot thinking indicator */}
              {isLoading && (
                <div className="flex gap-3.5 my-4 items-center">
                  <div className="w-8 h-8 rounded-full bg-brand-600/20 border border-brand-500/30 text-brand-300 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-brand-300 animate-pulse" />
                  </div>
                  <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-slate-300 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-brand-400 animate-bounce"></span>
                    <span className="w-2 h-2 rounded-full bg-brand-400 animate-bounce [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 rounded-full bg-brand-400 animate-bounce [animation-delay:0.4s]"></span>
                    <span className="text-xs text-slate-400 ml-1">
                      Searching HDB regulations & synthesizing answer...
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Bottom Input Area */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

