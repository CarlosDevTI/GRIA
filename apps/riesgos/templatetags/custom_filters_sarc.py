from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(dictionary, key):
    """
    Permite acceder a un valor de diccionario usando una variable como clave en las plantillas de Django.
    Uso: {{ mi_diccionario|lookup:mi_variable_de_clave }}
    """
    return dictionary.get(key)