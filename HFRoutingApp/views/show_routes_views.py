from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def show_routes_page(request):
    return render(request, 'routes/routes.html')
