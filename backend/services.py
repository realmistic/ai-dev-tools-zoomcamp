"""Business logic: balance and settlement calculations."""
from decimal import Decimal
from typing import Dict, List, Tuple
from .database import db


def calculate_balances(group_id: int) -> Dict[int, Decimal]:
    """
    Calculate per-person balance (Splitwise-style):
    balance = total_paid - total_share
    """
    people = db.get_group_people(group_id)
    expenses = db.get_group_expenses(group_id)

    balances = {}
    for person in people:
        # Total paid by this person
        total_paid = sum(
            Decimal(str(e["amount"]))
            for e in expenses
            if e["who_paid"] == person["id"]
        ) or Decimal("0.00")

        # Total share: sum of (expense / num_participants) for expenses they participated in
        total_share = Decimal("0.00")
        for expense in expenses:
            if person["id"] in expense["people_involved"]:
                num_participants = len(expense["people_involved"])
                if num_participants > 0:
                    share_of_expense = Decimal(str(expense["amount"])) / num_participants
                    total_share += share_of_expense

        balance = total_paid - total_share
        balances[person["id"]] = balance

    return balances


def calculate_settlement(group_id: int) -> List[Dict]:
    """
    Calculate minimal settlement plan (greedy algorithm).
    Returns list of {from_person_id, to_person_id, from_person_name, to_person_name, amount}
    """
    balances = calculate_balances(group_id)
    people = {p["id"]: p for p in db.get_group_people(group_id)}

    # Separate creditors (owed money) and debtors (owe money)
    creditors = [(pid, bal) for pid, bal in balances.items() if bal > Decimal("0.01")]
    debtors = [(pid, bal) for pid, bal in balances.items() if bal < Decimal("-0.01")]

    # Sort by balance (descending for creditors, ascending for debtors)
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1])

    settlements = []
    creditors_idx = 0
    debtors_idx = 0

    while creditors_idx < len(creditors) and debtors_idx < len(debtors):
        creditor_id, creditor_balance = creditors[creditors_idx]
        debtor_id, debtor_balance = debtors[debtors_idx]

        # Amount to transfer
        amount = min(creditor_balance, -debtor_balance)

        settlements.append(
            {
                "from_person_id": debtor_id,
                "to_person_id": creditor_id,
                "from_person_name": people[debtor_id]["name"],
                "to_person_name": people[creditor_id]["name"],
                "amount": amount.quantize(Decimal("0.01")),  # Round to 2 decimal places
            }
        )

        # Update balances
        new_creditor_bal = creditor_balance - amount
        new_debtor_bal = debtor_balance + amount
        creditors[creditors_idx] = (creditor_id, new_creditor_bal)
        debtors[debtors_idx] = (debtor_id, new_debtor_bal)

        # Move to next if current is settled (within tolerance)
        if abs(new_creditor_bal) < Decimal("0.01"):
            creditors_idx += 1
        if abs(new_debtor_bal) < Decimal("0.01"):
            debtors_idx += 1

    return settlements
