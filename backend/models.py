"""Pydantic models for FairShare API."""
from decimal import Decimal
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    name: str


class Person(PersonBase):
    id: int
    group_id: int


class ExpenseBase(BaseModel):
    who_paid: int
    amount: Decimal = Field(..., decimal_places=2)
    description: str = ""
    people_involved: List[int]  # IDs for input


class Expense(BaseModel):
    id: int
    group_id: int
    who_paid: int
    amount: Decimal = Field(..., decimal_places=2)
    description: str = ""
    people_involved: List["Person"]  # Person objects for output
    created_at: datetime


class Settlement(BaseModel):
    from_person_id: int
    to_person_id: int
    from_person_name: str
    to_person_name: str
    amount: Decimal = Field(..., decimal_places=2)


class PersonDetail(BaseModel):
    id: int
    name: str
    group_id: int
    total_paid: Decimal = Field(..., decimal_places=2)
    total_share: Decimal = Field(..., decimal_places=2)
    balance: Decimal = Field(..., decimal_places=2)
    paid_expenses: List[Expense]
    participated_expenses: List[Expense]


class GroupBase(BaseModel):
    trip_name: str


class GroupDetail(GroupBase):
    id: int
    people: List[Person]
    expenses: List[Expense]
    balances: dict  # {person_id: balance}
    settlement: List[Settlement]
    created_at: datetime
