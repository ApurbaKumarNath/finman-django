# tracker/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, QueryDict
from .models import Category

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user) 
    form = ExpenseForm(user=request.user) # Pass the user to the form
    return render(request, 'tracker/dashboard.html', {
        'expenses': expenses,
        'form': form
    })

@login_required
def add_expense(request):
    # This part handles the form submission when the user clicks "Add Expense"
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            # Return just the HTML for the new row
            return render(request, 'tracker/partials/expense_row.html', {'expense': expense})
    
    # This part will handle form errors, re-rendering the form with error messages
    # The HTMX swap will replace the old form with this new one
    form = ExpenseForm(request.POST, user=request.user)
    return render(request, 'tracker/partials/expense_form.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'DELETE':
        expense.delete()
    return HttpResponse('') # Return an empty response

# tracker/views.py

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'GET':
        # ENSURE THIS PART PASSES THE 'categories' CONTEXT
        categories = Category.objects.filter(user=request.user)
        return render(request, 'tracker/partials/expense_edit_form.html', {
            'expense': expense,
            'categories': categories, # This is needed for the <select> dropdown
        })
    
    elif request.method == 'PUT':
        # The PUT logic we wrote before is actually correct and can stay.
        data = QueryDict(request.body)
        form = ExpenseForm(data, instance=expense, user=request.user)
        
        if form.is_valid():
            form.save()
            return render(request, 'tracker/partials/expense_row.html', {'expense': expense})
        else:
            print("Form errors:", form.errors)
            # You can decide how to handle errors here, for now, we'll assume valid data
            # To be more robust, you could re-render the form with errors.
            categories = Category.objects.filter(user=request.user)
            return render(request, 'tracker/partials/expense_edit_form.html', {
                'expense': expense,
                'categories': categories,
            })

@login_required
def get_expense_row(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'tracker/partials/expense_row.html', {'expense': expense})