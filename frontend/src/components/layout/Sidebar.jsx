import { NavLink } from "react-router-dom";
import {
  Activity,
  Box,
  Target,
  Shield,
  TerminalSquare,
  Search,
  Newspaper,
} from "lucide-react";

const NAV = [
  { to: "/", icon: Activity, label: "Dashboard" },
  { to: "/agents", icon: Box, label: "Agent Network" },
  { to: "/portfolio", icon: Target, label: "Portfolio" },
  { to: "/analysis", icon: Search, label: "Analysis" },
  { to: "/news", icon: Newspaper, label: "News Feed" },
  { to: "/audit", icon: TerminalSquare, label: "On-chain Logs" },
];

export default function Sidebar({ health }) {
  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <h1 className="text-gradient">PakAI Capital</h1>
        <p className="text-muted text-xs">
          PSX Multi-Agent Trading System
        </p>
      </div>

      <div className="nav-links">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </div>

      {/* System status footer */}
      <div className="sidebar-footer">
        <div className="status-card">
          <div className="status-row">
            <span
              className={`status-dot ${health ? "online" : "offline"}`}
            />
            <span className="text-sm font-semibold">
              {health ? "System Online" : "Connecting..."}
            </span>
          </div>
          {health && (
            <div className="status-details">
              <span>Provider: {health.provider}</span>
              <span>Tickers: {health.tickers}</span>
              <span>Agent #{health.agent_id}</span>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
