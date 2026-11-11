import re

from django import forms

from .models import Categoria, Herramienta


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['codigo', 'nombre', 'categoria', 'estado', 'disponible', 'fecha_ingreso']
        widgets = {'fecha_ingreso': forms.DateInput(attrs={'type': 'date'})}

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo']
        if not re.fullmatch(r'HER-\d{3}', codigo):
            raise forms.ValidationError('El código debe tener el formato HER-000.')
        return codigo
