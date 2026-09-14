from django import forms


class GroupForm(forms.Form):
    trip_name = forms.CharField(
        label='Trip Name',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Trip name (e.g., Vegas 2026)'
        })
    )


class PersonForm(forms.Form):
    name = forms.CharField(
        label='Person Name',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Person name'
        })
    )


class ExpenseForm(forms.Form):
    who_paid = forms.ChoiceField(
        label='Who Paid?',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        label='Amount ($)',
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Amount',
            'step': '0.01'
        })
    )
    description = forms.CharField(
        label='Description',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Description (e.g., Hotel)'
        })
    )
    people_involved = forms.MultipleChoiceField(
        label='Who Was Involved?',
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, people=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if people:
            choices = [(str(p['id']), p['name']) for p in people]
            self.fields['who_paid'].choices = choices
            self.fields['people_involved'].choices = choices
