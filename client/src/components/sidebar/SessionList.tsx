import type { SessionSummary } from '@/lib/types';

interface SessionListProps {
  sessions: SessionSummary[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
}

export default function SessionList({
  sessions,
  activeSessionId,
  onSelectSession,
  onDeleteSession,
}: SessionListProps) {
  if (sessions.length === 0) return null;

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2 px-4">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
          Previous Chats
        </h3>
      </div>
      <div className="space-y-1 px-2">
        {sessions.map((session) => {
          const isActive = session.session_id === activeSessionId;
          const dateStr = new Date(session.last_message).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
          });

          return (
            <div
              key={session.session_id}
              onClick={() => onSelectSession(session.session_id)}
              className={`group flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors ${
                isActive
                  ? 'bg-brand-primary/10 text-brand-primary'
                  : 'hover:bg-surface-overlay text-text-secondary hover:text-text-primary'
              }`}
            >
              <div className="flex-1 min-w-0 pr-2">
                <p className="text-sm font-medium truncate">
                  {session.preview || 'Empty chat'}
                </p>
                <p className={`text-xs ${isActive ? 'text-brand-primary/70' : 'text-text-muted'}`}>
                  {dateStr}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.session_id);
                }}
                className={`p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity ${
                  isActive
                    ? 'hover:bg-brand-primary/20 text-brand-primary'
                    : 'hover:bg-status-down/10 text-text-muted hover:text-status-down'
                }`}
                title="Delete session"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
