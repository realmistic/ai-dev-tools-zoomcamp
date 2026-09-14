from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Group, Person, Expense, ExpenseParticipant
from .forms import GroupForm, PersonForm, ExpenseForm
from .services import calculate_balances, calculate_settlement


def index(request):
    """Home page with list of groups."""
    groups = Group.objects.all().order_by('-created_at')
    return render(request, 'fairshare_app/index.html', {'groups': groups})


def create_group(request):
    """Create a new group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Trip "{group.trip_name}" created!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm()
    return render(request, 'fairshare_app/create_group.html', {'form': form})


def group_detail(request, group_id):
    """View group details, balances, and settlement."""
    group = get_object_or_404(Group, id=group_id)
    people = group.people.all()
    expenses = group.expenses.all()
    
    balances = calculate_balances(group)
    settlement = calculate_settlement(group)
    
    # Get person names for settlement display
    settlement_with_names = []
    for s in settlement:
        debtor = get_object_or_404(Person, id=s['from'])
        creditor = get_object_or_404(Person, id=s['to'])
        settlement_with_names.append({
            'from_name': debtor.name,
            'to_name': creditor.name,
            'amount': s['amount'],
        })
    
    context = {
        'group': group,
        'people': people,
        'expenses': expenses,
        'balances': balances,
        'settlement': settlement_with_names,
    }
    return render(request, 'fairshare_app/group_detail.html', context)


def add_person(request, group_id):
    """Add a person to a group."""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.group = group
            person.save()
            messages.success(request, f'Added {person.name} to the group!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = PersonForm()
    
    return render(request, 'fairshare_app/add_person.html', {
        'form': form,
        'group': group,
    })


def add_expense(request, group_id):
    """Add an expense to a group."""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.save()
            
            # Add participants
            people_involved = form.cleaned_data.get('people_involved')
            for person in people_involved:
                ExpenseParticipant.objects.create(expense=expense, person=person)
            
            messages.success(request, f'Added expense: {expense.description}')
            return redirect('group_detail', group_id=group.id)
    else:
        form = ExpenseForm(group=group)
    
    return render(request, 'fairshare_app/add_expense.html', {
        'form': form,
        'group': group,
    })
