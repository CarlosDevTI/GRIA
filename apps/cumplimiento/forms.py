from django import forms
from .models import Indicador, RegistroIndicador, Formula

class IndicadorForm(forms.ModelForm):
    class Meta:
        model = Indicador
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre del Indicador',
        }

class FormulaForm(forms.ModelForm):
    """Formulario para agregar o editar fórmulas de un indicador."""
    class Meta:
        model = Formula
        fields = ['descripcion', 'meta', 'frecuencia_medicion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia_medicion': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'descripcion': 'Descripción de la Fórmula',
            'meta': 'Meta',
            'frecuencia_medicion': 'Frecuencia de Medición',
        }

class RegistroIndicadorForm(forms.ModelForm):
    class Meta:
        model = RegistroIndicador
        fields = ['mes', 'año', 'valor']
        widgets = {
            'mes': forms.Select(choices=RegistroIndicador.MESES, attrs={'class': 'form-control'}),
            'año': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2030}),
            'valor': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'mes': 'Mes',
            'año': 'Año',
            'valor': 'Valor',
        }