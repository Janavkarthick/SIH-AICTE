import React from 'react';
import { RiskLevel } from '../types';

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, className = '' }) => {
  let colorStyles = '';
  let label = '';

  switch (level) {
    case 'low':
      colorStyles = 'bg-emerald-100 text-emerald-800 border-emerald-300';
      label = 'Low Risk';
      break;
    case 'medium':
      colorStyles = 'bg-amber-100 text-amber-800 border-amber-300';
      label = 'Medium Risk';
      break;
    case 'high':
      colorStyles = 'bg-rose-100 text-rose-800 border-rose-300 animate-pulse';
      label = 'High Risk';
      break;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colorStyles} ${className}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          level === 'low' ? 'bg-emerald-500' : level === 'medium' ? 'bg-amber-500' : 'bg-rose-600'
        }`}
      />
      {label}
      {typeof score === 'number' && (
        <span className="ml-1 opacity-75 font-mono text-[11px]">({score}/100)</span>
      )}
    </span>
  );
};

export default RiskBadge;
