import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Play, Loader2 } from "lucide-react";

import Header from "../components/layout/Header";

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

export default function Analysis() {
  const navigate = useNavigate();

  const [selected, setSelected] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("");

  const filtered = TICKERS.filter((t) =>
    t.toLowerCase().includes(filter.toLowerCase())
  );

  // API CALL
  const handleRun = async (ticker) => {
    try {
      setSelected(ticker);
      setRunning(true);
      setError(null);

      const response = await fetch(
        "https://techex-google-hackathon.onrender.com/api/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ticker: ticker,
          }),
        }
      );

      const data = await response.json();

      console.log("API RESPONSE:", data);

      // NAVIGATE TO PORTFOLIO
      navigate("/portfolio", {
        state: {
          analysisData: data,
        },
      });

    } catch (err) {
      console.error(err);

      setError("Failed to fetch analysis.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <>
      <Header
        title="Run Analysis"
        subtitle="Analyze PSX tickers using AI-powered agents"
      />

      {/* SEARCH */}
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

      {/* TICKER GRID */}
      <div className="ticker-grid">
        {filtered.map((ticker) => (
          <button
            key={ticker}
            className={`ticker-btn ${selected === ticker ? "selected" : ""
              }`}
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

      {/* LOADING */}
      {running && (
        <div className="card mt">
          <div className="analysis-running">
            <Loader2 size={20} className="spin" />

            <span>
              Running AI analysis on{" "}
              <strong>{selected}</strong>...
            </span>
          </div>
        </div>
      )}

      {/* ERROR */}
      {error && (
        <div className="card mt error-box">
          <p>{error}</p>
        </div>
      )}
    </>
  );
}



// import { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import { Search, Play, Loader2 } from "lucide-react";
// import Header from "../components/layout/Header";
// import Badge from "../components/common/Badge";
// import { api } from "../services/api";
// import { useNavigate } from "react-router-dom";

// const TICKERS = [
//   "OGDC", "ENGRO", "HBL", "UBL", "MCB", "LUCK", "EFERT",
//   "PPL", "PSO", "SEARL", "NESTLE", "COLG", "ATRL", "MARI",
// ];

// export default function Analysis() {
//   const navigate = useNavigate(); //aded
//   const [selected, setSelected] = useState(null);
//   const [running, setRunning] = useState(false);
//   const [result, setResult] = useState(null);
//   const [error, setError] = useState(null);
//   const [filter, setFilter] = useState("");

//   const filtered = TICKERS.filter((t) =>
//     t.toLowerCase().includes(filter.toLowerCase())
//   );

async function handleRun(ticker) {
  setSelected(ticker);
  setRunning(true);
  setResult(null);
  setError(null);
  try {
    const data = await api.runAnalysis(ticker);
    setResult(data);
  } catch (err) {
    setError(err.response?.data?.error || err.message);
  } finally {
    setRunning(false);
  }
  const data = await api.runAnalysis(ticker);

  navigate("/portfolio", {
    state: {
      data,
    },
  });
}

//   const handleTickerClick = (ticker) => {
//     navigate("/portfolio", {
//       state: { ticker },
//     });
//   };

//   return (
//     <>
//       <Header
//         title="Run Analysis"
//         subtitle="Trigger AI analysis for any PSX ticker — analyst, news, and risk agents collaborate"
//       />

//       {/* Ticker search */}
//       <div className="card mb">
//         <div className="search-bar">
//           <Search size={16} className="text-muted" />
//           <input
//             type="text"
//             placeholder="Filter tickers..."
//             value={filter}
//             onChange={(e) => setFilter(e.target.value)}
//             className="search-input"
//           />
//         </div>
//       </div>

//       {/* Ticker grid */}
//       <div className="ticker-grid">
//         {filtered.map((ticker) => (
//           <button
//             key={ticker}
//             className={`ticker-btn ${selected === ticker ? "selected" : ""}`}
//             onClick={() => handleRun(ticker)}
//             disabled={running}
//           >
//             {running && selected === ticker ? (
//               <Loader2 size={16} className="spin" />
//             ) : (
//               <Play size={14} />
//             )}
//             {ticker}
//           </button>
//         ))}
//       </div>

//       {/* Result */}
//       {running && (
//         <div className="card mt">
//           <div className="analysis-running">
//             <Loader2 size={20} className="spin" />
//             <span>
//               Running full analysis on <strong>{selected}</strong>...
//               This may take 30–60 seconds.
//             </span>
//           </div>
//         </div>
//       )}

//       {error && (
//         <div className="card mt error-box">
//           <p>{error}</p>
//         </div>
//       )}

//       {result && !running && (
//         <div className="card mt">
//           <h3 className="card-title">
//             Analysis Result — {selected}
//           </h3>
//           <div className="analysis-result">
//             {result.decision && (
//               <div className="result-section">
//                 <h4>Decision</h4>
//                 <div className="result-row">
//                   <Badge
//                     variant={
//                       result.decision.action === "BUY"
//                         ? "positive"
//                         : result.decision.action === "SELL"
//                           ? "negative"
//                           : "neutral"
//                     }
//                   >
//                     {result.decision.action}
//                   </Badge>
//                   <span>
//                     Confidence: {result.decision.confidence}%
//                   </span>
//                 </div>
//                 {result.decision.reasoning && (
//                   <p className="text-sm text-muted mt-sm">
//                     {result.decision.reasoning}
//                   </p>
//                 )}
//               </div>
//             )}

//             {result.signals && (
//               <div className="result-section">
//                 <h4>Signals</h4>
//                 <pre className="result-json">
//                   {JSON.stringify(result.signals, null, 2)}
//                 </pre>
//               </div>
//             )}

//             {result.checkpoint && (
//               <div className="result-section">
//                 <h4>EIP-712 Checkpoint</h4>
//                 <pre className="result-json">
//                   {JSON.stringify(result.checkpoint, null, 2)}
//                 </pre>
//               </div>
//             )}
//           </div>
//         </div>
//       )}
//     </>
//   );
// }
