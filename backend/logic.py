from typing import List, Dict
from models import Transaction, SettlementTransfer

def calculate_settlement(transactions: List[Transaction], members: List[str]) -> List[SettlementTransfer]:
    # 1. Calculate Net Balance
    balances: Dict[str, float] = {m: 0.0 for m in members}
    
    for t in transactions:
        payer = t.payer
        amount = t.amount
        beneficiaries = t.for_whom if t.for_whom else members
        
        if not beneficiaries:
            continue
            
        split_amount = amount / len(beneficiaries)
        
        # Payer pays full amount (credit)
        # But wait, payer is also a beneficiary usually?
        # Standard logic: Payer +amount, Beneficiaries -split_amount
        # If payer is in beneficiaries, they get +amount - split_amount
        
        balances[payer] += amount
        for b in beneficiaries:
            balances[b] -= split_amount
            
    # 2. Greedy Algorithm
    # Separate into debtors (-) and creditors (+)
    debtors = []
    creditors = []
    
    for m, bal in balances.items():
        # Round to 2 decimal places to avoid float issues
        bal = round(bal, 2)
        if bal < -0.01:
            debtors.append({'name': m, 'amount': bal})
        elif bal > 0.01:
            creditors.append({'name': m, 'amount': bal})
            
    # Sort by magnitude (largest first)
    debtors.sort(key=lambda x: x['amount']) # Ascending (most negative first)
    creditors.sort(key=lambda x: x['amount'], reverse=True) # Descending (most positive first)
    
    transfers = []
    
    i = 0 # debtor index
    j = 0 # creditor index
    
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        debt_amount = abs(debtor['amount'])
        credit_amount = creditor['amount']
        
        settle_amount = min(debt_amount, credit_amount)
        
        transfers.append(SettlementTransfer(
            from_member=debtor['name'],
            to_member=creditor['name'],
            amount=round(settle_amount, 2)
        ))
        
        # Update remaining amounts
        debtor['amount'] += settle_amount
        creditor['amount'] -= settle_amount
        
        # Move indices if settled
        if abs(debtor['amount']) < 0.01:
            i += 1
        if abs(creditor['amount']) < 0.01:
            j += 1
            
    return transfers
