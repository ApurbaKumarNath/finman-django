# tracker/forms.py
from django import forms
from .models import Expense, Category

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'amount', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Get the user from the view
        super().__init__(*args, **kwargs)
        if user:
            # Filter categories to show only the ones owned by the logged-in user
            self.fields['category'].queryset = Category.objects.filter(user=user)