import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { useApi } from "../../hooks/useApi";
import { api } from "../../services/api";

export default function Layout() {
  const { data } = useApi(() => api.getHealth(), [], 30000);

  return (
    <div className="layout">
      <Sidebar health={data} />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
