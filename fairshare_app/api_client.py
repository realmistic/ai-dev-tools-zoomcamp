"""HTTP client to call FastAPI backend."""
import httpx
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8001"

class APIClient:
    """Client for communicating with FairShare FastAPI backend."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=10.0)

    def create_group(self, trip_name: str) -> Dict:
        """Create a new group."""
        response = self.client.post("/groups", json={"trip_name": trip_name})
        response.raise_for_status()
        return response.json()

    def get_group(self, group_id: int) -> Dict:
        """Get group details with people, expenses, balances, settlement."""
        response = self.client.get(f"/groups/{group_id}")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"DEBUG: API Error {response.status_code}: {response.text}")
            raise
        return response.json()

    def add_person(self, group_id: int, name: str) -> Dict:
        """Add a person to a group."""
        response = self.client.post(
            f"/groups/{group_id}/people", json={"name": name}
        )
        response.raise_for_status()
        return response.json()

    def get_person(self, group_id: int, person_id: int) -> Dict:
        """Get person details with balance."""
        response = self.client.get(f"/groups/{group_id}/people/{person_id}")
        response.raise_for_status()
        return response.json()

    def add_expense(
        self,
        group_id: int,
        who_paid: int,
        amount: Decimal,
        description: str,
        people_involved: List[int],
    ) -> Dict:
        """Add an expense to a group."""
        response = self.client.post(
            f"/groups/{group_id}/expenses",
            json={
                "who_paid": who_paid,
                "amount": float(amount),
                "description": description,
                "people_involved": people_involved,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_settlement(self, group_id: int) -> Dict:
        """Get the settlement plan for a group."""
        response = self.client.get(f"/groups/{group_id}/settlement")
        response.raise_for_status()
        return response.json()


# Global API client instance
api_client = APIClient()
