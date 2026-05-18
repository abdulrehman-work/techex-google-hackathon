export default function StatCard({ label, value, sub, icon: Icon, trend }) {
  return (
    <div className="card stat-card">
      <div className="stat-header">
        <span className="text-muted text-xs">{label}</span>
        {Icon && <Icon size={16} className="text-muted" />}
      </div>
      <span className={`stat-value ${trend === "up" ? "text-positive" : trend === "down" ? "text-negative" : ""}`}>
        {value}
      </span>
      {sub && <span className="text-muted text-xs">{sub}</span>}
    </div>
  );
}
