from django.shortcuts import render

# Create your views here.
def gria_view(request):
    """
    Vista para el proyecto general, este es el Principal.
    """
    
    return render(request, 'gria/gria_dashboard.html')