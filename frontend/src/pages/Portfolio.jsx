import { useLocation } from "react-router-dom";

export default function Portfolio() {
  const location = useLocation();

  // API response coming from navigate state
  const apiData = location.state?.data;

  // Loading fallback
  if (!apiData) {
    return (
      <div
        style={{
          minHeight: "80vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div className="card">
          <h2>No Analysis Data Found</h2>
          <p className="text-muted">
            Please run analysis first.
          </p>
        </div>
      </div>
    );
  }

  // MAPPING API RESPONSE
  const data = {
    ticker: apiData?.ticker,

    companyProfile: {
      companyName:
        apiData?.context?.companyProfile?.companyName,

      sector:
        apiData?.context?.companyProfile?.sector,
    },

    stock: {
      currentPrice:
        apiData?.context?.stockData?.currentPrice,

      previousClose:
        apiData?.context?.stockData?.previousClose,

      changePercent:
        apiData?.context?.stockData?.changePercent,

      volume:
        apiData?.context?.stockData?.volume,
    },

    recommendation: {
      action:
        apiData?.analysis?.signal,

      confidence:
        apiData?.analysis?.confidence,

      targetView:
        apiData?.analysis?.breakdown?.sentiment?.label,

      timeHorizon: "Medium Term",

      summary:
        apiData?.analysis?.breakdown?.portfolio
          ?.reasoningSummary,
    },

    agents: [
      {
        name: "Research Agent",

        score:
          apiData?.analysis?.breakdown?.research
            ?.score,

        summary:
          apiData?.analysis?.breakdown?.research
            ?.reasoning,
      },

      {
        name: "Macro Agent",

        score:
          apiData?.analysis?.breakdown?.macro
            ?.score,

        summary:
          apiData?.analysis?.breakdown?.macro
            ?.reasoning,
      },

      {
        name: "Sentiment Agent",

        score:
          apiData?.analysis?.breakdown?.sentiment
            ?.score,

        summary:
          apiData?.analysis?.breakdown?.sentiment
            ?.reasoning,
      },

      {
        name: "Risk Agent",

        score:
          apiData?.analysis?.breakdown?.risk
            ?.riskScore,

        summary:
          apiData?.analysis?.breakdown?.risk
            ?.reasoning,
      },
    ],

    risk: {
      level:
        apiData?.analysis?.breakdown?.risk
          ?.riskLevel,

      warnings:
        apiData?.analysis?.breakdown?.risk
          ?.warnings || [],
    },

    audit: {
      status:
        apiData?.analysis?.governanceStatus,

      summary:
        apiData?.analysis?.governanceReason,
    },

    dataSources: [
      "PSX",
      "Business Recorder",
      "SBP",
      "IFC",
    ],
  };

  return (
    <div>

      {/* HEADER */}

      <div className="page-header">
        <div>
          <h1 className="page-title">
            {data.ticker} Portfolio Analysis
          </h1>

          <p className="text-muted">
            {data.companyProfile.companyName} •{" "}
            {data.companyProfile.sector}
          </p>
        </div>

        <div
          style={{
            padding: "14px 30px",
            borderRadius: "16px",
            fontWeight: "800",
            fontSize: "1.1rem",
            letterSpacing: "0.08em",

            background:
              data.recommendation.action === "BUY"
                ? "#dcfce7"
                : data.recommendation.action === "SELL"
                  ? "#fee2e2"
                  : "#dbeafe",

            color:
              data.recommendation.action === "BUY"
                ? "#166534"
                : data.recommendation.action === "SELL"
                  ? "#991b1b"
                  : "#1e40af",
          }}
        >
          {data.recommendation.action}
        </div>
      </div>

      {/* TOP STATS */}

      <div className="grid-4 mb">

        <div className="card stat-card">
          <div className="text-muted">
            Current Price
          </div>

          <div className="stat-value">
            Rs {data.stock.currentPrice}
          </div>
        </div>

        <div className="card stat-card">
          <div className="text-muted">
            Previous Close
          </div>

          <div className="stat-value">
            Rs {data.stock.previousClose}
          </div>
        </div>

        <div className="card stat-card">
          <div className="text-muted">
            Change %
          </div>

          <div
            className={`stat-value ${data.stock.changePercent >= 0
                ? "text-positive"
                : "text-negative"
              }`}
          >
            {data.stock.changePercent}%
          </div>
        </div>

        <div className="card stat-card">
          <div className="text-muted">
            Volume
          </div>

          <div className="stat-value">
            {data.stock.volume?.toLocaleString()}
          </div>
        </div>

      </div>

      {/* MARKET OUTLOOK */}

      <div className="card mb">

        <div className="card-title">
          Market Outlook
        </div>

        <div className="grid-3">

          <div className="mini-stat">
            <div className="text-muted text-sm">
              Confidence
            </div>

            <div className="stat-value text-info">
              {data.recommendation.confidence}%
            </div>
          </div>

          <div className="mini-stat">
            <div className="text-muted text-sm">
              Time Horizon
            </div>

            <div className="font-semibold">
              {data.recommendation.timeHorizon}
            </div>
          </div>

          <div className="mini-stat">
            <div className="text-muted text-sm">
              Market View
            </div>

            <div className="font-semibold">
              {data.recommendation.targetView}
            </div>
          </div>

        </div>

        <p className="mt text-muted">
          {data.recommendation.summary}
        </p>

      </div>

      {/* AGENTS */}

      <div className="mb">

        <div className="card-title mb">
          Agent Analysis
        </div>

        <div className="grid-2">

          {data.agents.map((agent, index) => (
            <div
              key={index}
              className="card"
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "12px",
                }}
              >
                <h4>{agent.name}</h4>

                <div
                  style={{
                    background:
                      agent.score >= 70
                        ? "#dcfce7"
                        : agent.score >= 50
                          ? "#dbeafe"
                          : "#fee2e2",

                    color:
                      agent.score >= 70
                        ? "#166534"
                        : agent.score >= 50
                          ? "#1d4ed8"
                          : "#991b1b",

                    padding: "6px 12px",
                    borderRadius: "999px",
                    fontWeight: "700",
                  }}
                >
                  {agent.score}
                </div>
              </div>

              <p className="text-muted text-sm">
                {agent.summary}
              </p>
            </div>
          ))}

        </div>

      </div>

      {/* RISK */}

      <div className="card mb">

        <div
          className="card-title"
          style={{
            color: "#dc2626",
          }}
        >
          Risk Analysis
        </div>

        <div className="mini-stat mb">

          <div className="text-muted text-sm">
            Risk Level
          </div>

          <div
            className="stat-value"
            style={{
              color: "#dc2626",
            }}
          >
            {data.risk.level}
          </div>

        </div>

        <div className="decision-list">

          {data.risk.warnings.map(
            (warning, index) => (
              <div
                key={index}
                className="decision-item"
                style={{
                  borderLeft:
                    "4px solid #ef4444",
                  marginBottom: "12px",
                  padding: "14px",
                  background: "#fff5f5",
                  borderRadius: "12px",
                }}
              >
                <div
                  style={{
                    color: "#b91c1c",
                    fontWeight: "700",
                    marginBottom: "6px",
                  }}
                >
                  Warning
                </div>

                <div className="text-sm">
                  {warning}
                </div>
              </div>
            )
          )}

        </div>

      </div>

      {/* GOVERNANCE */}

      <div className="card mb">

        <div className="card-title">
          Governance Audit
        </div>

        <div className="mini-stat mb">

          <div className="text-muted text-sm">
            Status
          </div>

          <div
            className="stat-value"
            style={{
              color: "#16a34a",
            }}
          >
            {data.audit.status}
          </div>

        </div>

        <p className="text-muted">
          {data.audit.summary}
        </p>

      </div>

      {/* SOURCES */}

      <div className="card">

        <div className="card-title">
          Data Sources
        </div>

        <div
          style={{
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
            marginTop: "14px",
          }}
        >
          {data.dataSources.map(
            (source, index) => (
              <div
                key={index}
                style={{
                  background: "#f1f5f9",
                  padding: "10px 16px",
                  borderRadius: "999px",
                  fontWeight: "600",
                  color: "#334155",
                }}
              >
                {source}
              </div>
            )
          )}
        </div>

      </div>

    </div>
  );
}