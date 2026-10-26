import React from 'react';

interface AdvisoryBadgeProps {
  className?: string;
  size?: 'sm' | 'md';
}

export const AdvisoryBadge: React.FC<AdvisoryBadgeProps> = ({ className = '', size = 'sm' }) => {
  const sizeClasses = size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1 font-semibold tracking-wide uppercase rounded border bg-amber-50 text-amber-800 border-amber-300 shadow-sm ${sizeClasses} ${className}`}
      title="This insight is generated for decision-support only. Human AICTE official authority required."
    >
      <svg className="w-3 h-3 text-amber-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
      Advisory Only
    </span>
  );
};

export default AdvisoryBadge;
