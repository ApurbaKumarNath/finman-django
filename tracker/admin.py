# tracker/admin.py
from django.contrib import admin
from .models import Category, Expense, Income, Budget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name',)
    list_filter = ('user',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'category', 'amount', 'description')
    search_fields = ('description', 'category__name')
    list_filter = ('user', 'category', 'date')
    list_per_page = 20 # Add pagination

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'source', 'amount')
    list_filter = ('user', 'date')
    search_fields = ('source', 'description')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'month', 'year')