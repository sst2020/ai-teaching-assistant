import React from 'react';
import './Skeleton.css';

interface SkeletonProps {
  variant?: 'text' | 'rectangular' | 'circular';
  width?: string | number;
  height?: string | number;
  className?: string;
  animation?: 'pulse' | 'wave' | 'none';
}

/**
 * Skeleton loading placeholder component.
 * Provides visual feedback while content is loading.
 */
export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
  animation = 'pulse',
}) => {
  const style: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return (
    <div
      className={`skeleton skeleton--${variant} skeleton--${animation} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
};

interface SkeletonCardProps {
  lines?: number;
  showAvatar?: boolean;
  className?: string;
}

/**
 * Pre-built skeleton card for common loading states.
 */
export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  lines = 3,
  showAvatar = false,
  className = '',
}) => {
  return (
    <div className={`skeleton-card ${className}`} aria-label="Loading content">
      {showAvatar && (
        <div className="skeleton-card__header">
          <Skeleton variant="circular" width={40} height={40} />
          <div className="skeleton-card__header-text">
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="40%" />
          </div>
        </div>
      )}
      <div className="skeleton-card__body">
        {Array.from({ length: lines }).map((_, index) => (
          <Skeleton
            key={index}
            variant="text"
            width={index === lines - 1 ? '70%' : '100%'}
          />
        ))}
      </div>
    </div>
  );
};

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  className?: string;
}

/**
 * Pre-built skeleton table for loading table data.
 */
export const SkeletonTable: React.FC<SkeletonTableProps> = ({
  rows = 5,
  columns = 4,
  className = '',
}) => {
  return (
    <div className={`skeleton-table ${className}`} aria-label="Loading table">
      <div className="skeleton-table__header">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={index} variant="text" width="80%" height={20} />
        ))}
      </div>
      <div className="skeleton-table__body">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="skeleton-table__row">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton
                key={colIndex}
                variant="text"
                width={colIndex === 0 ? '90%' : '70%'}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export type { SkeletonProps, SkeletonCardProps, SkeletonTableProps };

