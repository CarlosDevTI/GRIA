from django import template

register = template.Library()

@register.filter(name='smart_format')
def smart_format(valor):
    """
    Filtro inteligente para formatear un valor según su tipo:
    - Si es un número entero (ej: 1, 10, 0), lo muestra como número.
    - Si es un número con decimales (ej: 0.3, 81.06), lo formatea como porcentaje con 2 decimales.
    - Si es texto, lo deja como está.
    """
    if valor is None or valor == '-':
        return '-'
    
    # Reemplazar coma por punto para la conversión a float
    valor_str = str(valor).strip().replace(',', '.')

    try:
        numero = float(valor_str)
        
        # Verificar si el número es un entero (ej: 5.0 -> True)
        if numero == int(numero):
            # Es un entero, devolverlo como número sin decimales.
            return str(int(numero))
        else:
            # Es un float, formatearlo como porcentaje.
            # Usamos f-string para asegurar 2 decimales y reemplazamos el punto por la coma.
            formateado = f"{numero:.2f}".replace('.', ',')
            return f"{formateado}%"
            
    except (ValueError, TypeError):
        # No se pudo convertir a número, es texto o ya tiene formato (ej. "N/A", "75%").
        return str(valor) # Devolver el valor original sin cambios
