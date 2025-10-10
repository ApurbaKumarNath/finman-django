# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# users/views.py (add this to the file)

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirect logged-in users to the dashboard
    return render(request, 'home.html')

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # Redirect to login page on successful sign-up
    template_name = 'signup.html'

@login_required
def profile_view(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile = request.user.profile # Get or create profile
        profile.picture = request.FILES['profile_picture']
        profile.save()
        return redirect('profile')

    return render(request, 'profile.html')