import { Shield } from "lucide-react";
import Header from "../components/layout/Header";
import Badge from "../components/common/Badge";
import Loading from "../components/common/Loading";
import ErrorBox from "../components/common/ErrorBox";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

export default function Audit() {
  const { data, loading, error, refetch } = useApi(
    () => api.getAudit(50),
    [],
    30000
  );

  const logs = data?.audit || [];

  return (
    <>
      <Header
        title="On-chain Audit Log"
        subtitle="EIP-712 signed checkpoints posted to ValidationRegistry (Sepolia)"
      />

      <div className="card mb">
        <div className="audit-info">
          <Shield size={18} className="text-info" />
          <p className="text-sm text-muted">
            Every trade decision produces a cryptographically signed
            checkpoint using EIP-712 typed data. These are posted to the
            Sepolia ValidationRegistry, creating an immutable audit trail
            verifiable by anyone on-chain.
          </p>
        </div>
      </div>

      {loading ? (
        <Loading message="Loading audit log..." />
      ) : error ? (
        <ErrorBox message={error} onRetry={refetch} />
      ) : logs.length === 0 ? (
        <div className="card">
          <p className="text-muted text-center py">No audit entries yet</p>
        </div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Ticker</th>
                  <th>Action</th>
                  <th>Agent</th>
                  <th>Tx Hash</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr key={i}>
                    <td className="text-xs">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="font-semibold">
                      {log.ticker || "—"}
                    </td>
                    <td>{log.action || log.event_type || "—"}</td>
                    <td>{log.agent || "System"}</td>
                    <td>
                      {log.tx_hash ? (
                        <a
                          href={`https://sepolia.etherscan.io/tx/${log.tx_hash}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hash-link"
                        >
                          {log.tx_hash.slice(0, 10)}...
                        </a>
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td>
                      <Badge variant="positive">Verified</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
