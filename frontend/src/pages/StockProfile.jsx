import { Link, useLocation, useParams } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ArrowLeft } from "lucide-react";
import Badge from "../components/common/Badge";
import { loadAnalysisResult } from "../services/api";

function signalVariant(signal) {
  if (signal === "BUY") return "positive";
  if (signal === "SELL") return "negative";
  return "warning";
}

export default function StockProfile() {
  const { ticker: routeTicker } = useParams();
  const location = useLocation();

  const apiData =
    location.state?.data ||
    location.state?.analysisData ||
    loadAnalysisResult(routeTicker);

  if (!apiData?.success) {
    return (
      <div className="card" style={{ marginTop: 40, textAlign: "center" }}>
        <h2>No analysis data</h2>
        <p className="text-muted mt-sm">
          Run an analysis from the Analysis page first.
        </p>
        <Link to="/analysis" className="btn mt" style={{ display: "inline-block" }}>
          Go to Analysis
        </Link>
      </div>
    );
  }

  const ctx = apiData.context || {};
  const analysis = apiData.analysis || {};
  const breakdown = analysis.breakdown || {};
  const profile = ctx.companyProfile || {};
  const stock = ctx.stockData || {};
  const fundamentals = ctx.fundamentals || {};
  const news = ctx.news || [];
  const macro = ctx.macroContext || {};
  const risk = breakdown.risk || {};

  const chartData = [...(ctx.priceHistory || [])]
    .reverse()
    .map((point) => ({
      date: point.date,
      close: point.close,
    }));

  const agents = [
    { name: "Research", data: breakdown.research, scoreKey: "score" },
    { name: "Macro", data: breakdown.macro, scoreKey: "score" },
    { name: "Sentiment", data: breakdown.sentiment, scoreKey: "score" },
    { name: "Risk", data: breakdown.risk, scoreKey: "riskScore" },
  ];

  const newsSources = [
    ...new Set(news.map((item) => item.source).filter(Boolean)),
    "PSX",
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Link to="/analysis" className="btn btn-sm" style={{ textDecoration: "none" }}>
          <ArrowLeft size={14} style={{ marginRight: 6, verticalAlign: "middle" }} />
          Back to Analysis
        </Link>
      </div>

      <div className="page-header">
        <div>
          <h1 className="page-title">
            {apiData.ticker} — {profile.companyName || "PSX Stock"}
          </h1>
          <p className="text-muted">
            {profile.sector || "Sector N/A"} • Opportunity score{" "}
            {analysis.opportunityScore ?? "—"}
          </p>
        </div>
        <Badge variant={signalVariant(analysis.signal)}>{analysis.signal}</Badge>
      </div>

      <div className="grid-4 mb">
        <div className="card stat-card">
          <div className="text-muted">Current Price</div>
          <div className="stat-value">Rs {stock.currentPrice ?? "—"}</div>
        </div>
        <div className="card stat-card">
          <div className="text-muted">Previous Close</div>
          <div className="stat-value">Rs {stock.previousClose ?? "—"}</div>
        </div>
        <div className="card stat-card">
          <div className="text-muted">Change %</div>
          <div
            className={`stat-value ${
              (stock.changePercent ?? 0) >= 0 ? "text-positive" : "text-negative"
            }`}
          >
            {stock.changePercent ?? "—"}%
          </div>
        </div>
        <div className="card stat-card">
          <div className="text-muted">Volume</div>
          <div className="stat-value">
            {stock.volume != null ? Number(stock.volume).toLocaleString() : "—"}
          </div>
        </div>
      </div>

      <div className="grid-2 mb">
        <div className="card">
          <h3 className="card-title">AI Recommendation</h3>
          <div className="grid-3">
            <div className="mini-stat">
              <div className="text-muted text-sm">Confidence</div>
              <div className="stat-value text-info">{analysis.confidence ?? "—"}%</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">Governance</div>
              <div className="font-semibold">{analysis.governanceStatus}</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">Risk Level</div>
              <div className="font-semibold text-negative">{risk.riskLevel || "—"}</div>
            </div>
          </div>
          <p className="mt text-muted">
            {breakdown.portfolio?.reasoningSummary || analysis.governanceReason}
          </p>
        </div>

        <div className="card">
          <h3 className="card-title">Fundamentals</h3>
          <div className="grid-2">
            <div className="mini-stat">
              <div className="text-muted text-sm">EPS</div>
              <div className="font-semibold">{fundamentals.eps ?? "—"}</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">P/E</div>
              <div className="font-semibold">{fundamentals.peRatio ?? "—"}</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">ROE</div>
              <div className="font-semibold">{fundamentals.roe ?? "—"}%</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">Dividend Yield</div>
              <div className="font-semibold">{fundamentals.dividendYield ?? 0}%</div>
            </div>
          </div>
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="card mb">
          <h3 className="card-title">Price History</h3>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} domain={["auto", "auto"]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="mb">
        <h3 className="card-title mb">Agent Analysis</h3>
        <div className="grid-2">
          {agents.map(({ name, data, scoreKey }) => (
            <div key={name} className="card">
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: 10,
                }}
              >
                <h4>{name} Agent</h4>
                <Badge
                  variant={
                    (data?.[scoreKey] ?? 0) >= 70
                      ? "positive"
                      : (data?.[scoreKey] ?? 0) >= 50
                        ? "info"
                        : "negative"
                  }
                >
                  {data?.[scoreKey] ?? "—"}
                </Badge>
              </div>
              <p className="text-muted text-sm">{data?.reasoning || "—"}</p>
            </div>
          ))}
        </div>
      </div>

      {news.length > 0 && (
        <div className="card mb">
          <h3 className="card-title">News</h3>
          <div className="decision-list" style={{ maxHeight: "none" }}>
            {news.map((item, index) => (
              <div key={index} className="decision-item">
                <div className="decision-header">
                  <span className="font-semibold">{item.headline}</span>
                  <Badge variant="info">{item.source}</Badge>
                </div>
                <p className="text-sm text-muted">{item.snippet}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card mb">
        <h3 className="card-title" style={{ color: "#dc2626" }}>
          Risk Warnings
        </h3>
        <div className="decision-list" style={{ maxHeight: "none" }}>
          {(risk.warnings || []).map((warning, index) => (
            <div
              key={index}
              className="decision-item"
              style={{ borderLeft: "4px solid #ef4444" }}
            >
              {warning}
            </div>
          ))}
        </div>
      </div>

      <div className="grid-2 mb">
        <div className="card">
          <h3 className="card-title">Macro Context</h3>
          <div className="grid-2">
            <div className="mini-stat">
              <div className="text-muted text-sm">SBP Rate</div>
              <div className="font-semibold">{macro.sbpPolicyRate}</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">PKR/USD</div>
              <div className="font-semibold">{macro.pkrUsdTrend}</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">Inflation</div>
              <div className="font-semibold">{macro.inflationView}</div>
            </div>
            <div className="mini-stat">
              <div className="text-muted text-sm">Market</div>
              <div className="font-semibold">{macro.marketCondition}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Governance Audit</h3>
          <Badge
            variant={analysis.governanceStatus === "APPROVED" ? "positive" : "warning"}
          >
            {analysis.governanceStatus}
          </Badge>
          <p className="text-muted mt-sm">{analysis.governanceReason}</p>
          {breakdown.governance?.finalNotes && (
            <p className="text-sm text-muted mt-sm">{breakdown.governance.finalNotes}</p>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Data Sources</h3>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12 }}>
          {newsSources.map((source) => (
            <span
              key={source}
              style={{
                background: "#f1f5f9",
                padding: "8px 14px",
                borderRadius: 999,
                fontWeight: 600,
                fontSize: "0.85rem",
              }}
            >
              {source}
            </span>
          ))}
        </div>
        {apiData.meta?.psxProfileSource && (
          <p className="text-xs text-muted mt-sm">
            PSX profile: {apiData.meta.psxProfileSource} • Generated{" "}
            {apiData.meta.generatedAt
              ? new Date(apiData.meta.generatedAt).toLocaleString()
              : "—"}
          </p>
        )}
      </div>
    </div>
  );
}
