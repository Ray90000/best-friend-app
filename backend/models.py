import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Member(BaseModel):
    name: str

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payer: str
    amount: float
    what: str
    for_whom: List[str] = [] # Empty list means everyone

class Trip(BaseModel):
    id: str
    name: str
    status: str = 'active' # active, settled
    members: List[str] = []
    transactions: List[Transaction] = []

class SettlementTransfer(BaseModel):
    from_member: str
    to_member: str
    amount: float

class SettlementResult(BaseModel):
    transfers: List[SettlementTransfer]
