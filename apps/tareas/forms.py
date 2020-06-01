from django import forms

# Modelos
from apps.tareas.models import Tarea,AsignarTarea

class AsignarTareaForm(forms.ModelForm):
    class Meta:
        model = AsignarTarea

        fields = [
            'tarea',
            'usuario',
        ]
        
        labels = {
            'tarea' : 'Tarea',
            'usuario' : 'Usuario',
        }

        widgets = {
            'tarea' : forms.Select(attrs={'class':'form-control'}),
            'usuario' : forms.Select(attrs={'class':'form-control'}),
        }

class TareaForm(forms.ModelForm):

    class Meta:
        model = Tarea

        fields =[
            'nombre',
            'complejidad',
            'duracion',
            'lugar',
            'comentarios'
        ]
    
        labels =  {
            'nombre' : 'Nombre',
            'complejidad' : 'Complejidad',
            'duracion' : 'Duración en horas',
            'lugar' : 'Dependencia',
            'comentarios' : 'Comentarios',
        }

        widgets = {
            'nombre':forms.TextInput(attrs={'class':'form-control'}),
            'complejidad':forms.NumberInput(attrs={'class':'custom-range','type':'range','max':5,'min':1,'step':1,'list':'tickmarks'}),
            'duracion':forms.TextInput(attrs={'class':'form-control'}),
            'lugar':forms.TextInput(attrs={'class':'form-control'}),
            'comentarios':forms.TextInput(attrs={'class':'form-control'}),
        }
