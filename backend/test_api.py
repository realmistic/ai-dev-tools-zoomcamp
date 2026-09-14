"""Tests for FairShare API."""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from .main import app
from .database import db, MockDatabase

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test."""
    global db
    from . import database
    database.db = MockDatabase()
    from . import main
    # Force reimport to use new db
    yield


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_group():
    """Test creating a group."""
    response = client.post("/groups", json={"trip_name": "Vegas 2026"})
    assert response.status_code == 201
    data = response.json()
    assert data["trip_name"] == "Vegas 2026"
    assert "id" in data
    assert data["people"] == []
    assert data["expenses"] == []


def test_get_group_not_found():
    """Test getting non-existent group."""
    response = client.get("/groups/999")
    assert response.status_code == 404


def test_add_person_to_group():
    """Test adding a person to a group."""
    # Create group
    group_resp = client.post("/groups", json={"trip_name": "Trip1"})
    group_id = group_resp.json()["id"]

    # Add person
    person_resp = client.post(
        f"/groups/{group_id}/people", json={"name": "Alice"}
    )
    assert person_resp.status_code == 201
    person_data = person_resp.json()
    assert person_data["name"] == "Alice"
    assert person_data["group_id"] == group_id


def test_add_expense_simple():
    """Test adding a simple expense (2 people)."""
    # Create group and add people
    group_resp = client.post("/groups", json={"trip_name": "Trip1"})
    group_id = group_resp.json()["id"]

    alice_resp = client.post(
        f"/groups/{group_id}/people", json={"name": "Alice"}
    )
    alice_id = alice_resp.json()["id"]

    bob_resp = client.post(f"/groups/{group_id}/people", json={"name": "Bob"})
    bob_id = bob_resp.json()["id"]

    # Add expense: Alice pays $100 for 2 people
    expense_resp = client.post(
        f"/groups/{group_id}/expenses",
        json={
            "who_paid": alice_id,
            "amount": 100,
            "description": "Hotel",
            "people_involved": [alice_id, bob_id],
        },
    )
    assert expense_resp.status_code == 201
    expense_data = expense_resp.json()
    assert Decimal(str(expense_data["amount"])) == Decimal("100")


def test_splitwise_balance_simple():
    """Test Splitwise-style balance: Alice pays $100 for 2, should be owed $50."""
    # Setup
    group_resp = client.post("/groups", json={"trip_name": "Trip1"})
    group_id = group_resp.json()["id"]

    alice_resp = client.post(
        f"/groups/{group_id}/people", json={"name": "Alice"}
    )
    alice_id = alice_resp.json()["id"]

    bob_resp = client.post(f"/groups/{group_id}/people", json={"name": "Bob"})
    bob_id = bob_resp.json()["id"]

    # Alice pays $100 for both
    client.post(
        f"/groups/{group_id}/expenses",
        json={
            "who_paid": alice_id,
            "amount": 100,
            "description": "Hotel",
            "people_involved": [alice_id, bob_id],
        },
    )

    # Get group and check balances
    group_resp = client.get(f"/groups/{group_id}")
    balances = group_resp.json()["balances"]
    alice_balance = Decimal(str(balances[str(alice_id)]))
    bob_balance = Decimal(str(balances[str(bob_id)]))

    # Alice paid $100, share is $50, balance = $50
    assert alice_balance == Decimal("50")
    # Bob paid $0, share is $50, balance = -$50
    assert bob_balance == Decimal("-50")


def test_settlement_plan_simple():
    """Test settlement plan: who pays whom."""
    # Setup: Alice $100 for 2, Bob pays nothing
    group_resp = client.post("/groups", json={"trip_name": "Trip1"})
    group_id = group_resp.json()["id"]

    alice_resp = client.post(
        f"/groups/{group_id}/people", json={"name": "Alice"}
    )
    alice_id = alice_resp.json()["id"]

    bob_resp = client.post(f"/groups/{group_id}/people", json={"name": "Bob"})
    bob_id = bob_resp.json()["id"]

    client.post(
        f"/groups/{group_id}/expenses",
        json={
            "who_paid": alice_id,
            "amount": 100,
            "description": "Hotel",
            "people_involved": [alice_id, bob_id],
        },
    )

    # Get settlement
    settlement_resp = client.get(f"/groups/{group_id}/settlement")
    settlements = settlement_resp.json()["settlements"]

    assert len(settlements) == 1
    assert settlements[0]["from_person_id"] == bob_id
    assert settlements[0]["to_person_id"] == alice_id
    assert Decimal(str(settlements[0]["amount"])) == Decimal("50")


def test_person_detail():
    """Test getting person detail with balances."""
    # Setup
    group_resp = client.post("/groups", json={"trip_name": "Trip1"})
    group_id = group_resp.json()["id"]

    alice_resp = client.post(
        f"/groups/{group_id}/people", json={"name": "Alice"}
    )
    alice_id = alice_resp.json()["id"]

    bob_resp = client.post(f"/groups/{group_id}/people", json={"name": "Bob"})
    bob_id = bob_resp.json()["id"]

    # Alice pays $100 for 2
    client.post(
        f"/groups/{group_id}/expenses",
        json={
            "who_paid": alice_id,
            "amount": 100,
            "description": "Hotel",
            "people_involved": [alice_id, bob_id],
        },
    )

    # Get Alice's detail
    alice_detail_resp = client.get(
        f"/groups/{group_id}/people/{alice_id}"
    )
    alice_detail = alice_detail_resp.json()

    assert Decimal(str(alice_detail["total_paid"])) == Decimal("100")
    assert Decimal(str(alice_detail["total_share"])) == Decimal("50")
    assert Decimal(str(alice_detail["balance"])) == Decimal("50")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
