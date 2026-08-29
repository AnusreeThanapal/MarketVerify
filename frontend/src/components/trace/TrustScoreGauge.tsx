import React from 'react';

interface TrustScoreGaugeProps {
  score: number; // 0 to 1
  label?: string;
}

export const TrustScoreGauge: React.FC<TrustScoreGaugeProps> = ({
  score,
  label = 'Bayesian Trust Score',
}) => {
  const percentage = Math.round(score * 100);
  const radius = 38;
  const strokeWidth = 7;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 0.75) return '#0D8253'; // Emerald
    if (s >= 0.5) return '#D97706';  // Amber
    return '#C53030';                 // Desaturated Red
  };

  const getTier = (s: number) => {
    if (s >= 0.75) return 'TIER 1 (HIGH)';
    if (s >= 0.5) return 'TIER 2 (MEDIUM)';
    return 'TIER 3 (LOW)';
  };

  const strokeColor = getColor(score);

  return (
    <div className="flex flex-col items-center justify-center p-3 bg-portal-bg rounded-portal border border-portal-border">
      <div className="relative w-24 h-24 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke="#E2E8F0"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Score Text */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-xl font-mono font-bold text-portal-navy leading-none">
            {percentage}%
          </span>
          <span className="text-[9px] font-mono font-semibold uppercase text-portal-textMuted mt-0.5">
            {getTier(score)}
          </span>
        </div>
      </div>

      <span className="text-xs font-mono font-bold text-portal-navy mt-1">
        {label}
      </span>
    </div>
  );
};
