# tracker/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    form = ExpenseForm(user=request.user) # Pass the user to the form
    return render(request, 'tracker/dashboard.html', {
        'expenses': expenses,
        'form': form
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
    
    # Whether the form was valid or not, we return the updated list
    expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    return render(request, 'tracker/partials/expense_list.html', {'expenses': expenses})