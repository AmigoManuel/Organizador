from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView

# Modelos
from apps.hogar.models import Usuario, PerteneceDependencia, Dependencia, Domicilio
from apps.tareas.models import AsignarTarea as AsignarTarea_model
from apps.tareas.models import Tarea
from apps.almanac_calendar.models import Event
# Formularios
from apps.tareas.forms import TareaForm, AsignarTareaForm


class CrearTarea(CreateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'tareas/tarea_form.html'
    success_url = reverse_lazy('tareas:crear_tarea')

    def get_context_data(self, **kwargs):
        context = super(CrearTarea, self).get_context_data(**kwargs)
        self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
        self.pertenece_dependencia = PerteneceDependencia.objects.filter(domicilio=self.usuario.domicilio,
                                                                         asignada=True)
        self.dependencia = Dependencia.objects.filter(pk__in=self.pertenece_dependencia)
        context['form'].fields['dependencia'].queryset = self.dependencia
        context['name'] = "Añadir Nueva Tarea"
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
        instance.domicilio = self.usuario.domicilio
        # Pasa los minutos a horas
        instance.duracion = instance.duracion * 60
        instance.save()
        return HttpResponseRedirect(reverse_lazy('tareas:crear_tarea'))


class AsignarTarea(CreateView):
    model = AsignarTarea_model
    form_class = AsignarTareaForm
    template_name = 'tareas/tarea_form.html'
    success_url = reverse_lazy('tareas:asignar_tarea')

    def get_context_data(self, **kwargs):
        context = super(AsignarTarea, self).get_context_data(**kwargs)
        context['name'] = "Asignar Tarea"
        self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
        # Filtra las posibles asignaciones que pueda realizar el admin según su domicilio
        context['form'].fields['tarea'].queryset = Tarea.objects.filter(domicilio=self.usuario.domicilio,
                                                                        asignada=False)
        context['form'].fields['usuario'].queryset = Usuario.objects.filter(domicilio=self.usuario.domicilio)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        # Busca la tarea a asignarse
        tarea = Tarea.objects.get(pk=instance.tarea.pk)
        # Indica que la terea ahora se encuentra asignada
        tarea.asignada = True
        # Guarda la tarea y la asignación a usuario
        tarea.save()
        instance.save()

        # Notifica mediante mail al usuario
        datos = Usuario.objects.get(pk=instance.usuario.pk)
        mensaje = "Hola " + datos.username + ", se te ha asignado la siguiente tarea: " + tarea.nombre + ", en " + str(tarea.dependencia) + ".\nComentarios: " + tarea.comentarios + ".\nPorfavor revisa la app.\n\nOrganizador =D"
        send_mail('Nueva asignación de tarea', mensaje, 'organizador.is2020@gmail.com', [datos.email], fail_silently=False)

        return HttpResponseRedirect(reverse_lazy('tareas:asignar_tarea'))


# vista para modificar las propiedades de una tarea, no modifica la asignacion de esta tarea.
class ModificarTarea(UpdateView):
    model = Tarea
    form_class = TareaForm
    template_name = 'tareas/modificar_tarea.html'
    success_url = reverse_lazy('tareas:listar_tareas_asignadas')

    def get_context_data(self, **kwargs):
        context = super(ModificarTarea, self).get_context_data(**kwargs)
        context['name'] = "Modificar Tarea"
        return context

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Tarea, id=id_)


class EliminarTarea(DeleteView):
    model = Tarea
    template_name = 'tareas/modificar_tarea.html'
    success_url = reverse_lazy('tareas:listar_tareas_asignadas')

    def get_context_data(self, **kwargs):
        context = super(EliminarTarea, self).get_context_data(**kwargs)
        context['name'] = "Eliminar Tarea"
        return context

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Tarea, id=id_)


class ListarTarea(ListView):
    model = Tarea
    template_name = 'tareas/listar_tareas.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListarTarea, self).get_context_data(**kwargs)

        # Toma la id de usuario almacenada
        pk_usuario = self.request.session.get('pk_usuario', '')
        # Intancia el objeto usuario
        usuario = Usuario.objects.get(pk=pk_usuario)
        usuarios = Usuario.objects.filter(domicilio=usuario.domicilio)

        Tareas_completadas = Tarea.objects.filter(domicilio=usuario.domicilio, completada=True)
        Tareas_no_completadas = Tarea.objects.filter(domicilio=usuario.domicilio, completada=False)

        context['asignaciones_completadas'] = AsignarTarea_model.objects.filter(usuario__in=usuarios, usuario=usuario, tarea__in=Tareas_completadas)
        context['asignaciones_no_completadas'] = AsignarTarea_model.objects.filter(usuario__in=usuarios, usuario=usuario, tarea__in=Tareas_no_completadas)

        return context

    def post(self, request, *args, **kwargs):
        # Notifica su tarea asignada como completada
        pk_asignada = request.POST.get('id_asignada')
        tipo = request.POST.get('tipo')
        if tipo == 'notifica_lograda':
            asignada_tarea = AsignarTarea_model.objects.get(pk=pk_asignada)
            asignada_tarea.notifica_completada = True
            asignada_tarea.save()
        elif tipo == 'notifica_objetar':
            asignada_tarea = AsignarTarea_model.objects.get(pk=pk_asignada)
            asignada_tarea.notifica_objetar = True
            asignada_tarea.justificacion = request.POST.get('justificacion')
            asignada_tarea.save()
        return HttpResponseRedirect(reverse_lazy('tareas:listar_tareas'))

    def get_queryset(self):
        # Toma la id de usuario almacenada
        pk_usuario = self.request.session.get('pk_usuario', '')
        # Intancia el objeto usuario
        usuario = Usuario.objects.get(pk=pk_usuario)
        usuarios = Usuario.objects.filter(domicilio=usuario.domicilio)
        # Retorna las tareas filtradas según domicilio, indicando las correspondiente al usuario en session
        tareas_no_completadas = Tarea.objects.filter(domicilio=usuario.domicilio, completada=False)
        return AsignarTarea_model.objects.filter(usuario__in=usuarios, usuario=usuario, tarea__in=tareas_no_completadas)


class ListarTareaAsignada(ListView):
    model = Tarea
    template_name = 'tareas/listar_tareas_asignadas.html'

    def get_queryset(self):
        # Toma la id de usuario almacenada
        pk_usuario = self.request.session.get('pk_usuario', '')
        # Intancia el objeto usuario
        usuario = Usuario.objects.get(pk=pk_usuario)
        usuarios = Usuario.objects.filter(domicilio=usuario.domicilio)
        # Retorna las tareas asignadas filtradas según domicilio
        return AsignarTarea_model.objects.filter(usuario__in=usuarios,notifica_completada=False)


class DistribuirTarea(TemplateView):
    template_name = 'tareas/tarea_distribuir.html'

    def get_context_data(self, **kwargs):
        context = super(DistribuirTarea, self).get_context_data(**kwargs)
        pk_usuario = self.request.session.get('pk_usuario', '')
        usuario = Usuario.objects.get(pk=pk_usuario)

        pertenece_dependencia = PerteneceDependencia.objects.filter(domicilio=usuario.domicilio, asignada=True)
        context['pertenece_dependencia'] = pertenece_dependencia

        usuarios = Usuario.objects.filter(domicilio=usuario.domicilio)
        context['usuarios'] = usuarios
        return context

    # Spaghetti post u.u
    def post(self, request, *args, **kwargs):
        identificador = request.POST.get('identificador')
        pk_usuario = self.request.session.get('pk_usuario', '')
        admin = Usuario.objects.get(pk=pk_usuario)
        usuarios = Usuario.objects.filter(domicilio=admin.domicilio)
        pd = PerteneceDependencia.objects.filter(domicilio=admin.domicilio)

        if identificador == 'cocinar':
            usuario = request.POST.get('usuario')
            hora = request.POST.get('hora')
            duracion = request.POST.get('duracion')
            radio_value = request.POST.get('radio_value')
            # Si no tiene una dependencia cocina se crea una y se asigna inmediatamente al domicilio actual
            try:
                pd.get(dependencia__nombre='Cocina')
            except:
                cocina = Dependencia('Cocina')
                cocina.save()
                PerteneceDependencia.objects.create(dependencia=cocina, domicilio=admin.domicilio, asignada=True)
                pd = PerteneceDependencia.objects.filter(domicilio=admin.domicilio)
            # hora como datetime
            start = hora_to_datetime(hora)
            # duracion como timedelta
            duracion = duracion_to_timedelta(duracion)
            end = start + duracion
            # Lista los usuario para ser rotativo
            rotar = False
            lista_usuarios = []
            if usuario == 'Todos de forma rotativa':
                rotar = True
                lista_usuarios = listar_usuarios(usuarios)
            # Crea las tareas, las asigna y calendariza por la semana
            for i in range(7):
                tarea = Tarea(nombre='Cocinar ' + str(radio_value),
                              domicilio=admin.domicilio,
                              complejidad=2,
                              duracion=duracion,
                              dependencia=pd.get(dependencia__nombre='Cocina').dependencia,
                              comentarios='Este día debes preparar ' + str(radio_value),
                              asignada=True)
                tarea.save()
                # Cambia el usuario si es rotativo
                if rotar:
                    usuario = lista_usuarios[i % len(lista_usuarios)]

                asignar_tarea = AsignarTarea_model(tarea=tarea,
                                                   usuario=Usuario.objects.get(domicilio=admin.domicilio,
                                                                               username=usuario),
                                                   calendarizar=True)
                asignar_tarea.save()
                event = Event(
                    title='Cocinar ' + str(radio_value),
                    asignar_tarea=asignar_tarea,
                    start=start + timedelta(days=i),
                    end=end + timedelta(days=i),
                    description='Este día debes preparar ' + str(radio_value)
                )
                event.save()

        elif identificador == 'limpiar':
            usuario = request.POST.get('usuario')
            dependencia = request.POST.get('dependencia')
            hora = request.POST.get('hora')
            duracion = request.POST.get('duracion')
            radio_value = request.POST.get('radio_value')
            # Dependencia
            rotar_dependencia = False
            lista_dependencias = []
            if dependencia == 'Todas de forma rotativa':
                rotar_dependencia = True
                lista_dependencias = listar_dependencias(pd)
            # hora como datetime
            start = hora_to_datetime(hora)
            # duracion como timedelta
            duracion = duracion_to_timedelta(duracion)
            end = start + duracion
            # Lista los usuario para ser rotativo
            rotar_usuario = False
            lista_usuarios = []
            if usuario == 'Todos de forma rotativa':
                rotar_usuario = True
                lista_usuarios = listar_usuarios(usuarios)
            # Valor incremental en caso de ser cada dos dias
            inc = 1
            if radio_value == 'Cada dos dias':
                inc = 2
            # Creacion de objetos
            for i in range(0, 7, inc):
                if rotar_dependencia:
                    dependencia = lista_dependencias[i % len(lista_dependencias)]
                tarea = Tarea(nombre='Limpiar ' + str(dependencia),
                              domicilio=admin.domicilio,
                              complejidad=2,
                              duracion=duracion,
                              dependencia=pd.get(dependencia__nombre=dependencia).dependencia,
                              comentarios='Este día debes limpiar ' + str(dependencia),
                              asignada=True)
                tarea.save()
                # Cambia el usuario si es rotativo
                if rotar_usuario:
                    usuario = lista_usuarios[i % len(lista_usuarios)]
                asignar_tarea = AsignarTarea_model(tarea=tarea,
                                                   usuario=Usuario.objects.get(domicilio=admin.domicilio,
                                                                               username=usuario),
                                                   calendarizar=True)
                asignar_tarea.save()
                event = Event(
                    title='Limpiar ' + str(dependencia),
                    asignar_tarea=asignar_tarea,
                    start=start + timedelta(days=i),
                    end=end + timedelta(days=i),
                    description='Este día debes limpiar ' + str(dependencia)
                )
                event.save()

        elif identificador == 'cuentas':
            usuario = request.POST.get('usuario')
            radio_value = request.POST.get('radio_value')
            # Si no tiene una dependencia oficina o exterior se crea una y se asigna inmediatamente al domicilio actual
            dependencia = 'Oficina'
            try:
                pd.get(dependencia__nombre='Oficina')
            except Exception:
                oficina = Dependencia('Oficina')
                oficina.save()
                PerteneceDependencia.objects.create(dependencia=oficina, domicilio=admin.domicilio, asignada=True)
                pd = PerteneceDependencia.objects.filter(domicilio=admin.domicilio)
            # hora como datetime
            hora = '13:00'
            hour = int(hora[0] + hora[1])
            minute = int(hora[3] + hora[4])
            if radio_value == 'Pagar a fin de mes':
                start = datetime.now().replace(day=30, microsecond=0, hour=hour, minute=minute)
            elif radio_value == 'Pagar a la quincena':
                start = datetime.now().replace(day=15, microsecond=0, hour=hour, minute=minute)
            # duracion como timedelta
            duracion = '01:00'
            duracion = duracion_to_timedelta(duracion)
            end = start + duracion
            # Lista los usuario para ser rotativo
            rotar_usuario = False
            lista_usuarios = []
            if usuario == 'Todos de forma rotativa':
                rotar_usuario = True
                lista_usuarios = listar_usuarios(usuarios)
            # Creación de objetos
            for i in range(6):
                tarea = Tarea(nombre='Realizar pago de cuentas',
                              domicilio=admin.domicilio,
                              complejidad=2,
                              duracion=duracion,
                              dependencia=pd.get(dependencia__nombre=dependencia).dependencia,
                              comentarios='Este día debes pagar las cuentas',
                              asignada=True)
                tarea.save()

                # Cambia el usuario si es rotativo
                if rotar_usuario:
                    usuario = lista_usuarios[i % len(lista_usuarios)]

                asignar_tarea = AsignarTarea_model(tarea=tarea,
                                                   usuario=Usuario.objects.get(domicilio=admin.domicilio,
                                                                               username=usuario),
                                                   calendarizar=True)

                asignar_tarea.save()
                event = Event(
                    title='Pagar cuentas ' + str(dependencia),
                    asignar_tarea=asignar_tarea,
                    start=start + relativedelta(months=i),
                    end=end + relativedelta(months=i),
                    description='Este día debes pagar las cuentas'
                )
                event.save()
        return HttpResponseRedirect(reverse_lazy('tareas:distribuir_tarea'))


# Utils : funciones de utilidad


# Transforma un string hh:mm en datetime
def hora_to_datetime(hora):
    hour = int(hora[0] + hora[1])
    minute = int(hora[3] + hora[4])
    start = datetime.now().replace(microsecond=0, hour=hour, minute=minute)
    return start


# Transforma un string hh:mm en timedelta
def duracion_to_timedelta(duracion):
    hours = int(duracion[0] + duracion[1])
    minutes = int(duracion[3] + duracion[4])
    duracion = timedelta(hours=hours, minutes=minutes)
    return duracion


# Lista los usuarios de un queryset
def listar_usuarios(usuarios):
    lista_usuarios = []
    usuarios = list(usuarios)
    for usuario in usuarios:
        lista_usuarios.append(usuario.username)
    return lista_usuarios


# Lista las dependencias de un queryset
def listar_dependencias(pd):
    lista_dependencias = []
    pd_list = list(pd)
    for item in pd_list:
        lista_dependencias.append(item.dependencia.nombre)
    return lista_dependencias
