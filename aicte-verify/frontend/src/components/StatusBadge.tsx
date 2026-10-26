import React from 'react';
import { ApplicationStatus, DocumentStatus, VerificationStatus } from '../types';

interface StatusBadgeProps {
  status: ApplicationStatus | DocumentStatus | VerificationStatus | string;
  type?: 'application' | 'document' | 'verification';
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  let style = 'bg-slate-100 text-slate-800 border-slate-300';
  let formattedText = status.replace('_', ' ');

  switch (status) {
    // Application statuses
    case 'draft':
      style = 'bg-slate-100 text-slate-700 border-slate-300';
      break;
    case 'submitted':
      style = 'bg-blue-50 text-blue-700 border-blue-300';
      break;
    case 'under_review':
      style = 'bg-indigo-50 text-indigo-700 border-indigo-300';
      break;
    case 'verified':
      style = 'bg-emerald-50 text-emerald-700 border-emerald-300';
      break;
    case 'deficiency_issued':
      style = 'bg-amber-50 text-amber-800 border-amber-300';
      break;
    case 'approved':
      style = 'bg-teal-50 text-teal-800 border-teal-300 font-bold';
      break;
    case 'rejected':
      style = 'bg-rose-50 text-rose-800 border-rose-300';
      formattedText = 'Recommend rejection';
      break;

    // Document / verification statuses
    case 'processing':
      style = 'bg-purple-50 text-purple-700 border-purple-300 animate-pulse';
      break;
    case 'not_run':
      style = 'bg-slate-100 text-slate-600 border-slate-300 italic';
      formattedText = 'Not Run';
      break;
    case 'flagged':
      style = 'bg-amber-100 text-amber-900 border-amber-400 font-semibold';
      break;
    case 'failed':
    case 'mismatch':
      style = 'bg-rose-100 text-rose-900 border-rose-400 font-semibold';
      break;
    case 'unreachable':
      style = 'bg-gray-100 text-gray-700 border-gray-300';
      break;
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${style} ${className}`}
    >
      {formattedText}
    </span>
  );
};

export default StatusBadge;
