from django.shortcuts import render, redirect
# users/views.py
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

# users/views.py (add this to the file)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirect logged-in users to the dashboard
    return render(request, 'home.html')

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # Redirect to login page on successful sign-up
    template_name = 'signup.html'
