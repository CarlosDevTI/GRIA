from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def indicadores_gerencia(request, agencia_id):
    try:
        datos = gestion_diaria(agencia=agencia_id)
        return JsonResponse(datos, safe=False)
    except Exception as e:
        # Log the error e
        return JsonResponse({'error': str(e)}, status=500)

def gestion_diaria_view(request):
    from apps.comercial.oracle_service import gestion_diaria
    datos = gestion_diaria()
    return render(request, 'gerencia/gestion_diaria.html', {'datos': datos})