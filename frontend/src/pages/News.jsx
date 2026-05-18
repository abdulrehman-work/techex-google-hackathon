import ComingSoon from "../components/common/ComingSoon";
const News = () => {
  return (
    <div className="text-white text-3xl flex justify-center items-center h-full">
      <ComingSoon title=" News Coming Soon" />
    </div>
  );
};

export default News;



// import { ExternalLink } from "lucide-react";
// import Header from "../components/layout/Header";
// import Badge from "../components/common/Badge";
// import Loading from "../components/common/Loading";
// import ErrorBox from "../components/common/ErrorBox";
// import { useApi } from "../hooks/useApi";
// import { api } from "../services/api";

// function sentimentVariant(s) {
//   if (!s) return "neutral";
//   const val = typeof s === "string" ? s.toLowerCase() : "";
//   if (val === "positive" || val === "bullish") return "positive";
//   if (val === "negative" || val === "bearish") return "negative";
//   return "warning";
// }

// export default function News() {
//   const { data, loading, error, refetch } = useApi(
//     () => api.getNews(30),
//     [],
//     60000
//   );

//   const articles = data?.articles || [];

//   return (
//     <>
//       <Header
//         title="News Feed"
//         subtitle="Scraped headlines from Dawn, Business Recorder, and other sources"
//       />

//       {loading ? (
//         <Loading message="Loading news..." />
//       ) : error ? (
//         <ErrorBox message={error} onRetry={refetch} />
//       ) : articles.length === 0 ? (
//         <div className="card">
//           <p className="text-muted text-center py">
//             No news articles scraped yet. The news agent scrapes
//             periodically.
//           </p>
//         </div>
//       ) : (
//         <div className="news-grid">
//           {articles.map((a, i) => (
//             <div key={i} className="card news-card">
//               <div className="news-header">
//                 <Badge variant={sentimentVariant(a.sentiment)}>
//                   {a.sentiment || "Neutral"}
//                 </Badge>
//                 <span className="text-xs text-muted">
//                   {a.source || "Unknown"}
//                 </span>
//               </div>
//               <h4 className="news-title">{a.title}</h4>
//               <p className="text-muted text-sm news-summary">
//                 {a.summary?.slice(0, 200) || a.content?.slice(0, 200)}
//               </p>
//               <div className="news-footer">
//                 <span className="text-xs text-muted">
//                   {a.published_at
//                     ? new Date(a.published_at).toLocaleString()
//                     : ""}
//                 </span>
//                 {a.url && (
//                   <a
//                     href={a.url}
//                     target="_blank"
//                     rel="noopener noreferrer"
//                     className="news-link"
//                   >
//                     <ExternalLink size={12} /> Source
//                   </a>
//                 )}
//               </div>
//             </div>
//           ))}
//         </div>
//       )}
//     </>
//   );
// }
