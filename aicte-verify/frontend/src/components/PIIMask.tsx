import React, { useState } from 'react';
import { auditApi } from '../api/audit';

interface PIIMaskProps {
  maskedValue: string;
  rawValue: string;
  label?: string;
  userRole?: string;
  documentId?: string;
  className?: string;
}

export const PIIMask: React.FC<PIIMaskProps> = ({
  maskedValue,
  rawValue,
  label = 'Sensitive Data',
  userRole = 'officer',
  documentId = 'doc-current',
  className = '',
}) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [isLogging, setIsLogging] = useState(false);

  const canReveal = userRole === 'officer' || userRole === 'scrutiny_admin' || userRole === 'admin';

  const toggleReveal = async () => {
    if (!isRevealed) {
      setIsLogging(true);
      try {
        await auditApi.logAction(
          'PII_REVEAL_VIEWED',
          'Document',
          documentId,
          `Officer unmasked and accessed sensitive PII: ${label}`
        );
      } catch {
        // Continue even if offline
      } finally {
        setIsLogging(false);
        setIsRevealed(true);
      }
    } else {
      setIsRevealed(false);
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-mono text-xs bg-slate-100 border border-slate-300 ${className}`}
    >
      <span className="text-slate-500 font-sans font-medium text-[11px]">{label}:</span>
      <span
        className={`font-semibold ${
          isRevealed ? 'text-indigo-900 bg-amber-50 px-1 rounded border border-amber-200' : 'text-slate-700 tracking-wider'
        }`}
      >
        {isRevealed ? rawValue : maskedValue}
      </span>

      {canReveal && (
        <button
          type="button"
          onClick={toggleReveal}
          disabled={isLogging}
          title={
            isRevealed
              ? 'Click to mask PII again'
              : 'Click to reveal raw PII (Audited officer action)'
          }
          className="ml-1 text-[11px] font-sans text-aicte-600 hover:text-aicte-800 underline flex items-center gap-0.5"
        >
          {isLogging ? (
            'Logging...'
          ) : isRevealed ? (
            <span className="text-slate-500 hover:text-slate-700">Hide</span>
          ) : (
            <span className="text-amber-700 font-semibold hover:text-amber-800">Reveal 👁️</span>
          )}
        </button>
      )}
    </span>
  );
};

export default PIIMask;
