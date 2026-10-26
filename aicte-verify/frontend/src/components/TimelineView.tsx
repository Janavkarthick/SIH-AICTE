import React from 'react';
import { TimelineEvent } from '../types';

interface TimelineViewProps {
  events: TimelineEvent[];
  className?: string;
}

export const TimelineView: React.FC<TimelineViewProps> = ({ events, className = '' }) => {
  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'status_change':
        return (
          <span className="p-1.5 rounded-full bg-blue-100 text-blue-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
        );
      case 'flag_raised':
        return (
          <span className="p-1.5 rounded-full bg-rose-100 text-rose-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </span>
        );
      case 'flag_resolved':
        return (
          <span className="p-1.5 rounded-full bg-emerald-100 text-emerald-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          </span>
        );
      case 'document_uploaded':
        return (
          <span className="p-1.5 rounded-full bg-purple-100 text-purple-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </span>
        );
      case 'deficiency_issued':
        return (
          <span className="p-1.5 rounded-full bg-amber-100 text-amber-800">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </span>
        );
      default:
        return (
          <span className="p-1.5 rounded-full bg-slate-100 text-slate-700">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
        );
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {events.map((evt, idx) => (
        <div key={evt.id} className="relative flex items-start gap-4">
          {/* Vertical connecting line */}
          {idx !== events.length - 1 && (
            <div className="absolute left-[17px] top-8 bottom-0 w-0.5 bg-slate-200" />
          )}

          {/* Node Icon */}
          <div className="relative z-10 flex-shrink-0">{getEventIcon(evt.type)}</div>

          {/* Event Content Card */}
          <div className="flex-1 bg-slate-50 border border-slate-200 rounded-lg p-3.5 shadow-sm">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <h4 className="text-xs font-bold text-slate-900">{evt.title}</h4>
              <span className="text-[11px] font-mono text-slate-400">
                {new Date(evt.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-600">{evt.description}</p>
            <div className="mt-2 text-[10px] text-slate-400 font-medium">Actor: {evt.actor}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TimelineView;
