from django import forms
from datetime import date

class ApreForm(forms.Form):
    """
    Formulario para capturar los filtros del reporte APRE
    """
    APRE_CHOICES = [
        ('', 'Escoja una opción'),
        ('apre_compensados', 'APRE CON COMPENSADOS'),
        ('apre_sincompensados', 'APRE SIN COMPENSADOS'),
        ('apre_basico', 'APRE BÁSICO PLENO'),
        ('apre_diferencia', 'APRE SÓLO MES ANTERIOR Y ACTUAL'),
    ]

    PERIODICIDAD_CHOICES = [
        ('mensual', 'Mensual'),
        ('diario', 'Diario')
    ]
    
    tipo_apre = forms.ChoiceField(
        choices=APRE_CHOICES,
        label="Tipo de APRE",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    periodicidad = forms.ChoiceField(
        choices=PERIODICIDAD_CHOICES,
        widget=forms.RadioSelect,
        label="Periodicidad",
        initial='mensual'
    )
    
    fecha = forms.DateField(
        label="Fecha",
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        help_text="Ingrese la fecha para generar el reporte."
    )

    def clean(self):
        cleaned_data = super().clean()
        periodicidad = cleaned_data.get('periodicidad')
        fecha = cleaned_data.get('fecha')

        if periodicidad == 'mensual' and not fecha:
            self.add_error('fecha', 'Para la periodicidad mensual, la fecha es requerida.')
        
        if fecha and fecha > date.today():
            self.add_error('fecha', "La fecha no puede ser en el futuro.")

        return cleaned_data
    
    def clean_tipo_apre(self):
        tipo_apre = self.cleaned_data['tipo_apre']
        if not tipo_apre:
            raise forms.ValidationError("Debe seleccionar un tipo de APRE")
        return tipo_apre