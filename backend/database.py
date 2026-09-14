"""Mock in-memory database for FairShare."""
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional


class MockDatabase:
    """Simple in-memory mock database."""

    def __init__(self):
        self.groups = {}
        self.people = {}
        self.expenses = {}
        self.group_counter = 1
        self.person_counter = 1
        self.expense_counter = 1

    def create_group(self, trip_name: str) -> int:
        """Create a group, return group_id."""
        group_id = self.group_counter
        self.groups[group_id] = {
            "id": group_id,
            "trip_name": trip_name,
            "created_at": datetime.now(),
        }
        self.group_counter += 1
        return group_id

    def get_group(self, group_id: int) -> Optional[dict]:
        """Get group by ID."""
        return self.groups.get(group_id)

    def add_person(self, group_id: int, name: str) -> int:
        """Add person to group, return person_id."""
        if group_id not in self.groups:
            return None
        person_id = self.person_counter
        self.people[person_id] = {
            "id": person_id,
            "group_id": group_id,
            "name": name,
        }
        self.person_counter += 1
        return person_id

    def get_person(self, person_id: int) -> Optional[dict]:
        """Get person by ID."""
        return self.people.get(person_id)

    def get_group_people(self, group_id: int) -> List[dict]:
        """Get all people in a group."""
        return [p for p in self.people.values() if p["group_id"] == group_id]

    def add_expense(
        self,
        group_id: int,
        who_paid: int,
        amount: Decimal,
        description: str,
        people_involved: List[int],
    ) -> int:
        """Add expense, return expense_id."""
        if group_id not in self.groups:
            return None
        expense_id = self.expense_counter
        self.expenses[expense_id] = {
            "id": expense_id,
            "group_id": group_id,
            "who_paid": who_paid,
            "amount": amount,
            "description": description,
            "people_involved": people_involved,
            "created_at": datetime.now(),
        }
        self.expense_counter += 1
        return expense_id

    def get_expense(self, expense_id: int) -> Optional[dict]:
        """Get expense by ID."""
        return self.expenses.get(expense_id)

    def get_group_expenses(self, group_id: int) -> List[dict]:
        """Get all expenses in a group."""
        return [e for e in self.expenses.values() if e["group_id"] == group_id]


# Global mock database instance
db = MockDatabase()
