// import axios from "axios";

// const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// const client = axios.create({
//   baseURL: API_BASE,
//   timeout: 30000,
// });

// export const api = {
//   // Health check
//   getHealth: () => client.get("/api/health").then((r) => r.data),

//   // Portfolio positions
//   getPortfolio: () => client.get("/api/portfolio").then((r) => r.data),

//   // Trade decisions
//   getDecisions: (limit = 20) =>
//     client.get("/api/decisions", { params: { limit } }).then((r) => r.data),

//   // Signals for a specific ticker
//   getSignals: (ticker) =>
//     client.get(`/api/signals/${ticker}`).then((r) => r.data),

//   // News articles
//   getNews: (limit = 30) =>
//     client.get("/api/news", { params: { limit } }).then((r) => r.data),

//   // Performance stats + recent trades
//   getPerformance: () => client.get("/api/performance").then((r) => r.data),

//   // Trigger manual analysis for a ticker
//   runAnalysis: (ticker) =>
//     client.post(`/api/run-analysis/${ticker}`).then((r) => r.data),

//   // On-chain audit log
//   getAudit: (limit = 50) =>
//     client.get("/api/audit", { params: { limit } }).then((r) => r.data),
// };


import axios from "axios";

const BASE_URL =
  "https://techex-google-hackathon.onrender.com/api";

export const api = {
  async runAnalysis(ticker) {
    const response = await axios.post(
      `${BASE_URL}/analyze`,
      {
        ticker,
      }
    );

    return response.data;
  },
};