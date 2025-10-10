# tracker/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, IncomeForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, QueryDict, HttpResponseBadRequest
from datetime import datetime
from django.db.models import Sum
from .models import Category, Expense, Income, Budget
import plotly.express as px
import pandas as pd

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

@login_required
def analytics_view(request):
    # Get filter parameters from the request, default to current month/year
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    
    # Query the database (this part is unchanged)
    expenses = Expense.objects.filter(
        user=request.user, 
        date__year=year, 
        date__month=month
    )
    
    # Aggregate data for the chart (this part is unchanged)
    category_totals = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    # --- Start of New Plotly Logic ---
    chart_html = ""
    if category_totals:
        # Convert the queryset to a Pandas DataFrame
        df = pd.DataFrame(list(category_totals))
        
        # Rename columns for clarity in the chart
        df.rename(columns={'category__name': 'Category', 'total': 'Amount'}, inplace=True)

        # Create the Plotly Express pie chart
        fig = px.pie(
            df, 
            names='Category', 
            values='Amount',
            title=f'Expenses for {datetime(year, month, 1).strftime("%B %Y")}',
            height=400
        )
        
        # Update layout for better appearance
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            legend_title_text='Categories'
        )
        
        # Convert the figure to HTML
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        # Provide a placeholder message if there's no data
        chart_html = "<div class='text-center p-5'><p>No expense data for this period.</p></div>"
    # --- End of New Plotly Logic ---


    context = {
        'chart_html': chart_html, # Renamed from chart_svg to chart_html
        'year': year,
        'month': month,
        # Generate lists for the filter dropdowns
        'years': range(datetime.now().year - 5, datetime.now().year + 1),
        'months': [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)],
    }
    
    # If this is an HTMX request, only return the chart partial
    if request.htmx:
        return render(request, 'tracker/partials/chart.html', context)
    
    # Otherwise, return the full page
    return render(request, 'tracker/analytics.html', context)

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user)
    form = IncomeForm()
    
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            # On success, return the updated list of incomes
            incomes = Income.objects.filter(user=request.user)
            return render(request, 'tracker/partials/income_list.html', {'incomes': incomes})
    
    # For GET requests, render the full page
    return render(request, 'tracker/income_list.html', {
        'incomes': incomes,
        'form': form
    })


@login_required
def manage_budgets(request):
    # Default to current month and year
    current_year = datetime.now().year
    current_month = datetime.now().month

    if request.method == 'POST':
        try:
            amount = request.POST.get('amount')
            category_id = request.POST.get('category_id')
            
            # Basic validation
            if not amount or not category_id:
                return HttpResponseBadRequest("Missing amount or category.")
            
            amount = float(amount)
            if amount < 0:
                return HttpResponseBadRequest("Amount cannot be negative.")

            category = get_object_or_404(Category, id=category_id, user=request.user)
            
            # Use update_or_create for efficiency. It finds a budget or creates a new one.
            budget, created = Budget.objects.update_or_create(
                user=request.user,
                category=category,
                year=current_year,
                month=current_month,
                defaults={'amount': amount}
            )
            # Return a partial that shows a success message
            return render(request, 'tracker/partials/budget_success_indicator.html')

        except (ValueError, Category.DoesNotExist):
            return HttpResponseBadRequest("Invalid data provided.")

    # For a GET request, prepare the data for the main page
    categories = Category.objects.filter(user=request.user)
    budgets = Budget.objects.filter(user=request.user, year=current_year, month=current_month)
    
    # Create a dictionary for easy lookup in the template
    budget_map = {budget.category.id: budget.amount for budget in budgets}
    
    context = {
        'categories': categories,
        'budget_map': budget_map,
        'current_month_name': datetime(current_year, current_month, 1).strftime('%B %Y')
    }
    return render(request, 'tracker/manage_budgets.html', context)