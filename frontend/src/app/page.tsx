"use client";

import { useState } from "react";
import { AlertCircle, CheckCircle2, Database, RefreshCw } from "lucide-react";

interface Exception {
  category: string;
  order_id: string;
  bank_txn_id?: string;
  details: string;
  gross_amount: number;
}

interface ReconciliationResult {
  total_records: number;
  reconciled_count: number;
  exception_count: number;
  match_rate: number;
  exceptions: Exception[];
}

interface AIDiagnosis {
  root_cause_analysis: string;
  recommended_action: string;
  confidence_score: number;
  requires_human_escalation: boolean;
}

export default function Dashboard() {
  const [data, setData] = useState<ReconciliationResult | null>(null);
  const [loading, setLoading] = useState(false);

  // AI Investigation States
  const [selectedException, setSelectedException] = useState<Exception | null>(null);
  const [aiDiagnosis, setAiDiagnosis] = useState<AIDiagnosis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const runReconciliation = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/reconcile", {
        method: "POST",
      });
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error("Failed to fetch reconciliation data:", error);
    } finally {
      setLoading(false);
    }
  };

  const investigateException = async (exception: Exception) => {
    setSelectedException(exception);
    setAiDiagnosis(null);
    setAnalyzing(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/resolve-exception", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(exception),
      });
      const result = await response.json();
      setAiDiagnosis(result);
    } catch (error) {
      console.error("AI resolution failed:", error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8 text-gray-900">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header Section */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AI Finance Controller</h1>
            <p className="text-gray-500 mt-1">Autonomous 3-Way Payment Reconciliation</p>
          </div>
          <button
            onClick={runReconciliation}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? <RefreshCw className="animate-spin" size={20} /> : <Database size={20} />}
            {loading ? "Processing Batch..." : "Run Reconciliation Loop"}
          </button>
        </div>

        {/* Metrics Row */}
        {data && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard title="Total Volume" value={data.total_records.toLocaleString()} />
            <MetricCard
              title="Match Rate"
              value={`${data.match_rate}%`}
              highlight={data.match_rate > 70 ? "text-green-600" : "text-yellow-600"}
            />
            <MetricCard
              title="Auto-Reconciled"
              value={data.reconciled_count.toLocaleString()}
              icon={<CheckCircle2 className="text-green-500" />}
            />
            <MetricCard
              title="Exceptions Flagged"
              value={data.exception_count.toLocaleString()}
              icon={<AlertCircle className="text-red-500" />}
            />
          </div>
        )}

        {/* Exception Ledger */}
        {data && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Exception Ledger (AI Queue)</h2>
              <p className="text-sm text-gray-500 mt-1">Records requiring LLM diagnostic resolution.</p>
            </div>
            <div className="overflow-x-auto h-[500px] overflow-y-scroll">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 sticky top-0 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 font-medium text-gray-600">Category</th>
                    <th className="px-6 py-3 font-medium text-gray-600">Reference ID</th>
                    <th className="px-6 py-3 font-medium text-gray-600">Amount (₹)</th>
                    <th className="px-6 py-3 font-medium text-gray-600">System Diagnostic</th>
                    <th className="px-6 py-3 font-medium text-gray-600">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data.exceptions.map((exc, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          {exc.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs">{exc.order_id !== "N/A" ? exc.order_id : exc.bank_txn_id}</td>
                      <td className="px-6 py-4 font-medium">{exc.gross_amount.toLocaleString()}</td>
                      <td className="px-6 py-4 text-gray-600">{exc.details}</td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => investigateException(exc)}
                          className="text-xs bg-indigo-50 text-indigo-600 px-3 py-1.5 rounded hover:bg-indigo-100 font-medium transition-colors whitespace-nowrap"
                        >
                          AI Investigate
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* AI Diagnostic Modal */}
      {selectedException && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">AI Diagnostic Report</h3>
              <button onClick={() => setSelectedException(null)} className="text-gray-400 hover:text-gray-600">Close</button>
            </div>
            <div className="p-6">
              {analyzing ? (
                <div className="flex flex-col items-center justify-center py-12 gap-3 text-indigo-600">
                  <RefreshCw className="animate-spin" size={32} />
                  <p className="text-sm font-medium">DeepSeek analyzing settlement discrepancy...</p>
                </div>
              ) : aiDiagnosis ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-xs font-semibold text-gray-500 uppercase">Root Cause Analysis</p>
                    <p className="text-sm text-gray-800 mt-1">{aiDiagnosis.root_cause_analysis}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-gray-500 uppercase">Recommended Action</p>
                    <p className="text-sm text-gray-800 mt-1">{aiDiagnosis.recommended_action}</p>
                  </div>
                  <div className="flex gap-4 pt-4 border-t border-gray-100">
                    <div className="bg-gray-50 px-3 py-2 rounded">
                      <p className="text-xs text-gray-500">Confidence</p>
                      <p className="text-sm font-bold text-gray-900">{(aiDiagnosis.confidence_score * 100).toFixed(1)}%</p>
                    </div>
                    <div className={`px-3 py-2 rounded ${aiDiagnosis.requires_human_escalation ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                      <p className="text-xs opacity-80">Escalation</p>
                      <p className="text-sm font-bold">{aiDiagnosis.requires_human_escalation ? 'Required' : 'Auto-Resolvable'}</p>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function MetricCard({ title, value, icon, highlight = "text-gray-900" }: any) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col gap-2">
      <div className="flex justify-between items-start">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        {icon}
      </div>
      <p className={`text-3xl font-bold tracking-tight ${highlight}`}>{value}</p>
    </div>
  );
}