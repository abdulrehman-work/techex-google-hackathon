import ComingSoon from "../components/common/ComingSoon";
const Agents = () => {
  return (
    <div className="text-white text-3xl flex justify-center items-center h-full">
      <ComingSoon title=" Agent Coming Soon" />
    </div>
  );
};

export default Agents;





// import {
//   TrendingUp,
//   Box,
//   Shield,
//   Target,
//   Cpu,
//   Activity,
// } from "lucide-react";
// import Header from "../components/layout/Header";
// import Badge from "../components/common/Badge";
// import { useApi } from "../hooks/useApi";
// import { api } from "../services/api";

// const AGENTS = [
//   {
//     name: "Market Analyst Agent",
//     icon: TrendingUp,
//     color: "#10b981",
//     desc: "Analyzes PSX historical data, moving averages, RSI, MACD, and order book depth for 14 tickers.",
//     role: "Technical analysis and pattern recognition across all monitored equities.",
//   },
//   {
//     name: "News & Sentiment Agent",
//     icon: Box,
//     color: "#3b82f6",
//     desc: "Scrapes Dawn, Business Recorder, and Twitter for macro-economic indicators and sentiment signals.",
//     role: "Real-time news ingestion and NLP-based sentiment scoring for market-moving events.",
//   },
//   {
//     name: "Risk Management Agent",
//     icon: Shield,
//     color: "#f59e0b",
//     desc: "Monitors portfolio beta, enforces stop-loss rules, and validates trades via on-chain RiskRouter.",
//     role: "Position sizing, exposure limits, and smart-contract risk validation (ERC-8004).",
//   },
//   {
//     name: "Portfolio Orchestrator",
//     icon: Target,
//     color: "#8b5cf6",
//     desc: "Combines signals from all agents to make final trade decisions with EIP-712 signed checkpoints.",
//     role: "Final decision authority — aggregates signals, executes via Kraken, posts on-chain proofs.",
//   },
// ];

// export default function Agents() {
//   const health = useApi(() => api.getHealth(), [], 30000);

//   return (
//     <>
//       <Header
//         title="Agent Swarm Network"
//         subtitle="Multi-agent system architecture for autonomous PSX trading"
//       />

//       {/* Architecture overview */}
//       <div className="card mb">
//         <h3 className="card-title">
//           <Cpu size={18} /> System Architecture
//         </h3>
//         <div className="arch-flow">
//           <div className="arch-step">
//             <span className="arch-label">Data Ingestion</span>
//             <span className="text-xs text-muted">
//               PRISM API + News Scrapers
//             </span>
//           </div>
//           <span className="arch-arrow">&rarr;</span>
//           <div className="arch-step">
//             <span className="arch-label">AI Analysis</span>
//             <span className="text-xs text-muted">
//               {health.data?.provider || "Anthropic"} LLM
//             </span>
//           </div>
//           <span className="arch-arrow">&rarr;</span>
//           <div className="arch-step">
//             <span className="arch-label">Risk Validation</span>
//             <span className="text-xs text-muted">On-chain RiskRouter</span>
//           </div>
//           <span className="arch-arrow">&rarr;</span>
//           <div className="arch-step">
//             <span className="arch-label">Execution</span>
//             <span className="text-xs text-muted">Kraken CLI</span>
//           </div>
//           <span className="arch-arrow">&rarr;</span>
//           <div className="arch-step">
//             <span className="arch-label">Audit</span>
//             <span className="text-xs text-muted">
//               EIP-712 Checkpoints
//             </span>
//           </div>
//         </div>
//       </div>

//       {/* Agent cards */}
//       <div className="grid grid-2">
//         {AGENTS.map((agent) => (
//           <div key={agent.name} className="card agent-card">
//             <div className="agent-header">
//               <div className="agent-icon" style={{ color: agent.color }}>
//                 <agent.icon size={22} />
//               </div>
//               <div>
//                 <h4>{agent.name}</h4>
//                 <Badge variant="positive">Active</Badge>
//               </div>
//             </div>
//             <p className="text-muted text-sm">{agent.desc}</p>
//             <div className="agent-role">
//               <Activity size={14} />
//               <span className="text-xs">{agent.role}</span>
//             </div>
//           </div>
//         ))}
//       </div>

//       {/* ERC-8004 Info */}
//       <div className="card mt">
//         <h3 className="card-title">
//           <Shield size={18} /> ERC-8004 Identity
//         </h3>
//         <p className="text-muted text-sm">
//           Every agent decision is cryptographically signed using EIP-712
//           typed data and posted as a checkpoint to the ValidationRegistry
//           on Sepolia. This creates an immutable, verifiable audit trail
//           that anyone can independently verify.
//         </p>
//         <div className="grid grid-3 mt-sm">
//           <div className="mini-stat">
//             <span className="text-xs text-muted">Registry</span>
//             <code className="text-xs">0x97b0...0ca3</code>
//           </div>
//           <div className="mini-stat">
//             <span className="text-xs text-muted">RiskRouter</span>
//             <code className="text-xs">0xd6A6...FdBC</code>
//           </div>
//           <div className="mini-stat">
//             <span className="text-xs text-muted">Vault</span>
//             <code className="text-xs">0x0E7C...fC90</code>
//           </div>
//         </div>
//       </div>
//     </>
//   );
// }
