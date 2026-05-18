import ComingSoon from "../components/common/ComingSoon";
const Dashboard = () => {
  return (
    <div className="text-white text-3xl flex justify-center items-center h-full">
      <ComingSoon title="Dashboard Coming Soon" />
    </div>
  );
};

export default Dashboard;














// import { TrendingUp, TrendingDown, BarChart3, Target } from "lucide-react";
// import {
//   AreaChart,
//   Area,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   ResponsiveContainer,
// } from "recharts";
// import Header from "../components/layout/Header";
// import StatCard from "../components/dashboard/StatCard";
// import Badge from "../components/common/Badge";
// import Loading from "../components/common/Loading";
// import ErrorBox from "../components/common/ErrorBox";
// import { useApi } from "../hooks/useApi";
// import { api } from "../services/api";

// export default function Dashboard() {
//   const perf = useApi(() => api.getPerformance(), [], 30000);
//   const decisions = useApi(() => api.getDecisions(10), [], 15000);

//   const perfData = perf.data;
//   const trades = perfData?.trades || [];

//   // Build chart data from recent trades
//   const chartData = trades.map((t, i) => ({
//     idx: i + 1,
//     pnl: t.pnl ?? 0,
//     cumPnl: trades
//       .slice(0, i + 1)
//       .reduce((s, tr) => s + (tr.pnl ?? 0), 0),
//   }));

//   return (
//     <>
//       <Header
//         title="Dashboard"
//         subtitle="Real-time overview of agent performance and trade signals"
//       />

//       {/* Stats row */}
//       <div className="grid grid-4">
//         <StatCard
//           label="Total Trades"
//           value={perfData?.total_trades ?? "—"}
//           icon={BarChart3}
//         />
//         <StatCard
//           label="Win Rate"
//           value={perfData ? `${perfData.win_rate}%` : "—"}
//           icon={Target}
//           trend={perfData?.win_rate >= 50 ? "up" : "down"}
//         />
//         <StatCard
//           label="Total P&L"
//           value={
//             perfData
//               ? `Rs. ${Number(perfData.total_pnl).toLocaleString()}`
//               : "—"
//           }
//           icon={perfData?.total_pnl >= 0 ? TrendingUp : TrendingDown}
//           trend={perfData?.total_pnl >= 0 ? "up" : "down"}
//         />
//         <StatCard
//           label="Recent Trades"
//           value={trades.length}
//           sub="Last 20 executions"
//           icon={BarChart3}
//         />
//       </div>

//       <div className="grid grid-2 mt">
//         {/* P&L Chart */}
//         <div className="card">
//           <h3 className="card-title">Cumulative P&L</h3>
//           {perf.loading ? (
//             <Loading />
//           ) : perf.error ? (
//             <ErrorBox message={perf.error} onRetry={perf.refetch} />
//           ) : chartData.length === 0 ? (
//             <p className="text-muted text-center py">
//               No trades yet — run analysis to generate signals
//             </p>
//           ) : (
//             <div style={{ height: 280 }}>
//               <ResponsiveContainer width="100%" height="100%">
//                 <AreaChart data={chartData}>
//                   <defs>
//                     <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
//                       <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
//                       <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
//                     </linearGradient>
//                   </defs>
//                   <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
//                   <XAxis
//                     dataKey="idx"
//                     stroke="#64748b"
//                     fontSize={11}
//                     tickLine={false}
//                   />
//                   <YAxis
//                     stroke="#64748b"
//                     fontSize={11}
//                     tickLine={false}
//                     tickFormatter={(v) => `${v >= 0 ? "+" : ""}${v}`}
//                   />
//                   <Tooltip
//                     contentStyle={{
//                       background: "#0f172a",
//                       border: "1px solid #1e293b",
//                       borderRadius: 8,
//                     }}
//                   />
//                   <Area
//                     type="monotone"
//                     dataKey="cumPnl"
//                     stroke="#3b82f6"
//                     strokeWidth={2}
//                     fill="url(#pnlGrad)"
//                     name="Cumulative P&L"
//                   />
//                 </AreaChart>
//               </ResponsiveContainer>
//             </div>
//           )}
//         </div>

//         {/* Recent Decisions */}
//         <div className="card">
//           <h3 className="card-title">Recent Decisions</h3>
//           {decisions.loading ? (
//             <Loading />
//           ) : decisions.error ? (
//             <ErrorBox message={decisions.error} onRetry={decisions.refetch} />
//           ) : (
//             <div className="decision-list">
//               {(decisions.data?.decisions || []).length === 0 ? (
//                 <p className="text-muted text-center py">No decisions yet</p>
//               ) : (
//                 (decisions.data?.decisions || []).map((d, i) => (
//                   <div key={i} className="decision-item">
//                     <div className="decision-header">
//                       <span className="font-semibold">{d.ticker}</span>
//                       <Badge
//                         variant={
//                           d.action === "BUY"
//                             ? "positive"
//                             : d.action === "SELL"
//                             ? "negative"
//                             : "neutral"
//                         }
//                       >
//                         {d.action}
//                       </Badge>
//                     </div>
//                     <p className="text-muted text-xs decision-reason">
//                       {d.reasoning?.slice(0, 120)}
//                       {d.reasoning?.length > 120 ? "..." : ""}
//                     </p>
//                     <div className="decision-meta">
//                       <span>Confidence: {d.confidence}%</span>
//                       <span>
//                         {new Date(d.created_at).toLocaleString()}
//                       </span>
//                     </div>
//                   </div>
//                 ))
//               )}
//             </div>
//           )}
//         </div>
//       </div>
//     </>
//   );
// }
