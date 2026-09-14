"""Settlement logic and balance calculations."""
from decimal import Decimal
from typing import Dict, List, Tuple


def calculate_balances(group) -> Dict[int, Decimal]:
    """
    Calculate per-person balance: paid - share.
    
    Share = total expenses / number of people (equally divided).
    Balance = what they paid - what they owe.
    
    Returns dict: {person_id: balance}
    """
    people = group.people.all()
    if not people.exists():
        return {}
    
    total_expenses = sum(
        expense.amount for expense in group.expenses.all()
    )
    
    num_people = people.count()
    share_per_person = total_expenses / num_people if num_people > 0 else Decimal(0)
    
    balances = {}
    for person in people:
        paid = sum(
            expense.amount for expense in person.paid_expenses.filter(group=group)
        )
        balance = paid - share_per_person
        balances[person.id] = balance
    
    return balances


def calculate_settlement(group) -> List[Dict]:
    """
    Calculate minimal settlement plan: who pays whom.
    
    Greedy algorithm: highest creditor (positive balance) receives from
    highest debtor (negative balance) first.
    
    Returns list of dicts: [{"from": person_id, "to": person_id, "amount": decimal}, ...]
    """
    balances = calculate_balances(group)
    
    # Separate creditors and debtors
    creditors = [(pid, bal) for pid, bal in balances.items() if bal > Decimal("0.01")]
    debtors = [(pid, bal) for pid, bal in balances.items() if bal < Decimal("-0.01")]
    
    # Sort by absolute balance (descending)
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1])  # ascending (most negative first)
    
    settlements = []
    creditors_idx = 0
    debtors_idx = 0
    
    while creditors_idx < len(creditors) and debtors_idx < len(debtors):
        creditor_id, creditor_balance = creditors[creditors_idx]
        debtor_id, debtor_balance = debtors[debtors_idx]
        
        # Amount to transfer: min of creditor's claim and debtor's debt
        amount = min(creditor_balance, -debtor_balance)
        
        settlements.append({
            "from": debtor_id,
            "to": creditor_id,
            "amount": amount,
        })
        
        # Update balances
        creditors[creditors_idx] = (creditor_id, creditor_balance - amount)
        debtors[debtors_idx] = (debtor_id, debtor_balance + amount)
        
        # Move to next if current is settled
        if creditors[creditors_idx][1] < Decimal("0.01"):
            creditors_idx += 1
        if debtors[debtors_idx][1] > Decimal("-0.01"):
            debtors_idx += 1
    
    return settlements
