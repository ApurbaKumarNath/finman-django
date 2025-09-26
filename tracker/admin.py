# tracker/admin.py
from django.contrib import admin
from .models import Category, Expense

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
