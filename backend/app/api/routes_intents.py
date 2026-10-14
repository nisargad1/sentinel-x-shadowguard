import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.schemas.intent import IntentContract, IntentEvaluateRequest, IntentEvaluateResponse
from app.services.intent_engine import IntentContractEngine
from app.models.intent_contract import IntentContractRecord

router = APIRouter(prefix="/intents", tags=["Intent Contracts & Drift Monitoring"])

@router.post("/contract", response_model=IntentContract)
def generate_contract(user_goal: str, db: Session = Depends(get_db)):
    """
    Parses natural language user goals into structured, enforceable Intent Contracts.
    """
    contract = IntentContractEngine.generate_contract(user_goal)
    
    # Persist contract for auditability
    record = IntentContractRecord(
        id=contract.contract_id,
        user_goal=contract.user_goal,
        permitted_resources=json.dumps(contract.permitted_resources),
        permitted_actions=json.dumps(contract.permitted_actions),
        prohibited_actions=json.dumps(contract.prohibited_actions),
        risk_constraints=json.dumps(contract.risk_constraints)
    )
    db.add(record)
    db.commit()

    return contract

@router.post("/evaluate", response_model=IntentEvaluateResponse)
def evaluate_intent_drift(req: IntentEvaluateRequest):
    """
    Evaluates whether proposed agent actions conform to the contract or represent intent drift.
    """
    return IntentContractEngine.evaluate_intent(
        user_goal=req.user_goal,
        tool_name=req.tool_name,
        tool_arguments=req.tool_arguments
    )

@router.get("", response_model=List[IntentContract])
def list_intent_contracts(limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieves stored intent contracts.
    """
    records = db.query(IntentContractRecord).order_by(desc(IntentContractRecord.created_at)).limit(limit).all()
    results = []
    for r in records:
        try:
            results.append(IntentContract(
                contract_id=r.id,
                user_goal=r.user_goal,
                permitted_resources=json.loads(r.permitted_resources),
                permitted_actions=json.loads(r.permitted_actions),
                prohibited_actions=json.loads(r.prohibited_actions),
                risk_constraints=json.loads(r.risk_constraints)
            ))
        except Exception:
            continue
    return results
