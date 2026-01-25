/**
 * EmptyState component - Premium Dark Theme
 * Elegant empty state with call-to-action
 */

interface EmptyStateProps {
  onCreateClick: () => void;
}

export default function EmptyState({ onCreateClick }: EmptyStateProps) {
  return (
    <div className="text-center py-16 animate-fade-in">
      {/* Icon */}
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 mb-6">
        <svg className="w-10 h-10 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>

      {/* Heading */}
      <h3 className="text-2xl font-bold text-slate-100 mb-3">
        No tasks yet
      </h3>

      {/* Description */}
      <p className="text-slate-400 mb-8 max-w-sm mx-auto leading-relaxed">
        Start organizing your work by creating your first task. Stay productive and focused.
      </p>

      {/* CTA Button */}
      <button
        onClick={onCreateClick}
        className="btn-primary"
      >
        <span className="flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Your First Task
        </span>
      </button>
    </div>
  );
}
