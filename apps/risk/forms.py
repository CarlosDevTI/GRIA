from django import forms

class UploadFileForm(forms.Form):
    """
    Un formulario simple para manejar la carga de un archivo.
    """
    file = forms.FileField(
        label="Seleccione el archivo (CSV o Excel)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
