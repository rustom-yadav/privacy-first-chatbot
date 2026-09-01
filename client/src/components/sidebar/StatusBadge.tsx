"use client";

interface StatusBadgeProps {
  status: "healthy" | "degraded" | "down" | "checking";
}

const statusConfig = {
  healthy: {
    label: "All Systems Online",
    color: "bg-status-healthy",
    textColor: "text-status-healthy",
    glow: true,
  },
  degraded: {
    label: "Partially Degraded",
    color: "bg-status-degraded",
    textColor: "text-status-degraded",
    glow: false,
  },
  down: {
    label: "API Offline",
    color: "bg-status-down",
    textColor: "text-status-down",
    glow: false,
  },
  checking: {
    label: "Checking...",
    color: "bg-text-muted",
    textColor: "text-text-muted",
    glow: false,
  },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const cfg = statusConfig[status];

  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-xl glass-light">
      <span
        className={`w-2 h-2 rounded-full ${cfg.color} ${cfg.glow ? "animate-pulse-glow" : ""}`}
      />
      <span className={`text-xs font-medium ${cfg.textColor}`}>
        {cfg.label}
      </span>
    </div>
  );
}
