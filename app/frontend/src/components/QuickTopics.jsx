import React from 'react';
import { User, Building2, Coins, FileText, Sparkles } from 'lucide-react';

const TOPICS = [
  {
    icon: User,
    label: 'Single Citizen BTO Rules',
    query: 'Can a single person buy a BTO flat in Singapore, and what are the rules, age limits, and flat types allowed?'
  },
  {
    icon: Building2,
    label: 'Standard vs Plus vs Prime',
    query: 'What is the difference between Standard, Plus, and Prime BTO flats under the new classification framework?'
  },
  {
    icon: Coins,
    label: 'Enhanced CPF Housing Grant',
    query: 'How much can I get for the Enhanced CPF Housing Grant (EHG), and what are the income ceilings?'
  },
  {
    icon: FileText,
    label: 'HFE Letter Process',
    query: 'What is the HDB Flat Eligibility (HFE) letter and how long is it valid for?'
  }
];

export default function QuickTopics({ onSelectTopic }) {
  return (
    <div className="max-w-2xl mx-auto py-10 px-4 text-center">
      <div className="w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center mx-auto mb-4 shadow-sm">
        <Sparkles className="w-8 h-8 text-brand-400" />
      </div>
      <h2 className="text-2xl font-bold text-slate-100 tracking-tight mb-2">
        Plan Your Singapore Home with AI
      </h2>
      <p className="text-sm text-slate-400 max-w-md mx-auto mb-8 leading-relaxed">
        Ask any question about HDB BTO eligibility, flat types, CPF housing grants, and HFE applications.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
        {TOPICS.map((topic, i) => {
          const Icon = topic.icon;
          return (
            <button
              key={i}
              onClick={() => onSelectTopic(topic.query)}
              className="group p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 hover:border-brand-500/50 hover:bg-slate-800 transition-all duration-200 text-left flex items-start gap-3.5 shadow-sm hover:shadow-brand-500/5 hover:-translate-y-0.5"
            >
              <div className="p-2 rounded-lg bg-brand-500/10 border border-brand-500/20 text-brand-300 group-hover:text-brand-200 group-hover:bg-brand-500/20 transition-colors">
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <span className="block text-sm font-semibold text-slate-200 group-hover:text-brand-300 transition-colors">
                  {topic.label}
                </span>
                <span className="block text-xs text-slate-400 mt-0.5 line-clamp-2">
                  {topic.query}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

