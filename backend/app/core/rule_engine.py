import numpy as np
import pandas as pd

CONTRACT_MDR_RATE = 0.02
GST_ON_FEE = 0.18


def run_deterministic_reconciliation(
    erp_path: str, pg_path: str, bank_path: str
):
    erp_df = pd.read_csv(erp_path)
    pg_df = pd.read_csv(pg_path)
    bank_df = pd.read_csv(bank_path)

    # 1. Join ERP and Payment Gateway records on order_id
    erp_pg_merge = pd.merge(
        erp_df,
        pg_df,
        on="order_id",
        how="outer",
        suffixes=("_erp", "_pg"),
        indicator="_merge_erp_pg",
    )

    reconciled = []
    flagged_for_agent = []

    for _, row in erp_pg_merge.iterrows():
        # Case A: Missing Gateway callback (Abandoned/Failed payment)
        if row["_merge_erp_pg"] == "left_only":
            flagged_for_agent.append(
                {
                    "order_id": row["order_id"],
                    "category": "MISSING_PG_RECORD",
                    "details": f"ERP order completed without gateway settlement.",
                    "gross_amount": row["gross_amount_erp"],
                }
            )
            continue

        # Case B: Disputed / Chargeback status
        if row["status_pg"] == "DISPUTED":
            flagged_for_agent.append(
                {
                    "order_id": row["order_id"],
                    "pg_txn_id": row["pg_txn_id"],
                    "category": "CHARGEBACK",
                    "details": f"Gateway flagged transaction as disputed.",
                    "gross_amount": row["gross_amount_pg"],
                }
            )
            continue

        # Case C: Fee Discrepancy Check (Verify contractual 2% MDR)
        expected_fee = round(row["gross_amount_pg"] * CONTRACT_MDR_RATE, 2)
        if abs(row["fee"] - expected_fee) > 0.05:
            flagged_for_agent.append(
                {
                    "order_id": row["order_id"],
                    "pg_txn_id": row["pg_txn_id"],
                    "category": "MDR_DISCREPANCY",
                    "details": f"Expected fee ₹{expected_fee}, actual fee charged ₹{row['fee']}",
                    "gross_amount": row["gross_amount_pg"],
                    "fee_variance": round(row["fee"] - expected_fee, 2),
                }
            )
            continue

        # Case D: Clean 1:1 settlement match
        reconciled.append(
            {
                "order_id": row["order_id"],
                "pg_txn_id": row["pg_txn_id"],
                "settlement_id": row["settlement_id"],
                "net_amount": row["net_amount"],
                "status": "RECONCILED",
            }
        )

    # 2. Check Bank Statement for Unmatched Phantom Credits
    matched_pg_set = set(erp_pg_merge["pg_txn_id"].dropna())
    
    for _, bank_row in bank_df.iterrows():
        # Skip batch settlements or debits
        if "BATCH" in str(bank_row["narration"]) or bank_row["type"] != "CREDIT":
            continue
            
        # Extract PG txn ID from narration (e.g., CMS/RAZORPAY/pay_xyz/...)
        extracted_pg_id = next((part for part in str(bank_row["narration"]).split('/') if part.startswith('pay_')), None)
        
        if extracted_pg_id not in matched_pg_set:
            flagged_for_agent.append(
                {
                    "order_id": "N/A",
                    "bank_txn_id": bank_row["bank_txn_id"],
                    "category": "PHANTOM_BANK_CREDIT",
                    "details": f"Bank credit of ₹{bank_row['amount']} with no matching ERP/PG record.",
                    "gross_amount": bank_row["amount"],
                }
            )

    return {
        "total_records": len(erp_df),
        "reconciled_count": len(reconciled),
        "exception_count": len(flagged_for_agent),
        "match_rate": round((len(reconciled) / len(erp_df)) * 100, 2), # Fixed match rate math
        "reconciled_sample": reconciled[:10],
        "exceptions": flagged_for_agent,
    }