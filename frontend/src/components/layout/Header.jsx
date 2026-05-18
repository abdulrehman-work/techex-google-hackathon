import { Bell } from "lucide-react";

export default function Header({ title, subtitle }) {
  return (
    <header className="page-header">
      <div>
        <h2 className="page-title">{title}</h2>
        {subtitle && <p className="text-muted">{subtitle}</p>}
      </div>
      <div className="header-actions">
        <button className="icon-btn">
          <Bell size={18} />
        </button>
      </div>
    </header>
  );
}
