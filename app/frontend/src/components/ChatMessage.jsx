import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Copy, Check } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!message.content) return;
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3.5 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-brand-600/20 border border-brand-500/30 text-brand-300 flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
          <Bot className="w-4 h-4 text-brand-300" />
        </div>
      )}

      <div
        className={`relative group max-w-[85%] sm:max-w-[80%] rounded-2xl px-5 py-3.5 shadow-sm text-sm leading-relaxed ${
          isUser
            ? 'bg-gradient-to-br from-brand-700 to-brand-800 text-white rounded-tr-sm border border-brand-600/40 shadow-brand-900/20'
            : 'bg-slate-800/90 text-slate-100 rounded-tl-sm border border-slate-700/80 shadow-slate-950/20'
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none prose-p:my-1.5 prose-ul:my-1.5 prose-li:my-0.5 prose-strong:text-brand-300">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Copy button for bot response */}
        {!isUser && message.content && (
          <button
            onClick={handleCopy}
            className="absolute top-2.5 right-2.5 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-slate-300 hover:text-white text-xs flex items-center gap-1"
            title="Copy answer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 text-slate-200 flex items-center justify-center flex-shrink-0 mt-1">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}

