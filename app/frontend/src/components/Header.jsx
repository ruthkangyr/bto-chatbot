import React from 'react';
import { Home, Trash2, Cpu, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Header({ isHealthy, onClearChat, hasMessages }) {
  return (
    <header className="bg-gradient-to-r from-brand-900 via-brand-800 to-brand-700 text-white px-6 py-4 border-b border-brand-700/50 shadow-lg">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-brand-600/60 border border-brand-400/30 flex items-center justify-center shadow-inner text-white">
            <Home className="w-6 h-6 text-brand-200" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white">
                HDB BTO & Housing Grants AI Assistant
              </h1>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[11px] font-semibold bg-brand-500/30 border border-brand-400/30 rounded-full text-brand-100">
                Agentic RAG
              </span>
            </div>
            <p className="text-xs text-brand-200/90 font-medium">
              Official Guidelines • Standard, Plus & Prime • CPF Housing Grants
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Status Indicator */}
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900/40 border border-brand-500/30 text-xs text-brand-100">
            {isHealthy === true && (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>FastAPI Ready</span>
              </>
            )}
            {isHealthy === false && (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span className="text-amber-200">Backend Disconnected</span>
              </>
            )}
            {isHealthy === null && (
              <>
                <Cpu className="w-3.5 h-3.5 text-brand-300 animate-spin" />
                <span>Checking...</span>
              </>
            )}
          </div>

          {/* Clear button */}
          {hasMessages && (
            <button
              onClick={onClearChat}
              className="p-2 rounded-lg text-brand-200 hover:text-white hover:bg-brand-700/60 transition-colors text-xs flex items-center gap-1.5"
              title="Clear conversation"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Reset</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

