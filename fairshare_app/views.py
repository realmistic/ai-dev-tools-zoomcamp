"""Views for FairShare - call FastAPI backend API."""
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from .api_client import api_client
from .forms import GroupForm, PersonForm, ExpenseForm


def index(request):
    """Home page - list all groups."""
    # In a real app, we'd need to persist which groups exist
    # For now, just show a welcome page
    return render(request, 'fairshare_app/index.html', {})


def create_group(request):
    """Create a new group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            try:
                group_data = api_client.create_group(form.cleaned_data['trip_name'])
                messages.success(request, f'Trip "{form.cleaned_data["trip_name"]}" created!')
                return redirect('group_detail', group_id=group_data['id'])
            except Exception as e:
                messages.error(request, f'Error creating trip: {str(e)}')
    else:
        form = GroupForm()

    return render(request, 'fairshare_app/create_group.html', {'form': form})


def group_detail(request, group_id):
    """View group details, expenses, balances, and settlement."""
    try:
        group = api_client.get_group(group_id)
        
        # Convert balances keys to integers for template access
        balances = {int(k): Decimal(v) for k, v in group.get('balances', {}).items()}
        
        # Convert settlement amounts to Decimal
        settlement = [
            {
                **s,
                'amount': Decimal(str(s['amount']))
            }
            for s in group.get('settlement', [])
        ]
        
        context = {
            'group': group,
            'people': group.get('people', []),
            'expenses': group.get('expenses', []),
            'balances': balances,
            'settlement': settlement,
        }
        return render(request, 'fairshare_app/group_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error loading group: {str(e)}')
        return redirect('index')


def add_person(request, group_id):
    """Add a person to a group."""
    try:
        group = api_client.get_group(group_id)
    except Exception as e:
        messages.error(request, f'Group not found: {str(e)}')
        return redirect('index')

    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            try:
                api_client.add_person(group_id, form.cleaned_data['name'])
                messages.success(request, f'Added {form.cleaned_data["name"]} to the group!')
                return redirect('group_detail', group_id=group_id)
            except Exception as e:
                messages.error(request, f'Error adding person: {str(e)}')
    else:
        form = PersonForm()

    return render(request, 'fairshare_app/add_person.html', {'group': group, 'form': form})


def add_expense(request, group_id):
    """Add an expense to a group."""
    try:
        group = api_client.get_group(group_id)
    except Exception as e:
        messages.error(request, f'Group not found: {str(e)}')
        return redirect('index')

    if request.method == 'POST':
        form = ExpenseForm(request.POST, people=group['people'])
        if form.is_valid():
            try:
                api_client.add_expense(
                    group_id,
                    int(form.cleaned_data['who_paid']),
                    form.cleaned_data['amount'],
                    form.cleaned_data['description'],
                    [int(pid) for pid in form.cleaned_data['people_involved']]
                )
                messages.success(request, f'Added expense: {form.cleaned_data["description"]}')
                return redirect('group_detail', group_id=group_id)
            except Exception as e:
                messages.error(request, f'Error adding expense: {str(e)}')
    else:
        form = ExpenseForm(people=group['people'])

    return render(request, 'fairshare_app/add_expense.html', {'group': group, 'form': form})


def person_detail(request, group_id, person_id):
    """View person's expenses and balance."""
    try:
        group = api_client.get_group(group_id)
        person_data = api_client.get_person(group_id, person_id)
        
        context = {
            'group': group,
            'person': person_data,
            'total_paid': Decimal(str(person_data.get('total_paid', 0))),
            'total_share': Decimal(str(person_data.get('total_share', 0))),
            'balance': Decimal(str(person_data.get('balance', 0))),
            'paid_expenses': person_data.get('paid_expenses', []),
            'participated_expenses': person_data.get('participated_expenses', []),
        }
        return render(request, 'fairshare_app/person_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error loading person: {str(e)}')
        return redirect('index')
