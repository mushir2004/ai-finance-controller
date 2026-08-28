# AI Finance Controller: Autonomous 3-Way Reconciliation

A closed-loop financial operations agent built for the Razorpay AI Buildathon. It reconciles a 5,000-record synthetic batch across ERP, Payment Gateway, and Bank Statement ledgers.

## The Problem
The 2026 builder consensus is clear: **verification capacity, not generation speed, is the bottleneck** in finance operations. Reconciliation, settlement, and forecasting are still done by hand because traditional LLM agents hallucinate numbers. 

## The Hybrid Architecture Solution
This system proves throughput and measured accuracy by combining high-speed deterministic rules with targeted LLM reasoning for edge cases.

1. **Deterministic Rule Engine (Pass 1):** Vectorized pandas logic instantly reconciles 1:1 matches, calculates exact MDR fee variances, and maps batch bank rollups. 
2. **LLM Agent (Pass 2):** Unstructured anomalies (cryptic bank memo chargebacks, phantom credits) are isolated into an Exception Queue. The LLM (via NVIDIA API) is only invoked to diagnose these specific edge cases, enforcing a strict JSON diagnostic schema.
3. **Honest Exception Ledger:** No forced matches. If a bank credit lacks a trace ID, it remains flagged for human escalation.

## Tech Stack
* **Backend:** FastAPI, Python, Pandas (Rule Engine), OpenAI SDK.
* **LLM Engine:** Llama 3.1 70B / DeepSeek v4 (via NVIDIA API Catalog).
* **Frontend:** Next.js, React, Tailwind CSS.

## Benchmark Results (5,000 Synthetic Records)
* **Match Rate:** ~80.8% auto-reconciled deterministically.
* **Exceptions Flagged:** ~1,000 targeted cases (MDR discrepancies, phantom credits, missing callbacks).
* **Throughput:** Deterministic pass completes in milliseconds; AI diagnostics run on-demand for specific ledger exceptions.
