from django import template

register = template.Library()

@register.filter
def to_numeric(value):
    """Convierte un valor a float. Si falla, devuelve 0."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0
