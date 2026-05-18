import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Play, Loader2 } from "lucide-react";
import Header from "../components/layout/Header";
import { analyzeStock, saveAnalysisResult } from "../services/api";

const TICKERS = [
  "OGDC",
  "ENGRO",
  "HBL",
  "UBL",
  "MCB",
  "LUCK",
  "EFERT",
  "PPL",
  "PSO",
  "SEARL",
  "NESTLE",
  "COLG",
  "ATRL",
  "MARI",
];

function formatApiError(err) {
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg || d).join(", ");
  return err.message || "Failed to fetch analysis.";
}

export default function Analysis() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");

  const filtered = TICKERS.filter((t) =>
    t.toLowerCase().includes(filter.toLowerCase())
  );

  const handleRun = async (ticker) => {
    setSelected(ticker);
    setRunning(true);
    setError(null);

    try {
      const data = await analyzeStock(ticker);

      if (!data?.success) {
        throw new Error("Analysis did not complete successfully.");
      }

      saveAnalysisResult(data);
      navigate(`/profile/${data.ticker}`, { state: { data } });
    } catch (err) {
      console.error(err);
      setError(formatApiError(err));
    } finally {
      setRunning(false);
    }
  };

  return (
    <>
      <Header
        title="Run Analysis"
        subtitle="Analyze PSX tickers using AI-powered agents (may take 1–2 minutes)"
      />

      <div className="card mb">
        <div className="search-bar">
          <Search size={16} className="text-muted" />
          <input
            type="text"
            placeholder="Search ticker..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="ticker-grid">
        {filtered.map((ticker) => (
          <button
            key={ticker}
            type="button"
            className={`ticker-btn ${selected === ticker ? "selected" : ""}`}
            onClick={() => handleRun(ticker)}
            disabled={running}
          >
            {running && selected === ticker ? (
              <Loader2 size={16} className="spin" />
            ) : (
              <Play size={15} />
            )}
            {ticker}
          </button>
        ))}
      </div>

      {running && (
        <div className="card mt">
          <div className="analysis-running">
            <Loader2 size={20} className="spin" />
            <span>
              Running AI analysis on <strong>{selected}</strong>… This can take up
              to 2 minutes on the hosted API.
            </span>
          </div>
        </div>
      )}

      {error && (
        <div className="card mt error-box">
          <p>{error}</p>
        </div>
      )}
    </>
  );
}
