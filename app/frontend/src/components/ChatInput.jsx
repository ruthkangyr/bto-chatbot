import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSendMessage(trimmed);
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-slate-800 bg-slate-900/90 backdrop-blur px-4 py-3.5 sm:px-6">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-center gap-2.5">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about BTO eligibility, grants, flat types, HFE..."
            disabled={isLoading}
            className="w-full bg-slate-800/80 border border-slate-700/80 rounded-2xl px-4 py-3.5 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="px-5 py-3.5 bg-gradient-to-r from-brand-700 to-brand-600 hover:from-brand-600 hover:to-brand-500 text-white rounded-2xl font-medium text-sm flex items-center gap-2 transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-brand-900/20 active:scale-95"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="hidden sm:inline">Thinking...</span>
            </>
          ) : (
            <>
              <span>Send</span>
              <Send className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}

