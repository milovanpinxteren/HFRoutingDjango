from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def show_checks_page(request):
    return render(request, 'checks_page.html')

