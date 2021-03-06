from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.hogar.forms import UsuarioForm, UsuarioAdminForm, DomicilioForm, CrearDependenciaForm, AsignarDependenciaForm
from apps.hogar.models import Usuario, Domicilio, Dependencia, PerteneceDependencia
from apps.tareas.models import AsignarTarea


# Vista para registrar usuario común
class RegisterUser(CreateView):
    model = Usuario
    template_name = 'hogar/añadir_usuario.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('hogar:añadir')

    # Despliega formulario por pantalla
    def get_context_data(self, **kwargs):
        context = super(RegisterUser, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        return context

    # Guarda nuevo usuario añadido a hogar
    def form_valid(self, form):
        instance = form.save(commit=False)
        self.usuario = Usuario.objects.get(pk=self.request.session.get('pk_usuario', ''))
        instance.domicilio = self.usuario.domicilio
        instance.es_administrador = 0
        instance.save()
        return HttpResponseRedirect(reverse_lazy('hogar:añadir'))


# Vista doble form para registrar domicilio y usuario administrador
class Register(CreateView):
    model = Domicilio
    template_name = 'hogar/register.html'
    form_class = UsuarioAdminForm
    second_form_class = DomicilioForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(self.request.GET)
        return context

    def post(self, request, *arg, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)
        if form.is_valid() and form2.is_valid():
            sol = form.save(commit=False)
            sol.domicilio = form2.save()
            sol.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, form2=form2))


def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # redirect()
            # Instancia de objeto usuario
            usuario = Usuario.objects.get(username=username)
            # Almacena la pk de usuario para utilizar a futuro
            request.session['pk_usuario'] = usuario.pk
            request.session['es_administrador'] = usuario.es_administrador
            # Redirige
            return HttpResponseRedirect(reverse('hogar:dashboard'))
        else:
            messages.info(request, 'Usuario o contraseña incorrectos')

    context = {}
    return render(request, 'hogar/login.html', context)


class Dashboard(ListView):
    model = AsignarTarea
    template_name = 'hogar/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        pk_usuario = self.request.session.get('pk_usuario', '')
        usuario = Usuario.objects.get(pk=pk_usuario)
        usuarios = Usuario.objects.filter(domicilio=usuario.domicilio)
        context['qs_notifica_completada'] = AsignarTarea.objects.filter(usuario__in=usuarios, notifica_completada=True)
        context['qs_notifica_objetar'] = AsignarTarea.objects.filter(usuario__in=usuarios, notifica_objetar=True)
        return context

    def get_queryset(self):
        return None

    def post(self, request, *args, **kwargs):
        # Notifica su tarea asignada como completada
        pk_asignada = request.POST.get('id_asignada')
        asignada_status = request.POST.get('asignada_status')
        asignada_tarea = AsignarTarea.objects.get(pk=pk_asignada)
        # obtiene el usuario
        pk_usuario = self.request.session.get('pk_usuario')
        usuario = Usuario.objects.get(pk=pk_usuario)

        tipo = request.POST.get('tipo')
        if tipo == 'notifica_completada':
            if asignada_status == "on":
                asignada_tarea.tarea.completada = True
                asignada_tarea.notifica_completada = False
                # Asigna el puntaje al usuario
                usuario.puntaje_obtenido += asignada_tarea.tarea.get_puntaje
            else:
                asignada_tarea.tarea.completada = False
                asignada_tarea.notifica_completada = False
            asignada_tarea.tarea.save()
            asignada_tarea.save()
        elif tipo == 'notifica_objetar':
            if asignada_status == 'on':
                # Eliminar la tarea
                asignada_tarea.notifica_objetar = False
                asignada_tarea.tarea.delete()
                asignada_tarea.delete()
                # asignada_tarea.delete()
            else:
                # Conservar la tarea
                asignada_tarea.notifica_objetar = False
                asignada_tarea.save()

        usuario.save()
        return HttpResponseRedirect(reverse_lazy('hogar:dashboard'))


class Usuariolist(ListView):
    model = Usuario
    template_name = 'hogar/list_usuarios.html'

    def get_queryset(self):
        # Toma la id de usuario almacenada
        pk_usuario = self.request.session.get('pk_usuario', '')
        # Intancia el objeto usuario
        usuario = Usuario.objects.get(pk=pk_usuario)
        if usuario:
            # Retorna los usuarios filtrados según domicilio
            return Usuario.objects.filter(domicilio=usuario.domicilio)


# view para modificar datos de un determinado usuario
class UsuarioModificar(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'hogar/modificar_usuario.html'
    success_url = reverse_lazy('hogar:list_usuarios')

    def get_context_data(self, **kwargs):
        context = super(UsuarioModificar, self).get_context_data(**kwargs)
        context['name'] = "Modificar Usuario"
        return context

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def get_object(self):
        id_ = self.kwargs.get("pk")
        return get_object_or_404(Usuario, id=id_)


# View para modificar domicilio
class DomicilioModificar(CreateView):
    model = Domicilio
    form_class = DomicilioForm
    template_name = 'hogar/domicilio_modificar.html'
    success_url = reverse_lazy('hogar:domicilio_modificar')

    def get_context_data(self, **kwargs):
        context = super(DomicilioModificar, self).get_context_data(**kwargs)
        self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
        context['domicilio_actual'] = self.usuario.domicilio
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
        self.usuario.domicilio.calle = instance.calle
        self.usuario.domicilio.numero = instance.numero
        self.usuario.domicilio.comuna = instance.comuna
        self.usuario.domicilio.ciudad = instance.ciudad
        self.usuario.domicilio.save()
        return HttpResponseRedirect(self.success_url)


# View para crear y asignar dependencias, las dos en una
class DomicilioDependencias(CreateView):
    model = Dependencia
    template_name = 'hogar/domicilio_dependencias.html'
    form_class = CrearDependenciaForm
    second_form_class = AsignarDependenciaForm
    success_url = reverse_lazy('hogar:domicilio_dependencias')

    def get_context_data(self, **kwargs):
        context = super(DomicilioDependencias, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(self.request.GET)

        self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
        context['dependencias_disponibles'] = PerteneceDependencia.objects.filter(domicilio=self.usuario.domicilio,
                                                                                  asignada=False)
        context['dependencias_asignadas'] = PerteneceDependencia.objects.filter(domicilio=self.usuario.domicilio,
                                                                                asignada=True)
        context['form2'].fields['dependencia'].queryset = PerteneceDependencia.objects.filter(
            domicilio=self.usuario.domicilio, asignada=False)
        return context

    def post(self, request, *arg, **kwargs):
        self.object = self.get_object
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
            pertence_instance = PerteneceDependencia(domicilio=self.usuario.domicilio, dependencia=instance,
                                                     asignada=False)
            instance.save()
            pertence_instance.save()
            return HttpResponseRedirect(self.get_success_url())
        elif form2.is_valid():
            instance = form2.save(commit=False)
            self.usuario = Usuario.objects.get(pk=self.request.session['pk_usuario'])
            self.pertenece_instance = PerteneceDependencia.objects.get(dependencia_id=instance.dependencia.pk)
            self.pertenece_instance.asignada = True
            self.pertenece_instance.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form, form2=form2))
