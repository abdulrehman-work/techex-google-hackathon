const VARIANTS = {
  positive: { bg: "rgba(16,185,129,0.12)", color: "#10b981" },
  negative: { bg: "rgba(239,68,68,0.12)", color: "#ef4444" },
  warning: { bg: "rgba(245,158,11,0.12)", color: "#f59e0b" },
  info: { bg: "rgba(59,130,246,0.12)", color: "#3b82f6" },
  neutral: { bg: "rgba(148,163,184,0.12)", color: "#94a3b8" },
};

export default function Badge({ children, variant = "neutral" }) {
  const v = VARIANTS[variant] || VARIANTS.neutral;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "2px 10px",
        borderRadius: "9999px",
        fontSize: "0.75rem",
        fontWeight: 600,
        background: v.bg,
        color: v.color,
      }}
    >
      {children}
    </span>
  );
}
