from app.core.agent import resolve_exception_with_ai
from app.core.rule_engine import run_deterministic_reconciliation
from fastapi import APIRouter, Body
import os

router = APIRouter(prefix="/api/v1")

@router.post("/reconcile")
def execute_reconciliation():
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
    )
    # Ensure these paths match where your CSVs are stored
    erp_path = os.path.join(base_path, "erp_orders.csv")
    pg_path = os.path.join(base_path, "pg_settlements.csv")
    bank_path = os.path.join(base_path, "bank_statement.csv")

    results = run_deterministic_reconciliation(erp_path, pg_path, bank_path)
    return results

@router.post("/resolve-exception")
def execute_ai_resolution(exception_data: dict = Body(...)):
    """
    Passes a single flagged exception to the DeepSeek LLM for diagnosis.
    """
    ai_diagnosis = resolve_exception_with_ai(exception_data)
    return ai_diagnosis