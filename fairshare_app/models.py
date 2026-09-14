from decimal import Decimal
from django.db import models


class Group(models.Model):
    """A group trip or shared expense group."""
    trip_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trip_name


class Person(models.Model):
    """A person in a group."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="people")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.name


class Expense(models.Model):
    """A shared expense."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    who_paid = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="paid_expenses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.who_paid.name} paid {self.amount} for {self.description}"


class ExpenseParticipant(models.Model):
    """Who is involved in an expense."""
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="participants")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="expense_participations")

    class Meta:
        unique_together = ("expense", "person")

    def __str__(self):
        return f"{self.person.name} in {self.expense.description}"
