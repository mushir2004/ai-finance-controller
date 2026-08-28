import os
from app.core.rule_engine import run_deterministic_reconciliation
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.post("/reconcile")
def execute_reconciliation():
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
    )
    erp_path = os.path.join(base_path, "erp_orders.csv")
    pg_path = os.path.join(base_path, "pg_settlements.csv")
    bank_path = os.path.join(base_path, "bank_statement.csv")

    results = run_deterministic_reconciliation(erp_path, pg_path, bank_path)
    return results