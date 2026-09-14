"""FastAPI backend for FairShare."""
from decimal import Decimal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .models import (
    GroupBase,
    GroupDetail,
    PersonBase,
    Person,
    PersonDetail,
    ExpenseBase,
    Expense,
    Settlement,
)
from .database import db
from .services import calculate_balances, calculate_settlement

app = FastAPI(
    title="FairShare API",
    description="Split expenses fairly among friends",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}


@app.post("/groups", response_model=GroupDetail, status_code=201)
async def create_group(group: GroupBase):
    """Create a new group."""
    group_id = db.create_group(group.trip_name)
    return get_group_detail(group_id)


@app.get("/groups/{group_id}", response_model=GroupDetail)
async def get_group(group_id: int):
    """Get group details."""
    return get_group_detail(group_id)


def get_group_detail(group_id: int) -> GroupDetail:
    """Helper to construct group detail response."""
    group = db.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    people = db.get_group_people(group_id)
    expenses = db.get_group_expenses(group_id)
    balances = calculate_balances(group_id)
    settlement = calculate_settlement(group_id)

    # Convert balances dict values to Decimal for JSON serialization
    balances_dict = {str(k): v for k, v in balances.items()}

    return GroupDetail(
        id=group["id"],
        trip_name=group["trip_name"],
        people=[
            Person(id=p["id"], name=p["name"], group_id=p["group_id"]) for p in people
        ],
        expenses=[
            Expense(
                id=e["id"],
                group_id=e["group_id"],
                who_paid=e["who_paid"],
                amount=Decimal(str(e["amount"])),
                description=e["description"],
                people_involved=e["people_involved"],
                created_at=e["created_at"],
            )
            for e in expenses
        ],
        balances=balances_dict,
        settlement=[
            Settlement(
                from_person_id=s["from_person_id"],
                to_person_id=s["to_person_id"],
                from_person_name=s["from_person_name"],
                to_person_name=s["to_person_name"],
                amount=Decimal(str(s["amount"])),
            )
            for s in settlement
        ],
        created_at=group["created_at"],
    )


@app.post("/groups/{group_id}/people", response_model=Person, status_code=201)
async def add_person(group_id: int, person: PersonBase):
    """Add a person to a group."""
    group = db.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    person_id = db.add_person(group_id, person.name)
    person_data = db.get_person(person_id)
    return Person(
        id=person_data["id"],
        name=person_data["name"],
        group_id=person_data["group_id"],
    )


@app.get("/groups/{group_id}/people/{person_id}", response_model=PersonDetail)
async def get_person(group_id: int, person_id: int):
    """Get person details and balance."""
    group = db.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    person = db.get_person(person_id)
    if not person or person["group_id"] != group_id:
        raise HTTPException(status_code=404, detail="Person not found")

    expenses = db.get_group_expenses(group_id)

    # Total paid
    total_paid = sum(
        Decimal(str(e["amount"]))
        for e in expenses
        if e["who_paid"] == person_id
    ) or Decimal("0.00")

    # Total share (their share of expenses they participated in)
    total_share = Decimal("0.00")
    for expense in expenses:
        if person_id in expense["people_involved"]:
            num_participants = len(expense["people_involved"])
            if num_participants > 0:
                share_of_expense = Decimal(str(expense["amount"])) / num_participants
                total_share += share_of_expense

    balance = total_paid - total_share

    # Expenses they paid
    paid_expenses = [
        Expense(
            id=e["id"],
            group_id=e["group_id"],
            who_paid=e["who_paid"],
            amount=Decimal(str(e["amount"])),
            description=e["description"],
            people_involved=e["people_involved"],
            created_at=e["created_at"],
        )
        for e in expenses
        if e["who_paid"] == person_id
    ]

    # Expenses they participated in
    participated_expenses = [
        Expense(
            id=e["id"],
            group_id=e["group_id"],
            who_paid=e["who_paid"],
            amount=Decimal(str(e["amount"])),
            description=e["description"],
            people_involved=e["people_involved"],
            created_at=e["created_at"],
        )
        for e in expenses
        if person_id in e["people_involved"]
    ]

    return PersonDetail(
        id=person["id"],
        name=person["name"],
        group_id=person["group_id"],
        total_paid=total_paid,
        total_share=total_share,
        balance=balance,
        paid_expenses=paid_expenses,
        participated_expenses=participated_expenses,
    )


@app.post("/groups/{group_id}/expenses", response_model=Expense, status_code=201)
async def add_expense(group_id: int, expense: ExpenseBase):
    """Add an expense to a group."""
    group = db.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Validate that who_paid and people_involved are in this group
    for person_id in [expense.who_paid] + expense.people_involved:
        person = db.get_person(person_id)
        if not person or person["group_id"] != group_id:
            raise HTTPException(
                status_code=400, detail=f"Person {person_id} not in this group"
            )

    expense_id = db.add_expense(
        group_id,
        expense.who_paid,
        expense.amount,
        expense.description,
        expense.people_involved,
    )
    expense_data = db.get_expense(expense_id)

    return Expense(
        id=expense_data["id"],
        group_id=expense_data["group_id"],
        who_paid=expense_data["who_paid"],
        amount=Decimal(str(expense_data["amount"])),
        description=expense_data["description"],
        people_involved=expense_data["people_involved"],
        created_at=expense_data["created_at"],
    )


@app.get("/groups/{group_id}/settlement")
async def get_settlement(group_id: int):
    """Get the settlement plan for a group."""
    group = db.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    settlement = calculate_settlement(group_id)
    return {
        "settlements": [
            Settlement(
                from_person_id=s["from_person_id"],
                to_person_id=s["to_person_id"],
                from_person_name=s["from_person_name"],
                to_person_name=s["to_person_name"],
                amount=Decimal(str(s["amount"])),
            )
            for s in settlement
        ]
    }
