import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_URL || "https://techex-google-hackathon.onrender.com";

const client = axios.create({
  baseURL: API_BASE,
  timeout: 180000,
  headers: { "Content-Type": "application/json" },
});

export async function analyzeStock(ticker) {
  const response = await client.post("/api/analyze", {
    ticker: String(ticker).trim().toUpperCase(),
  });
  return response.data;
}

export function saveAnalysisResult(result) {
  if (!result?.ticker) return;
  sessionStorage.setItem(`analysis:${result.ticker}`, JSON.stringify(result));
}

export function loadAnalysisResult(ticker) {
  if (!ticker) return null;
  const raw = sessionStorage.getItem(`analysis:${String(ticker).toUpperCase()}`);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export const api = { analyzeStock, saveAnalysisResult, loadAnalysisResult };
