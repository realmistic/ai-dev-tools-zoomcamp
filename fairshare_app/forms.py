from django import forms
from .models import Group, Person, Expense, ExpenseParticipant


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['trip_name']
        widgets = {
            'trip_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trip name (e.g., Vegas 2026)'}),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Person name'}),
        }


class ExpenseForm(forms.ModelForm):
    people_involved = forms.ModelMultipleChoiceField(
        queryset=Person.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Who was involved?"
    )

    class Meta:
        model = Expense
        fields = ['who_paid', 'amount', 'description']
        widgets = {
            'who_paid': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount ($)', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description (e.g., Hotel)'}),
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['who_paid'].queryset = group.people.all()
            self.fields['people_involved'].queryset = group.people.all()
