# tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('edit_expense/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete_expense/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('get_expense_row/<int:pk>/', views.get_expense_row, name='get_expense_row'),
]