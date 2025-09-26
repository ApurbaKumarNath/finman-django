# tracker/models.py
from django.db import models
from django.contrib.auth.models import User # Import the built-in User model

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    
    class Meta:
        # This ensures a user cannot have two categories with the same name
        unique_together = ('user', 'name')
        verbose_name_plural = "Categories" # Corrects the pluralization in the admin panel

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True) # Optional field
    date = models.DateField()

    class Meta:
        # Order expenses by date by default, newest first
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} - {self.description[:20]} - {self.amount}'