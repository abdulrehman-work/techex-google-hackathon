import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import Agents from "./pages/Agents";
import Portfolio from "./pages/Portfolio";
import Analysis from "./pages/Analysis";
import News from "./pages/News";
import Audit from "./pages/Audit";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="agents" element={<Agents />} />
          <Route path="portfolio" element={<Portfolio />} />
          <Route path="analysis" element={<Analysis />} />
          <Route path="news" element={<News />} />
          <Route path="audit" element={<Audit />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
