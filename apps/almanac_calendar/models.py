from django.db import models
from django.utils import timezone
from apps.hogar.models import Domicilio,Usuario,Dependencia
from apps.tareas.models import Tarea, AsignarTarea

# Create your models here.
class Event(models.Model):
    #event, Holiday, Exam
    #description
    #heading
    #datetime
    usuario = models.ForeignKey(Usuario, default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Title')
    #type = models.CharField(blank=True, null=True, max_length=10, default='EV')
    #description = models.CharField(max_length=50, null=True, blank=True, default='')
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)
    #all_day = models.BooleanField(default=False)

    def __str__(self):
        return self.title
